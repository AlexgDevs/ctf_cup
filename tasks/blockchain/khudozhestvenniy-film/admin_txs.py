import json
import collections

P = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\luckyspire.state.json"
D = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\storage_diffs.json"

CASINO = "0xe7f1725e7734ce288f8367e1bb143e90bb3f0512"
IMPL = "0x3ad8d297ad557783ab111c87ec48368cb2a84f18"
ADMIN = "0x70997970c51812dc3a010c7d01b50e0d17dc79c8"
COMMON_SEL = {"0x0695a252", "0x92090cff", "0x379607f5"}

st = json.load(open(P, "r", encoding="utf-8"))
events = json.load(open(D, "r", encoding="utf-8"))
by_block = collections.defaultdict(list)
for e in events:
    by_block[e["block"]].append(e)

rows = []
for t in st["transactions"]:
    info = t["info"]
    if info["from"] != ADMIN:
        continue
    tr0 = info["traces"][0]["trace"] if info["traces"] else {}
    sel = (tr0.get("data") or "")[:10]
    if info.get("to") == CASINO and sel in COMMON_SEL:
        continue
    rows.append((t["block_number"], info["transaction_hash"], info.get("to"), sel, info["traces"]))

print("admin non-common txs:", len(rows))
for blk, h, to, sel, traces in rows[:40]:
    print("block", blk, "to", (to or "CREATE")[-6:], "sel", sel, "hash", h[:14])
    for node in traces:
        x = node["trace"]
        print("    ", x["kind"], "caller", x["caller"][-6:], "addr", x["address"][-6:], "data", (x.get("data") or "")[:10], "value", x["value"])
    ev = [e for e in by_block.get(int(blk, 16) if isinstance(blk, str) else blk, []) if e["addr"] == CASINO]
    print("     casino writes this block:", len(ev))
    for e in ev[:12]:
        print("       slot", e["slot"][-14:], "old", e["old"][-16:], "new", e["new"][-16:])
