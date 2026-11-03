import json
from sympy import Matrix, Rational, ilcm, gcd

M_u = json.load(open("M.json"))
M_s = [[x - (1 << 64) if x >= (1 << 63) else x for x in row] for row in M_u]
M = Matrix(M_s)
N = M - 1337 * Matrix.eye(40)
ns = N.nullspace()
print("nullspace dim for 1337:", len(ns))
for vec in ns:
    den = 1
    for x in vec:
        den = ilcm(den, Rational(x).q)
    ints = [int(x * den) for x in vec]
    g = 0
    for x in ints:
        g = gcd(g, x)
    ints = [x // g for x in ints] if g else ints
    print("int vector:", ints)
    print("as bytes:", bytes([x & 0xff for x in ints]))
    print("all in 0..255:", all(0 <= x <= 255 for x in ints))
    print("min,max:", min(ints), max(ints))
    json.dump(ints, open("v1337.json", "w"))
