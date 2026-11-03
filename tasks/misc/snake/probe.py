import json
import sys
from wsclient import WS

URL = "ws://8rdso9rdbof14wv0.instances.ctfcup.online/ws"

ws = WS(URL, timeout=10)
first = ws.recv_text()
print("RAW FIRST:", first[:1500])
st = json.loads(first)
print("KEYS:", sorted(st.keys()))
print({k: v for k, v in st.items() if k != "snake"})
print("snake len:", len(st.get("snake", [])), "head:", st.get("snake", [None])[0])
ws.close()
