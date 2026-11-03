import sys, random
sys.setrecursionlimit(10000)
DIRS = [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
R = 4
cells = [(q,r) for q in range(-R,R+1) for r in range(-R,R+1) if abs(q+r)<=R]
S = set(cells)
def nb(c): return [(c[0]+a,c[1]+b) for a,b in DIRS if (c[0]+a,c[1]+b) in S]
def find_cycle(start, limit=2_000_000):
    path=[start]; used={start}; cnt=[0]
    def dfs():
        cnt[0]+=1
        if cnt[0]>limit: return False
        if len(path)==len(cells):
            return start in nb(path[-1])
        last=path[-1]
        cand=[n for n in nb(last) if n not in used]
        # Warnsdorff: fewest free onward neighbours first
        cand.sort(key=lambda n: sum(1 for m in nb(n) if m not in used))
        for n in cand:
            path.append(n); used.add(n)
            if dfs(): return True
            path.pop(); used.discard(n)
        return False
    ok = dfs()
    return list(path) if ok else None
cyc = None
for s in [(0,0),(1,0),(0,1),(-1,0)]:
    cyc = find_cycle(s)
    if cyc: break
print("cycle found:", bool(cyc), "len", len(cyc) if cyc else 0)
if cyc:
    assert len(set(cyc))==61 and all(cyc[(i+1)%61] in nb(cyc[i]) for i in range(61))
    print("CYCLE=", cyc)
