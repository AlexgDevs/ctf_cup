import json
import numpy as np

M_u = json.load(open("M.json"))
M_s = [[x - (1 << 64) if x >= (1 << 63) else x for x in row] for row in M_u]
A = np.array(M_s, dtype=object)
print("max |entry|:", max(abs(x) for r in M_s for x in r))

Af = np.array([[float(x) for x in r] for r in M_s])
w, V = np.linalg.eig(Af)
print("eigenvalues (real parts, sorted):")
print(np.round(np.sort(w.real), 4))
print("imag parts nonzero count:", int(np.sum(np.abs(w.imag) > 1e-6)))
