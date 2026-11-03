import struct
from elftools.elf.elffile import ELFFile
with open("mmm","rb") as f:
    e = ELFFile(f)
    ro = e.get_section_by_name(".rodata")
    rd = ro.data(); base = ro["sh_addr"]
    def rd_at(va, n):
        o = va - base
        return rd[o:o+n]
    M = [[struct.unpack("<Q", rd_at(0x3220 + (r*40+c)*8, 8))[0] for c in range(40)] for r in range(40)]
    K = [struct.unpack("<I", rd_at(0x3100 + i*4, 4))[0] for i in range(64)]
    print("K[0..3]", [hex(x) for x in K[:4]], "K63", hex(K[63]))
    print("M row0 first 8:", [hex(x) for x in M[0][:8]])
    print("M row1 first 8:", [hex(x) for x in M[1][:8]])
    print("M diag first 8:", [hex(M[i][i]) for i in range(8)])
    nz = sum(1 for r in M for x in r if x)
    print("nonzero entries", nz, "of", 1600)
    import json
    json.dump(M, open("M.json","w"))
    json.dump(K, open("K.json","w"))
    # search for 32-byte digest-like constants near end of rodata (after matrix)
    print("bytes after matrix (0x6420..0x6448):", rd_at(0x6420, 0x28).hex())
