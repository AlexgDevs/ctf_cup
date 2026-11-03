import json

P = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\luckyspire.state.json"
OUT = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\state_changes.json"

with open(P, "r", encoding="utf-8") as f:
    st = json.load(f)

hs = st["historical_states"]
print("historical states:", len(hs))
print("entry 0 accounts:", len(hs[0][1]["accounts"]))
print("entry 0 keys:", list(hs[0][1].keys()))

CASINO = "0xe7f1725e7734ce288f8367e1bb143e90bb3f0512"
IMPL = "0x3ad8d297ad557783ab111c87ec48368cb2a84f18"

prev_storage = {}
prev_codehash = {}
prev_balance = {}
changes = []
code_changes = []
bal_changes = []
for i, (bh, state) in enumerate(hs):
    accs = state["accounts"]
    cas = accs.get(CASINO)
    if cas and "storage" in cas and cas["storage"] is not None:
        cur = cas["storage"]
        if i == 0 or prev_storage:
            for k, v in cur.items():
                if prev_storage.get(k) != v:
                    changes.append({"block_index": i, "block_hash": bh, "slot": k,
                                    "old": prev_storage.get(k), "new": v})
        prev_storage = dict(cur)
    for a, acc in accs.items():
        ch = acc.get("code_hash")
        if ch is not None and prev_codehash.get(a) not in (None, ch):
            code_changes.append({"block_index": i, "address": a, "old": prev_codehash.get(a), "new": ch})
        if ch is not None:
            prev_codehash[a] = ch

print("casino storage slot changes:", len(changes))
for c in changes[:60]:
    print(c["block_index"], c["slot"][-8:], "old", (c["old"] or "")[-40:], "new", (c["new"] or "")[-40:])
print("code_hash changes:", len(code_changes))
for c in code_changes[:40]:
    print(c["block_index"], c["address"], c["old"][:14], "->", c["new"][:14])

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"storage": changes, "code": code_changes}, f)
print("saved")
