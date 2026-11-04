#!/usr/bin/env python3
"""
Targeted il2cpp metadata dumper — busca clases específicas, escribe directo a disco.
Soporta global-metadata.dat v24-v31 (Unity 2018-2022+).
"""
import sys, struct, mmap

def u32(d, o): return struct.unpack_from('<I', d, o)[0]
def i32(d, o): return struct.unpack_from('<i', d, o)[0]
def u16(d, o): return struct.unpack_from('<H', d, o)[0]

def cstr(d, base, idx):
    o = base + idx
    if o >= len(d): return ""
    end = d.index(b'\x00', o)
    return d[o:end].decode('utf-8', errors='replace')

TARGETS = {
    "FightingFighter", "FightingFighterManager", "FighterManager",
    "BaseCameraController", "CameraController", "GameCamera",
    "PlayerManager", "PlayerController", "BattlePlayer",
    "RoleProperty", "RoleStatus", "PlayerInfo",
    "FightingCamera", "MainCameraCtrl",
}

def main():
    if len(sys.argv) < 3:
        print("uso: python3 il2cpp_dump.py global-metadata.dat dump.cs")
        sys.exit(1)

    with open(sys.argv[1], 'rb') as f:
        meta = f.read()

    magic   = u32(meta, 0)
    version = i32(meta, 4)
    if magic != 0xFAB11BAF:
        print(f"Magic incorrecto: {hex(magic)}")
        sys.exit(1)
    print(f"version: {version}")

    # Header offsets por versión
    if version >= 29:
        str_off     = u32(meta, 0x18)
        td_off      = u32(meta, 0xA0); td_sz  = u32(meta, 0xA4)
        fld_off     = u32(meta, 0x60); fld_sz = u32(meta, 0x64)
        td_stride   = 0x94
    elif version >= 27:
        str_off     = u32(meta, 0x0C)
        td_off      = u32(meta, 0x40); td_sz  = u32(meta, 0x44)
        fld_off     = u32(meta, 0x48); fld_sz = u32(meta, 0x4C)
        td_stride   = 0x68
    else:
        str_off     = u32(meta, 0x0C)
        td_off      = u32(meta, 0x38); td_sz  = u32(meta, 0x3C)
        fld_off     = u32(meta, 0x40); fld_sz = u32(meta, 0x44)
        td_stride   = 0x5C

    fd_stride   = 0x0C
    td_count    = td_sz  // td_stride
    fd_count    = fld_sz // fd_stride
    print(f"TypeDefs: {td_count}  Fields: {fd_count}")

    # offsets de field_count y fieldStart dentro de Il2CppTypeDefinition
    if version >= 29:
        off_fname   = 0x00; off_fstart = 0x20
        off_fcount  = 0x44  # uint16 field_count
    elif version >= 27:
        off_fname   = 0x00; off_fstart = 0x24
        off_fcount  = 0x64  # uint16 field_count (en los 2 bytes bajos de un u32)
    else:
        off_fname   = 0x00; off_fstart = 0x20
        off_fcount  = 0x58

    found = 0
    with open(sys.argv[2], 'w', encoding='utf-8') as out:
        for ti in range(td_count):
            base  = td_off + ti * td_stride
            nidx  = i32(meta, base + 0x00)
            nsidx = i32(meta, base + 0x04)

            name = cstr(meta, str_off, nidx)
            if not any(t in name for t in TARGETS):
                continue

            ns          = cstr(meta, str_off, nsidx)
            field_start = i32(meta, base + off_fstart)
            field_count = u16(meta, base + off_fcount)

            out.write(f"\n// Namespace: {ns}\n")
            out.write(f"class {name}  // TypeIndex: {ti}\n{{\n")
            out.write("    // Fields:\n")

            for fi in range(field_count):
                fidx = field_start + fi
                if fidx < 0 or fidx >= fd_count: continue
                fb      = fld_off + fidx * fd_stride
                fnidx   = i32(meta, fb + 0x00)
                foffset = i32(meta, fb + 0x08)
                fname   = cstr(meta, str_off, fnidx)
                out.write(f"    // 0x{foffset:X}: {fname}\n")

            out.write("}\n")
            found += 1
            print(f"  → {name}")

    print(f"\ndump guardado en {sys.argv[2]}  ({found} clases)")

if __name__ == '__main__':
    main()
