import json, hashlib, struct
from elftools.elf.elffile import ELFFile

M_u = json.load(open("M.json"))
cand = b"ctfcup{99aeaf6c1fb1d156e4194be638825e6f}"
assert len(cand) == 40
v = list(cand)

# check(): t = M*v mod 2^64, need t_j*v_i == t_i*v_j (mod 2^64) for all i<j, and some t != 0
t = [sum(M_u[r][c] * v[c] for c in range(40)) % (1 << 64) for r in range(40)]
ok_prop = all((t[j] * v[i] - t[i] * v[j]) % (1 << 64) == 0
              for i in range(40) for j in range(i + 1, 40))
print("proportional (mod 2^64):", ok_prop, " any t!=0:", any(t))
print("t == 1337*v:", all(t[i] == (1337 * v[i]) % (1 << 64) for i in range(40)))

digest = hashlib.sha256(cand).digest()
print("sha256:", digest.hex())
with open("mmm", "rb") as f:
    e = ELFFile(f)
    ro = e.get_section_by_name(".rodata")
    rd = ro.data(); base = ro["sh_addr"]
    for va in range(0x3000, 0x6448 - 32):
        if rd[va - base: va - base + 32] == digest:
            print("digest found in .rodata at", hex(va))
            break
    else:
        print("digest NOT found verbatim in .rodata")
