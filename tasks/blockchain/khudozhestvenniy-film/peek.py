import json

P = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\luckyspire.state.json"
with open(P, "r", encoding="utf-8") as f:
    st = json.load(f)

print("best_block_number:", st["best_block_number"])
for k in ("blocks", "transactions", "historical_states"):
    v = st[k]
    print("==", k, type(v).__name__, len(v))
    if isinstance(v, list) and v:
        print(json.dumps(v[0], ensure_ascii=False)[:1500])
    elif isinstance(v, dict):
        keys = list(v.keys())
        print("keys sample:", keys[:5])
        print(json.dumps(v[keys[0]], ensure_ascii=False)[:1500])
