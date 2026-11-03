import json
from wsclient import WS
from bot import next_dir
ws = WS("ws://8rdso9rdbof14wv0.instances.ctfcup.online/ws", timeout=15)
st = json.loads(ws.recv_text())            # initial state (must consume)
ws.send_text(json.dumps({"type": "reset"}))
st = json.loads(ws.recv_text())            # reset response
steps = 0; last_len = 1
while steps < 6000:
    head = (st["snake"][0]["q"], st["snake"][0]["r"])
    ws.send_text(json.dumps({"type": "move", "dir": next_dir(head)}))
    st = json.loads(ws.recv_text())
    steps += 1
    if st["length"] != last_len:
        last_len = st["length"]
        print("steps", steps, "length", last_len, flush=True)
    if not st["alive"] or st["won"]:
        break
print("END steps", steps, "len", st["length"], "alive", st["alive"], "won", st["won"])
print("message:", st.get("message"))
ws.close()
