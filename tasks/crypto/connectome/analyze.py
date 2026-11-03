import gzip
import struct
import collections

ROOT = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\crypto\connectome"

edges = []
with gzip.open(ROOT + r"\adjacency.csv.gz", "rt") as f:
    next(f)
    for line in f:
        a, b = line.strip().split(",")
        edges.append((int(a), int(b)))

nodes = set()
deg = collections.Counter()
adj = collections.defaultdict(set)
for a, b in edges:
    nodes.add(a)
    nodes.add(b)
    deg[a] += 1
    deg[b] += 1
    adj[a].add(b)
    adj[b].add(a)

print("edges:", len(edges), "nodes:", len(nodes), "max id:", max(nodes), "min id:", min(nodes))
print("degree histogram top:", collections.Counter(deg.values()).most_common(8))
print("distinct degrees:", len(set(deg.values())))

data = open(ROOT + r"\message.bin", "rb").read()
words = list(struct.unpack("<%dI" % (len(data) // 4), data))
print("words:", len(words))
print("words:", words)

in_nodes = sum(1 for w in words if w in nodes)
in_deg = sum(1 for w in words if w in deg)
print("words that are node ids:", in_nodes, "of", len(words))
print("values <= 255:", sum(1 for w in words if w <= 255))

# consecutive pairs that are edges
pairs = [(words[i], words[i + 1]) for i in range(len(words) - 1)]
e_hits = sum(1 for a, b in pairs if b in adj.get(a, ()))
print("consecutive pairs that are edges:", e_hits, "of", len(pairs))

# shortest path/deg-ordering checks: words as indexes into sorted node list
sorted_nodes = sorted(nodes)
idx_ok = [w for w in words if w < len(sorted_nodes)]
print("words usable as index into sorted nodes:", len(idx_ok))
