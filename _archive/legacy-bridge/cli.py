#!/usr/bin/env python3
"""CLI chat client for Agentic OS Bridge."""

import json
import sys
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def status():
    try:
        resp = urllib.request.urlopen(f"{BASE_URL}/api/v1/status")
        data = json.loads(resp.read())
        print(f"Status: {data['status']}")
        print(f"Vault: {data['vault_path']}")
        print(f"Store: {data['session_store']}")
    except Exception as e:
        print(f"Bridge not reachable: {e}")
        sys.exit(1)

def chat(message: str, session_id: str = None):
    payload = {"message": message}
    if session_id:
        payload["session_id"] = session_id

    req = urllib.request.Request(
        f"{BASE_URL}/api/v1/chat",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )

    try:
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        print(f"\n[session: {data['session_id']}]")
        print(f"  → {data['reply']}")
        print(f"  tokens: {data['tokens_used']}")
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.read().decode()}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "status":
        status()
    elif sys.argv[1] == "chat":
        msg = sys.argv[2] if len(sys.argv) > 2 else input("You: ")
        chat(msg)
    else:
        print("Usage: python cli.py [status|chat <message>]")