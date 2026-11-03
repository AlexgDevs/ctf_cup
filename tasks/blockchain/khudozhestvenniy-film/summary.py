import json
import hashlib
import collections

P = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\luckyspire.state.json"
with open(P, "r", encoding="utf-8") as f:
    st = json.load(f)

print("top keys:", list(st.keys()))
blk = st["block"]
print("block:", blk)
acc = st["accounts"]
print("accounts:", len(acc))

contracts = {a: v for a, v in acc.items() if v.get("code") not in (None, "0x", "")}
print("contracts with code:", len(contracts))
storage_sizes = collections.Counter()
for a, v in acc.items():
    storage_sizes[len(v.get("storage", {}) or {})] += 1
print("storage size distribution (top):", storage_sizes.most_common(10))

# codehash groups (keccak not available by default; use sha3 via pysha3 unavailable -> record raw code len)
code_groups = collections.defaultdict(list)
for a, v in contracts.items():
    code_groups[v["code"]].append(a)
print("distinct code blobs:", len(code_groups))
for code, addrs in sorted(code_groups.items(), key=lambda x: -len(x[1]))[:10]:
    print("code len", (len(code) - 2) // 2, "count", len(addrs), "first addr", addrs[0])

CASINO = "0xe7f1725e7734ce288f8367e1bb143e90bb3f0512"
c = acc.get(CASINO)
print("casino present:", c is not None)
if c:
    print("casino nonce/balance:", c["nonce"], c["balance"], "code len", (len(c["code"]) - 2) // 2)
    print("casino storage entries:", len(c["storage"]))
    for k, v in list(c["storage"].items())[:40]:
        print("  ", k, v)
