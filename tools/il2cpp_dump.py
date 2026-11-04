#!/usr/bin/env python3
"""
Targeted il2cpp metadata dumper — lee solo las secciones necesarias, no el archivo entero.
Soporta global-metadata.dat v24-v31.
"""
import sys, struct

def r32(f, off):
    f.seek(off); return struct.unpack('<i', f.read(4))[0]
def u32(f, off):
    f.seek(off); return struct.unpack('<I', f.read(4))[0]
def pu32(d, o): return struct.unpack_from('<I', d, o)[0]
def pi32(d, o): return struct.unpack_from('<i', d, o)[0]
def pu16(d, o): return struct.unpack_from('<H', d, o)[0]

def cstr(d, idx):
    if idx < 0 or idx >= len(d): return ""
    end = d.index(b'\x00', idx)
    return d[idx:end].decode('utf-8', errors='replace')

# Búsqueda amplia — ajustar si los nombres no matchean
TARGETS = {
    "Fighter", "Player", "Character", "Role", "Hero",
    "Camera", "BattleManager", "GameManager", "FightingManager",
    "EntityManager", "ActorManager", "CharacterManager",
    "HP", "Health", "Alive", "Dead",
}

def main():
    if len(sys.argv) < 3:
        print("uso: python3 il2cpp_dump.py global-metadata.dat dump.cs")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, 'rb') as f:
        magic   = u32(f, 0)
        version = r32(f, 4)

    if magic != 0xFAB11BAF:
        print(f"Magic incorrecto: {hex(magic)}")
        sys.exit(1)
    print(f"version: {version}")

    with open(path, 'rb') as f:
        if version >= 29:
            str_off  = u32(f, 0x18); str_sz  = u32(f, 0x1C)
            td_off   = u32(f, 0xA0); td_sz   = u32(f, 0xA4)
            fld_off  = u32(f, 0x60); fld_sz  = u32(f, 0x64)
            td_stride = 0x94
            off_fstart = 0x20; off_fcount = 0x44
        elif version >= 27:
            str_off  = u32(f, 0x0C); str_sz  = u32(f, 0x10)
            td_off   = u32(f, 0x40); td_sz   = u32(f, 0x44)
            fld_off  = u32(f, 0x48); fld_sz  = u32(f, 0x4C)
            td_stride = 0x68
            off_fstart = 0x24; off_fcount = 0x64
        else:
            str_off  = u32(f, 0x0C); str_sz  = u32(f, 0x10)
            td_off   = u32(f, 0x38); td_sz   = u32(f, 0x3C)
            fld_off  = u32(f, 0x40); fld_sz  = u32(f, 0x44)
            td_stride = 0x5C
            off_fstart = 0x20; off_fcount = 0x58

        # leer solo las 3 secciones necesarias
        print(f"Leyendo strings ({str_sz//1024}KB)...")
        f.seek(str_off); strings = f.read(str_sz)
        print(f"Leyendo TypeDefs ({td_sz//1024}KB)...")
        f.seek(td_off);  tdefs   = f.read(td_sz)
        print(f"Leyendo Fields ({fld_sz//1024}KB)...")
        f.seek(fld_off); fields  = f.read(fld_sz)

    td_count  = td_sz  // td_stride
    fd_count  = fld_sz // 0x0C
    print(f"TypeDefs: {td_count}  Fields: {fd_count}")

    found = 0
    with open(sys.argv[2], 'w', encoding='utf-8') as out:
        for ti in range(td_count):
            base = ti * td_stride
            nidx = pi32(tdefs, base + 0x00)
            nsidx= pi32(tdefs, base + 0x04)
            name = cstr(strings, nidx)
            if not any(t in name for t in TARGETS):
                continue

            ns          = cstr(strings, nsidx)
            field_start = pi32(tdefs, base + off_fstart)
            field_count = pu16(tdefs, base + off_fcount)

            out.write(f"\n// Namespace: {ns}\n")
            out.write(f"class {name}  // TypeIndex: {ti}\n{{\n")
            out.write("    // Fields:\n")
            for fi in range(field_count):
                fidx = field_start + fi
                if fidx < 0 or fidx >= fd_count: continue
                fb      = fidx * 0x0C
                fnidx   = pi32(fields, fb + 0x00)
                foffset = pi32(fields, fb + 0x08)
                fname   = cstr(strings, fnidx)
                out.write(f"    // 0x{foffset:X}: {fname}\n")
            out.write("}\n")
            found += 1
            print(f"  → {name}")

    print(f"dump guardado: {sys.argv[2]}  ({found} clases)")

if __name__ == '__main__':
    main()
