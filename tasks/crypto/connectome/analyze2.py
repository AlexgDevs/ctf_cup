import gzip
import struct
import collections
import random

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
print("nodes", len(nodes))

data = open(ROOT + r"\message.bin", "rb").read()
words = list(struct.unpack("<%dI" % (len(data) // 4), data))

orders = {
    "sorted_id": nodes,
    "deg_desc": sorted(nodes, key=lambda n: -len(adj[n])),
    "deg_asc": sorted(nodes, key=lambda n: len(adj[n])),
}
dens = len(edges) / (len(nodes) * (len(nodes) - 1) / 2)
print("density", round(dens, 4))

for name, order in orders.items():
    m = [order[w] for w in words]
    hits = sum(1 for i in range(len(m) - 1) if m[i + 1] in adj[m[i]])
    print(f"{name}: consecutive edges {hits}/{len(m)-1}")

# Random baseline for consecutive edge hits under sorted order
rnd = random.Random(0)
base = []
for _ in range(200):
    perm = list(range(len(nodes)))
    rnd.shuffle(perm)
    m = [nodes[perm[w]] for w in words]
    base.append(sum(1 for i in range(len(m) - 1) if m[i + 1] in adj[m[i]]))
print("random baseline mean/max:", sum(base) / len(base), max(base))

# Check if each word w is the k-th neighbor rank of previous word
order = nodes
ranks = []
for i in range(len(words) - 1):
    a = order[words[i]]
    b = order[words[i + 1]]
    nb = sorted(adj[a])
    ranks.append(nb.index(b) if b in adj[a] else None)
print("neighbor ranks of consecutive pairs (sorted order):", ranks[:20])

# Are words the same across message as shared pattern? count repeats
print("distinct words:", len(set(words)), "of", len(words))
print("first 10 mapped node ids:", [order[w] for w in words[:10]])
