import json, sys
from wsclient import WS
CYC = [(0, 1), (1, 1), (1, 0), (2, 0), (2, -1), (3, -1), (4, -1), (4, -2), (4, -3), (4, -4), (3, -4), (2, -4), (1, -4), (0, -4), (-1, -3), (0, -3), (1, -3), (2, -3), (3, -3), (3, -2), (2, -2), (1, -2), (1, -1), (0, 0), (0, -1), (0, -2), (-1, -2), (-2, -2), (-3, -1), (-4, 0), (-4, 1), (-3, 0), (-2, -1), (-1, -1), (-2, 0), (-1, 0), (-1, 1), (-2, 1), (-3, 1), (-4, 2), (-3, 2), (-4, 3), (-4, 4), (-3, 4), (-3, 3), (-2, 2), (-1, 2), (-2, 3), (-2, 4), (-1, 4), (0, 4), (1, 3), (2, 2), (3, 1), (4, 0), (3, 0), (2, 1), (1, 2), (0, 3), (-1, 3), (0, 2)]
N = len(CYC)
DIRS = [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
IDX = {c: i for i, c in enumerate(CYC)}

def next_dir(head):
    i = IDX[head]
    nxt = CYC[(i + 1) % N]
    d = (nxt[0]-head[0], nxt[1]-head[1])
    return DIRS.index(d)

def play(ws, max_steps=6000):
    ws.send_text(json.dumps({"type": "reset"}))
    st = json.loads(ws.recv_text())
    steps = 0
    while steps < max_steps:
        head = (st["snake"][0]["q"], st["snake"][0]["r"])
        d = next_dir(head)
        ws.send_text(json.dumps({"type": "move", "dir": d}))
        st = json.loads(ws.recv_text())
        steps += 1
        if st.get("length", 0) % 10 == 0 and st.get("length"):
            pass
        if not st["alive"] or st["won"]:
            break
    return st, steps

if __name__ == "__main__":
    ws = WS("ws://8rdso9rdbof14wv0.instances.ctfcup.online/ws", timeout=15)
    st, steps = play(ws)
    print("steps", steps, "len", st["length"], "alive", st["alive"], "won", st["won"])
    print("message:", st.get("message"))
    ws.close()
