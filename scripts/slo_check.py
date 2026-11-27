"""Post-deploy SLO check (Pha D): gateway-health, /health, /ready, landing, login.

Usage: python scripts/slo_check.py --base-url http://127.0.0.1:8080 [--admin-email .. --admin-password ..]
Exit non-zero when any check fails. Production-safe: read-only except admin login.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request

CHECKS: list[str] = []


def check(name: str):
    def deco(fn):
        CHECKS.append(name)
        return fn
    return deco


def get(base: str, path: str, headers: dict | None = None, timeout: int = 10):
    req = urllib.request.Request(base + path, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


@check("gateway-health")
def c_gateway(base: str, _: dict) -> str:
    status, body = get(base, "/gateway-health")
    assert status == 200 and b"MVP" in body or b"monolith" in body, body[:100]
    return "gateway up"


@check("backend-health")
def c_health(base: str, _: dict) -> str:
    status, body = get(base, "/health")
    assert status == 200 and json.loads(body)["status"] == "ok", body[:100]
    return "health ok"


@check("ready")
def c_ready(base: str, _: dict) -> str:
    status, body = get(base, "/ready")
    data = json.loads(body)
    assert status == 200 and data["success"], body[:200]
    return f"ready={data['data']['ready']} checks={data['data']['checks']}"


@check("landing")
def c_landing(base: str, _: dict) -> str:
    status, body = get(base, "/api/v1/public/landing")
    data = json.loads(body)["data"]
    for k in ("categories", "highlights", "top_favorites", "top_ratings"):
        assert k in data, k
    return f"landing keys ok ({len(data['highlights'])} highlights)"


@check("admin-login")
def c_login(base: str, args: dict) -> str:
    payload = json.dumps({"email": args["email"], "password": args["password"]}).encode()
    req = urllib.request.Request(
        base + "/api/v1/auth/login", data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read())
    assert data["success"] and data["data"]["expires_in"] == 30, data
    return "login ok expires_in=30"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    ap.add_argument("--admin-email", default="admin@alats.vn")
    ap.add_argument("--admin-password", default="Admin@123")
    ns = ap.parse_args()
    args = {"email": ns.admin_email, "password": ns.admin_password}
    fns = {
        "gateway-health": c_gateway, "backend-health": c_health, "ready": c_ready,
        "landing": c_landing, "admin-login": c_login,
    }
    passed, failed = 0, 0
    for name in CHECKS:
        try:
            detail = fns[name](ns.base_url, args)
            print(f"PASS {name} {detail}")
            passed += 1
        except Exception as exc:  # noqa: BLE001 — report then continue
            print(f"FAIL {name}: {exc}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
