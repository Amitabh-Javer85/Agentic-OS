#!/usr/bin/env python3
"""Automated security and acceptance tests for the Agentic OS Local Runner."""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
PORT = 3000
BASE_URL = f"http://127.0.0.1:{PORT}"
TOKEN_FILE = WORKSPACE_ROOT / ".local-token"

def run_tests():
    print("Starting Agentic OS Runner Security Tests...")
    
    # 1. Start runner server in background process
    proc = subprocess.Popen(
        [sys.executable, str(WORKSPACE_ROOT / "apps" / "runner" / "server.py"), "serve"],
        cwd=str(WORKSPACE_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    time.sleep(1.2)  # Give server a moment to bind

    passed = 0
    failed = 0

    try:
        # Load local token
        if not TOKEN_FILE.is_file():
            print("FAIL: .local-token was not generated on startup")
            failed += 1
            return 1
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()

        # Test 1: Unauthenticated request should return 401
        try:
            req = urllib.request.Request(f"{BASE_URL}/api/v1/status")
            urllib.request.urlopen(req)
            print("FAIL: Unauthenticated request was allowed")
            failed += 1
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print("PASS: Unauthenticated request returned 401")
                passed += 1
            else:
                print(f"FAIL: Expected 401, got {e.code}")
                failed += 1

        # Test 2: Authenticated request should return 200 and valid JSON
        try:
            req = urllib.request.Request(
                f"{BASE_URL}/api/v1/status",
                headers={"Authorization": f"Bearer {token}"}
            )
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                assert data["status"] == "ok"
                assert "weekly-digest" in data["registered_skills"]
                print("PASS: Authenticated status call succeeded (skills discovered)")
                passed += 1
        except Exception as e:
            print(f"FAIL: Authenticated status request failed: {e}")
            failed += 1

        # Test 3: Cross-origin request with untrusted origin should return 403
        try:
            req = urllib.request.Request(
                f"{BASE_URL}/api/v1/status",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Origin": "http://malicious-website.com"
                }
            )
            urllib.request.urlopen(req)
            print("FAIL: Malicious cross-origin request was allowed")
            failed += 1
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print("PASS: Malicious cross-origin request rejected with 403")
                passed += 1
            else:
                print(f"FAIL: Expected 403 for untrusted origin, got {e.code}")
                failed += 1

        # Test 4: Free-form prompt / unallowlisted skill name should return 400
        try:
            req = urllib.request.Request(
                f"{BASE_URL}/api/v1/run-skill",
                data=json.dumps({"skill_name": "rm -rf /"}).encode(),
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            urllib.request.urlopen(req)
            print("FAIL: Unregistered skill name was allowed to execute")
            failed += 1
        except urllib.error.HTTPError as e:
            if e.code == 400:
                print("PASS: Unregistered skill rejected with 400")
                passed += 1
            else:
                print(f"FAIL: Expected 400 for bad skill, got {e.code}")
                failed += 1

        # Test 5: Command Centre HTML is served at root
        try:
            with urllib.request.urlopen(f"{BASE_URL}/") as resp:
                html = resp.read().decode("utf-8")
                assert "<title>Agentic OS — Command Centre</title>" in html
                print("PASS: Command Centre HTML served at /")
                passed += 1
        except Exception as e:
            print(f"FAIL: Serving Command Centre HTML failed: {e}")
            failed += 1

    finally:
        proc.terminate()
        proc.wait(timeout=3)

    print(f"\nTest Summary: {passed} PASSED, {failed} FAILED")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(run_tests())
