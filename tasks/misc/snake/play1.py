import json
from collections import deque
from wsclient import WS
DIRS = [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
def inside(q,r,R=4): return abs(q)<=R and abs(r)<=R and abs(q+r)<=R
def bfs(start, goal, blocked):
    prev = {start: None}; dq = deque([start])
    while dq:
        c = dq.popleft()
        if c == goal:
            path=[]; 
            while c != start: path.append(c); c = prev[c]
            return path[::-1]
        for dq_,dr in DIRS:
            n=(c[0]+dq_, c[1]+dr)
            if inside(*n) and n not in blocked and n not in prev:
                prev[n]=c; dq.append(n)
    return None
ws = WS("ws://8rdso9rdbof14wv0.instances.ctfcup.online/ws", timeout=10)
st = json.loads(ws.recv_text())
print("start food", st["food"])
for step in range(60):
    snake = [(s["q"],s["r"]) for s in st["snake"]]
    food = (st["food"]["q"], st["food"]["r"])
    path = bfs(snake[0], food, set(snake[:-1]))
    if not path:
        print("no path, stop"); break
    nxt = path[0]
    d = DIRS.index((nxt[0]-snake[0][0], nxt[1]-snake[0][1]))
    ws.send_text(json.dumps({"type":"move","dir":d}))
    st = json.loads(ws.recv_text())
    print(step, "dir", d, "head", st["snake"][0], "len", st["length"], "food", st["food"], "alive", st["alive"], "won", st["won"], "msg", st.get("message"))
    if not st["alive"] or st["won"]: break
    if st["length"] >= 3: break
ws.close()
