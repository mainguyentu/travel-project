import json
import urllib.request

BASE = "http://127.0.0.1:8013"


def get(path, headers=None):
    req = urllib.request.Request(BASE + path, headers=headers or {})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def post(path, payload, headers=None):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        BASE + path, data=data,
        headers={**(headers or {}), "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)


print("health:", get("/health"))
landing = get("/api/v1/public/landing")
print("landing keys:", sorted(landing["data"].keys()))
dest = get("/api/v1/destinations?page=1&limit=2")
print("destinations total:", dest["meta"]["total"])
pair = post("/api/v1/auth/login", {"email": "admin@alats.vn", "password": "Admin@123"})
print("login ok, expires_in:", pair["data"]["expires_in"])
h = {"Authorization": "Bearer " + pair["data"]["access_token"]}
users = get("/api/v1/admin/users", h)
print("admin users total:", users["meta"]["total"])
