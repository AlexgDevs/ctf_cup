import json
from wsclient import WS
from bot import CYC, next_dir
ws = WS("ws://8rdso9rdbof14wv0.instances.ctfcup.online/ws", timeout=15)
st = json.loads(ws.recv_text())
print("initial", st["snake"], st["food"], st["alive"])
ws.send_text(json.dumps({"type":"reset"})); st = json.loads(ws.recv_text())
print("after reset", st["snake"], st["food"], st["alive"], st["length"])
for i in range(16):
    head = (st["snake"][0]["q"], st["snake"][0]["r"])
    d = next_dir(head)
    ws.send_text(json.dumps({"type":"move","dir":d})); st = json.loads(ws.recv_text())
    print(i, "head", head, "dir", d, "->", st["snake"], "food", st["food"], "len", st["length"], "alive", st["alive"], "won", st["won"])
    if not st["alive"]: break
ws.close()
