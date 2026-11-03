import json
from wsclient import WS
ws = WS("ws://8rdso9rdbof14wv0.instances.ctfcup.online/ws", timeout=10)
print(ws.recv_text()[:300])
for d in [3, 3, 3]:
    ws.send_text(json.dumps({"type":"move","dir":d}))
    st = json.loads(ws.recv_text())
    print("dir", d, {k:v for k,v in st.items() if k!="type"})
ws.close()
