import json
import collections

P = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\txs_compact.json"
txs = json.load(open(P, "r", encoding="utf-8"))

CASINO = "0xe7f1725e7734ce288f8367e1bb143e90bb3f0512"
IMPL = "0x3ad8d297ad557783ab111c87ec48368cb2a84f18"
TOKEN = "0x5fbdb2315678afecb367f032d93f642f64180aa3"

common = {CASINO, IMPL, TOKEN}
odd = []
for t in txs:
    if t["to"] in common:
        continue
    odd.append(t)

print("txs not to casino/impl/token:", len(odd))
for t in odd[:80]:
    kinds = [x["kind"] for x in t["traces"]]
    sel = [x["data"][:10] for x in t["traces"] if x["kind"] in ("CALL", "DELEGATECALL")][:3]
    print(t["index"], t["from"][-6:], "->", (t["to"] or "CREATE")[-6:], "traces", len(t["traces"]), collections.Counter(kinds).most_common(3), sel)
