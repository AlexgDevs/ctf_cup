import json
from wsclient import WS
for trial in range(2):
    ws = WS("ws://8rdso9rdbof14wv0.instances.ctfcup.online/ws", timeout=10)
    print("connect", json.loads(ws.recv_text())["food"])
    for _ in range(2):
        ws.send_text(json.dumps({"type":"reset"}))
        st = json.loads(ws.recv_text())
        print("  reset food", st["food"], "snake", st["snake"])
    ws.close()
