"""weird-rsa solver: RSA over GF(257)[x], factor N, decrypt c = m^e mod N."""

import ast
import re
import sys
from pathlib import Path

from sympy import Poly, GF, invert, gcd, lcm, integer_nthroot
from sympy import symbols

OUT = Path(__file__).parent / "weird-rsa" / "output.txt"
FLAG_PATH = Path(__file__).parent / "flag.txt"


def parse_output(path: Path):
    txt = path.read_text()
    d = {}
    for key in ("p", "e"):
        m = re.search(rf"^{key} = (\d+)$", txt, re.M)
        d[key] = int(m.group(1))
    for key in ("N", "c"):
        m = re.search(rf"^{key} = (\[[^\]]+\])$", txt, re.M)
        d[key] = ast.literal_eval(m.group(1))[::-1]  # sage .list() is low-degree first
    return d


def main():
    p, e, Nlist, clist = (lambda d: (d["p"], d["e"], d["N"], d["c"]))(parse_output(OUT))
    x = symbols("x")
    R = GF(p)

    def poly_powmod(base, exp, mod):
        result = Poly(1, x, domain=R)
        b = base.rem(mod)
        while exp:
            if exp & 1:
                result = (result * b).rem(mod)
            b = (b * b).rem(mod)
            exp >>= 1
        return result

    N = Poly(Nlist, x, domain=R)
    c = Poly(clist, x, domain=R)

    print("[*] factoring N over GF(%d), deg=%d ..." % (p, N.degree()))
    facs = N.factor_list()[1]
    print("[*] factors (deg, mult):", [(f.degree(), mult) for f, mult in facs])
    assert sum(f.degree() * mult for f, mult in facs) == N.degree()

    P = None
    Q = None
    for f, mult in facs:
        assert mult == 1
        if f.degree() == 58:
            P = f
        elif f.degree() == 59:
            Q = f
        else:
            raise SystemExit(f"unexpected factor degree {f.degree()}")
    assert P is not None and Q is not None

    phi_P = p ** 58 - 1
    phi_Q = p ** 59 - 1
    lam = lcm(phi_P, phi_Q)  # carmichael analogue
    d = int(invert(e, lam))
    print("[*] private exponent computed, d has", d.bit_length(), "bits")

    m = poly_powmod(c, d, N)
    coeffs = [int(c_) for c_ in m.all_coeffs()][::-1]  # constant term first
    flag = bytes(coeffs)
    print("[+] flag bytes:", flag)
    FLAG_PATH.write_text(flag.decode(errors="replace"), encoding="utf-8")
    print("[+] written to", FLAG_PATH)


if __name__ == "__main__":
    main()
