import json
import collections

P = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\luckyspire.state.json"
OUT = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\txs_compact.json"

with open(P, "r", encoding="utf-8") as f:
    st = json.load(f)

txs = st["transactions"]
print("tx count:", len(txs))
print("info keys:", sorted(txs[0]["info"].keys()))
print("first tx keys:", sorted(txs[0].keys()))

kinds = collections.Counter()
succ = collections.Counter()
senders = collections.Counter()
targets = collections.Counter()

compact = []
for t in txs:
    info = t["info"]
    senders[info["from"]] += 1
    targets[info.get("to")] += 1
    traces = []
    for node in info.get("traces", []):
        tr = node["trace"]
        kinds[tr["kind"]] += 1
        succ[tr["success"]] += 1
        traces.append({"idx": node["idx"], "parent": node.get("parent"), "children": node.get("children"),
                       "depth": tr["depth"], "kind": tr["kind"], "caller": tr["caller"],
                       "address": tr["address"], "value": tr["value"], "success": tr["success"],
                       "data": tr["data"] if tr.get("data") else "",
                       "selfdestruct": tr.get("selfdestruct_address")})
    compact.append({
        "hash": info["transaction_hash"],
        "index": info["transaction_index"],
        "from": info["from"],
        "to": info.get("to"),
        "contract_address": info.get("contract_address"),
        "traces": traces,
        "receipt": t.get("receipt"),
    })

print("kinds:", kinds.most_common())
print("success:", succ.most_common())
print("distinct senders:", len(senders), senders.most_common(8))
print("distinct targets:", len(targets), targets.most_common(8))

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(compact, f)
print("saved", OUT)
