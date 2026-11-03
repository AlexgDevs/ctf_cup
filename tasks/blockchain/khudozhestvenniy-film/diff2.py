import json
import collections

P = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\luckyspire.state.json"
OUT = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\storage_diffs.json"

st = json.load(open(P, "r", encoding="utf-8"))
hs = st["historical_states"]

prev = {}          # (addr, slot) -> value
events = []        # every slot write seen
per_addr = collections.Counter()
for i, (bh, state) in enumerate(hs):
    stor = state.get("storage", {}) or {}
    for addr, slots in stor.items():
        for slot, val in (slots or {}).items():
            key = (addr, slot)
            if key in prev and prev[key] != val:
                events.append({"block": i, "addr": addr, "slot": slot, "old": prev[key], "new": val})
                per_addr[addr] += 1
            prev[key] = val

print("storage writes that changed a value:", len(events))
print("per-address change counts:", per_addr.most_common(15))

# keep a compact copy
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(events, f)

CASINO = "0xe7f1725e7734ce288f8367e1bb143e90bb3f0512"
ce = [e for e in events if e["addr"] == CASINO]
print("casino writes:", len(ce))
for e in ce[:50]:
    print(e["block"], e["slot"][-6:], e["old"][-20:], "->", e["new"][-20:])
