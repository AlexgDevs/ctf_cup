"""Шаблон разведки. Скопировать в tasks/<cat>/<task>/recon.py, заполнить TARGET и точки проверки."""

import sys
import requests

TARGET = "http://HOST:PORT"  # <-- выданный scope, ничего за его пределами

PATHS = [
    "/",
    "/robots.txt",
    "/sitemap.xml",
    "/favicon.ico",
    "/api",
    "/api/",
    "/admin",
    "/admin/",
    "/debug",
    "/health",
    "/.git/HEAD",
    "/.env",
    "/login",
    "/register",
]

COMMON_CREDS = [
    ("admin", "admin"),
    ("admin", "password"),
    ("admin", "123456"),
    ("admin", "admin123"),
]

TIMEOUT = 10


def req(method="GET", path="/", **kwargs):
    url = TARGET.rstrip("/") + path
    try:
        r = requests.request(method, url, timeout=TIMEOUT, allow_redirects=False, **kwargs)
        body = r.text[:500]
        print(f"[{r.status_code}] {method} {path}"
              + (f" -> {r.headers.get('Location')}" if r.headers.get("Location") else ""))
        if r.cookies:
            print(f"       cookies: {dict(r.cookies)}")
        if body and r.status_code not in (404,):
            print(f"       body[:500]: {body!r}")
        return r
    except requests.RequestException as e:
        print(f"[ERR] {method} {path}: {e}")
        return None


def main():
    print(f"=== recon {TARGET} ===")
    print("--- headers on / ---")
    r = req("GET", "/")
    if r is not None:
        for k, v in r.headers.items():
            print(f"       {k}: {v}")

    print("--- paths ---")
    for p in PATHS:
        req("GET", p)

    print("--- done: смотри вывод, гипотезы -> notes.md ---")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        TARGET = sys.argv[1]
    main()
