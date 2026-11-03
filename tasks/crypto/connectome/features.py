import gzip
import struct
import collections
import string

ROOT = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\crypto\connectome"

edges = []
with gzip.open(ROOT + r"\adjacency.csv.gz", "rt") as f:
    next(f)
    for line in f:
        a, b = line.strip().split(",")
        edges.append((int(a), int(b)))

adj = collections.defaultdict(set)
for a, b in edges:
    adj[a].add(b)
    adj[b].add(a)
nodes = sorted(adj)
data = open(ROOT + r"\message.bin", "rb").read()
words = list(struct.unpack("<%dI" % (len(data) // 4), data))
path = [nodes[w] for w in words]

PRINT = set(map(ord, string.printable))

def score(bs):
    if not bs:
        return 0, b""
    ok = sum(1 for b in bs if b in PRINT)
    return ok / len(bs), bytes(bs)

def tri(n):
    nb = adj[n]
    return sum(1 for x in nb for y in adj[x] if y in nb) // 2

feats = {
    "id_lo": lambda n: n & 0xff,
    "id_hi": lambda n: (n >> 8) & 0xff,
    "id_mod255": lambda n: n % 255,
    "deg": lambda n: len(adj[n]) & 0xff,
    "deg_lo": lambda n: len(adj[n]) & 0xff,
    "nbsum_lo": lambda n: sum(adj[n]) & 0xff,
    "tri_lo": lambda n: tri(n) & 0xff,
    "idx": lambda n: nodes.index(n) & 0xff,
    "idx_hi": lambda n: (nodes.index(n) >> 8) & 0xff,
}

results = []
for name, f in feats.items():
    bs = [f(n) for n in path]
    p, b = score(bs)
    results.append((p, name, b))

# pair features: rank of next node in sorted neighbors, xor of ids, common neighbors
def common(a, b):
    return len(adj[a] & adj[b])

pair_feats = {
    "xor_lo": lambda a, b: (a ^ b) & 0xff,
    "diff_lo": lambda a, b: (b - a) & 0xff,
    "common_lo": lambda a, b: common(a, b) & 0xff,
    "rank_lo": lambda a, b: (sorted(adj[a]).index(b)) & 0xff,
}
for name, f in pair_feats.items():
    bs = [f(path[i], path[i + 1]) for i in range(len(path) - 1)]
    p, b = score(bs)
    results.append((p, name, b))

results.sort(reverse=True)
for p, name, b in results:
    print(f"{p:.2f} {name:12s} {b[:80]!r}")
