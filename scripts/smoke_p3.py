"""P3 integration smoke via gateway :8080. Requires `docker compose up -d`."""
import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8080"

PASS = 0
FAIL = 0


def check(name, fn):
    global PASS, FAIL
    try:
        detail = fn()
        PASS += 1
        print(f"PASS {name} {detail or ''}")
    except Exception as e:  # noqa: BLE001
        FAIL += 1
        print(f"FAIL {name}: {e}")


def get(path, headers=None, timeout=10):
    req = urllib.request.Request(BASE + path, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.load(r)


def post(path, payload, headers=None, timeout=10):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        BASE + path, data=data,
        headers={**(headers or {}), "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.load(r)


def t_gateway_root():
    req = urllib.request.Request(BASE + "/gateway-health")
    with urllib.request.urlopen(req, timeout=5) as r:
        text = r.read().decode()
    assert r.status == 200 and "MVP monolith" in text, text
    return "gateway up"


def t_health():
    status, body = get("/health")
    assert status == 200, status
    assert body.get("status") == "ok", body
    return "backend ok"


def t_landing():
    status, body = get("/api/v1/public/landing")
    assert status == 200, status
    keys = sorted(body["data"].keys())
    assert keys == ["categories", "highlights", "top_favorites", "top_ratings"], keys
    return f"keys={','.join(keys)}"


def t_frontend_home():
    req = urllib.request.Request(BASE + "/")
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8", "ignore")
    assert r.status == 200, r.status
    assert "Alats Travel" in html, "brand missing"
    return "blade ok"


def t_auth_login():
    status, body = post(
        "/api/v1/auth/login",
        {"email": "admin@alats.vn", "password": "Admin@123"},
    )
    assert status == 200, body
    assert body["data"]["expires_in"] == 30, body
    return "login ok"


check("gateway root", t_gateway_root)
check("backend health", t_health)
check("public landing", t_landing)
check("frontend home", t_frontend_home)
check("admin login", t_auth_login)

print(f"\n{ PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
