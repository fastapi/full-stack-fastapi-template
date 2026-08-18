#!/usr/bin/env python3
"""Smoke test for RBAC API endpoints."""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://localhost:8000"


def token(email: str, password: str) -> str:
    data = urllib.parse.urlencode({"username": email, "password": password}).encode()
    req = urllib.request.Request(f"{BASE}/api/v1/login/access-token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["access_token"]


def status_code(path: str, access_token: str) -> int:
    req = urllib.request.Request(f"{BASE}{path}")
    req.add_header("Authorization", f"Bearer {access_token}")
    try:
        urllib.request.urlopen(req)
        return 200
    except urllib.error.HTTPError as exc:
        return exc.code


def main() -> int:
    admin = token("admin@example.com", "changethis")
    manager = token("manager@example.com", "changethis")
    member = token("member@example.com", "changethis")

    checks = {
        "admin_users": status_code("/api/v1/users/", admin),
        "manager_users": status_code("/api/v1/users/", manager),
        "member_users": status_code("/api/v1/users/", member),
        "admin_metrics": status_code("/api/v1/metrics/", admin),
        "member_metrics": status_code("/api/v1/metrics/", member),
    }
    for name, code in checks.items():
        print(f"{name}: {code}")

    expected = {
        "admin_users": 200,
        "manager_users": 200,
        "member_users": 403,
        "admin_metrics": 200,
        "member_metrics": 403,
    }
    return 0 if checks == expected else 1


if __name__ == "__main__":
    sys.exit(main())
