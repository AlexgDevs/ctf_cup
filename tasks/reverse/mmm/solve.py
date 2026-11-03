"""mmm solver.

check(): len==40; t = M*v (40x40 uint64 matrix in .rodata at 0x3220), accepted iff t is
proportional to v (pairwise t_j*v_i == t_i*v_j) and t != 0. The matrix has eigenvalue
1337 with a 1-dim rational eigenvector, which is exactly the printable flag.
hash_check(): sha256(input) must equal the 32-byte constant at .rodata 0x6420.
"""
import hashlib
from sympy import Matrix, Rational, ilcm, gcd
from elftools.elf.elffile import ELFFile

with open("mmm", "rb") as f:
    e = ELFFile(f)
    ro = e.get_section_by_name(".rodata")
    rd = ro.data()
    base = ro["sh_addr"]

    def u64(va):
        o = va - base
        return int.from_bytes(rd[o:o + 8], "little")

    M_u = [[u64(0x3220 + (r * 40 + c) * 8) for c in range(40)] for r in range(40)]
    target = rd[0x6420 - base:0x6420 - base + 32]

M = Matrix([[x - (1 << 64) if x >= (1 << 63) else x for x in row] for row in M_u])
ns = (M - 1337 * Matrix.eye(40)).nullspace()
assert len(ns) == 1
vec = ns[0]
den = 1
for x in vec:
    den = ilcm(den, Rational(x).q)
ints = [int(x * den) for x in vec]
g = 0
for x in ints:
    g = gcd(g, x)
ints = [int(x // g) for x in ints]
flag = bytes(ints)

assert hashlib.sha256(flag).digest() == target
print(flag.decode())
