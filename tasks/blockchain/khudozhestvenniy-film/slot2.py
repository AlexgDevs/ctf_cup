import json

P = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\luckyspire.state.json"
D = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\storage_diffs.json"
CASINO = "0xe7f1725e7734ce288f8367e1bb143e90bb3f0512"
SLOT2 = "0x" + "0" * 63 + "2"

st = json.load(open(P, "r", encoding="utf-8"))
events = json.load(open(D, "r", encoding="utf-8"))

# state index i corresponds to block number i+1 (historical_states[0] follows block 0 genesis tx)
slot2 = [e for e in events if e["addr"] == CASINO and int(e["slot"], 16) == 2]
print("slot 0x2 writes:", len(slot2))
for e in slot2[:12]:
    print("  block_idx", e["block"], e["old"][-8:], "->", e["new"][-8:])

blocks_wanted = sorted(set(e["block"] for e in slot2))[:3]
print("first blocks with slot2 write:", blocks_wanted)

for t in st["transactions"]:
    bn = int(t["block_number"], 16) if isinstance(t["block_number"], str) else int(t["block_number"])
    if bn not in (1, 2, 3, 4, 5, 6) and bn not in [b + 1 for b in blocks_wanted] and bn not in blocks_wanted:
        continue
    info = t["info"]
    tr0 = info["traces"][0]["trace"] if info["traces"] else {}
    print("tx block", bn, "from", info["from"][-6:], "to", (info.get("to") or "CREATE")[-6:],
          "sel", (tr0.get("data") or "")[:10], "traces", len(info["traces"]),
          "kinds", sorted(set(n["trace"]["kind"] for n in info["traces"])))
