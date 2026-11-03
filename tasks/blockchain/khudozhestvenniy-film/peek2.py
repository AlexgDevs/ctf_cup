import json
P = r"C:\Users\caloz\PycharmProjects\ctf_cup\tasks\blockchain\khudozhestvenniy-film\luckyspire.state.json"
st = json.load(open(P, "r", encoding="utf-8"))
hs = st["historical_states"]
s0 = hs[0][1]["storage"]
print("type", type(s0).__name__, "len", len(s0))
if isinstance(s0, dict):
    k = list(s0.keys())[:3]; print("keys sample", k)
    print("value sample", str(s0[k[0]])[:400])
s1 = hs[1][1]["storage"]; print("block1 len", len(s1))
