import json
import collections

P = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\txs_compact.json"
txs = json.load(open(P, "r", encoding="utf-8"))

CASINO = "0xe7f1725e7734ce288f8367e1bb143e90bb3f0512"
IMPL = "0x3ad8d297ad557783ab111c87ec48368cb2a84f18"
TOKEN = "0x5fbdb2315678afecb367f032d93f642f64180aa3"

# group every tx by (sender, target, top-level selector, set of trace kinds)
groups = collections.Counter()
examples = {}
for t in txs:
    sel = t["traces"][0]["data"][:10] if t["traces"] else ""
    kinds = tuple(sorted(set(x["kind"] for x in t["traces"])))
    key = (t["from"], t["to"], sel, kinds)
    groups[key] += 1
    examples.setdefault(key, t["hash"])

print("distinct (from,to,selector,kinds):", len(groups))
for key, n in groups.most_common(60):
    frm, to, sel, kinds = key
    tag = "CASINO" if to == CASINO else "IMPL" if to == IMPL else "TOKEN" if to == TOKEN else (to or "CREATE")[-6:]
    print(n, frm[-6:], "->", tag, sel, kinds)
