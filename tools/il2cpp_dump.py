#!/usr/bin/env python3
"""
Minimal il2cpp metadata dumper — solo genera dump.cs con clases/campos/offsets.
Funciona con global-metadata.dat version 24.0 - 29.x (Unity 2018-2022).
"""
import sys, struct, os

def u32(d, o): return struct.unpack_from('<I', d, o)[0]
def u64(d, o): return struct.unpack_from('<Q', d, o)[0]
def i32(d, o): return struct.unpack_from('<i', d, o)[0]
def cstr(d, o):
    end = d.index(b'\x00', o)
    return d[o:end].decode('utf-8', errors='replace')

def main():
    if len(sys.argv) < 3:
        print("uso: python3 il2cpp_dump.py global-metadata.dat output_dump.cs")
        sys.exit(1)

    meta_path = sys.argv[1]
    out_path  = sys.argv[2]

    with open(meta_path, 'rb') as f:
        meta = f.read()

    magic = u32(meta, 0)
    if magic != 0xFAB11BAF:
        print(f"Magic incorrecto: {hex(magic)} — ¿es el global-metadata.dat correcto?")
        sys.exit(1)

    version = i32(meta, 4)
    print(f"global-metadata.dat version: {version}")

    # Header offsets varían por versión — tabla para v24-v29
    # Formato: (stringOffset, stringSize, typeDefsOffset, typeDefsSize,
    #           fieldsOffset, fieldsSize, fieldDefaultsOffset, fieldDefaultsSize)
    # Offsets del header de global-metadata (siempre en bytes desde 0)
    def hdr(offset): return u32(meta, offset)

    string_off  = hdr(0x0C); string_size = hdr(0x10)
    # TypeDefs — offset varía por versión
    if version >= 27:
        typedef_off  = hdr(0x40); typedef_size = hdr(0x44)
        fields_off   = hdr(0x48); fields_size  = hdr(0x4C)
        methods_off  = hdr(0x58); methods_size = hdr(0x5C)
    elif version >= 24:
        typedef_off  = hdr(0x38); typedef_size = hdr(0x3C)
        fields_off   = hdr(0x40); fields_size  = hdr(0x44)
        methods_off  = hdr(0x50); methods_size = hdr(0x54)
    else:
        print(f"Versión {version} no soportada. Probá con v24-v29.")
        sys.exit(1)

    # Stride de Il2CppTypeDefinition también varía
    # v24: 0x5C, v27+: 0x68
    td_stride = 0x68 if version >= 27 else 0x5C
    # Il2CppFieldDefinition stride = 0xC (v24-v29)
    fd_stride = 0x0C

    td_count = typedef_size // td_stride
    fd_count = fields_size  // fd_stride

    print(f"TypeDefs: {td_count}  Fields: {fd_count}")

    def get_str(o):
        if o < 0 or string_off + o >= len(meta): return ""
        return cstr(meta, string_off + o)

    out_lines = []

    for ti in range(td_count):
        base = typedef_off + ti * td_stride
        name_idx    = i32(meta, base + 0x00)
        ns_idx      = i32(meta, base + 0x04)
        field_start = i32(meta, base + (0x24 if version >= 27 else 0x20))
        field_count = u32(meta, base + (0x64 if version >= 27 else 0x58)) & 0xFFFF

        name = get_str(name_idx)
        ns   = get_str(ns_idx)
        full = f"{ns}.{name}" if ns else name

        out_lines.append(f"\n// Namespace: {ns}")
        out_lines.append(f"class {name} // TypeDefIndex: {ti}")
        out_lines.append("{")
        out_lines.append(f"    // Fields:")

        for fi in range(field_count):
            fidx = field_start + fi
            if fidx < 0 or fidx >= fd_count: continue
            fb = fields_off + fidx * fd_stride
            fname_idx = i32(meta, fb + 0x00)
            # offset dentro del objeto en il2cpp: bytes 4-7 del field def
            foffset   = i32(meta, fb + 0x08)
            fname = get_str(fname_idx)
            out_lines.append(f"    // 0x{foffset:X}: {fname}")

        out_lines.append("}")

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out_lines))

    print(f"dump guardado en {out_path}  ({len(out_lines)} líneas)")

if __name__ == '__main__':
    main()
