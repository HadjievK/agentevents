"""
graph_mail.py  —  Send email via Microsoft Graph, Device Code Flow
───────────────────────────────────────────────────────────────────
WHY Device Code Flow:
  • No App Registration needed (uses Microsoft's built-in "Microsoft Graph" app)
  • No redirect URI, no local HTTP server, no client secret
  • Works on any machine — even headless
  • You just open a URL in ANY browser and type a 6-character code

FIRST RUN:
  📱 Opening https://microsoft.com/devicelogin …
     Enter code: ABCD-EFGH
  → you paste that code, log in with your SAP account, click Accept
  → tokens saved to token_cache.json
  → never asked again (refresh token lasts ~90 days)

WHAT YOU NEED IN .env:
  GRAPH_USER_EMAIL=kristiyan.hadjiev@sap.com     ← required

OPTIONAL (only if SAP blocks /organizations/ endpoint):
  GRAPH_TENANT_ID=<your-sap-tenant-uuid>        ← see README if needed
"""

from __future__ import annotations

import json, os, sys, time, webbrowser
from pathlib import Path
from typing import Any

import requests

# ─── config ──────────────────────────────────────────────────────────────────
USER_EMAIL   = os.environ.get("GRAPH_USER_EMAIL", "").strip()

# Microsoft's public "Microsoft Graph" app — works for any M365 tenant
# No need to register your own app.
PUBLIC_CLIENT_ID = "1b730df6-6f10-4745-9e74-79e99bc38429"   # "Microsoft Graph Explorer" public app

# Tenant — /organizations/ works for any corporate M365 tenant.
# If SAP blocks that too, set GRAPH_TENANT_ID in .env (see below).
TENANT_ID        = os.environ.get("GRAPH_TENANT_ID", "").strip() or "organizations"
DEVICE_CODE_URL  = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/devicecode"
TOKEN_URL        = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
GRAPH_SEND_URL   = "https://graph.microsoft.com/v1.0/me/sendMail"

SCOPE            = "Mail.Send offline_access"
TOKEN_CACHE      = Path(__file__).resolve().parent / "token_cache.json"


# ══════════════════════════════════════════════════════════════════════════════
# TOKEN CACHE   – load / save / refresh
# ══════════════════════════════════════════════════════════════════════════════

class _Tokens:
    access_token:  str | None = None
    refresh_token: str | None = None
    expires_at:    float      = 0

    def load(self) -> bool:
        if not TOKEN_CACHE.exists():
            return False
        try:
            d = json.loads(TOKEN_CACHE.read_text(encoding="utf-8"))
            self.access_token  = d.get("access_token")
            self.refresh_token = d.get("refresh_token")
            self.expires_at    = d.get("expires_at", 0)
            return True
        except Exception:
            return False

    def save(self):
        TOKEN_CACHE.write_text(json.dumps({
            "access_token":  self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at":    self.expires_at,
        }), encoding="utf-8")

    def is_valid(self) -> bool:
        return self.access_token is not None and time.time() < (self.expires_at - 60)

    def apply(self, resp: dict):
        self.access_token  = resp["access_token"]
        self.refresh_token = resp.get("refresh_token", self.refresh_token)
        self.expires_at    = time.time() + resp.get("expires_in", 3600)

    def refresh(self) -> bool:
        if not self.refresh_token:
            return False
        r = requests.post(TOKEN_URL, data={
            "grant_type":    "refresh_token",
            "client_id":     PUBLIC_CLIENT_ID,
            "refresh_token": self.refresh_token,
            "scope":         SCOPE,
        })
        if r.status_code != 200:
            print(f"  ⚠️  refresh failed: {r.status_code}")
            return False
        self.apply(r.json())
        self.save()
        print("  ✅ Token refreshed silently.")
        return True


_tokens = _Tokens()


# ══════════════════════════════════════════════════════════════════════════════
# DEVICE CODE FLOW   – the "paste this code" dance (one time)
# ══════════════════════════════════════════════════════════════════════════════

def _device_code_login() -> bool:
    """
    1. Ask Microsoft for a device code
    2. Show the user the URL + code
    3. Poll until the user completes login (or timeout)
    """
    # step 1 — request device code
    r = requests.post(DEVICE_CODE_URL, data={
        "client_id": PUBLIC_CLIENT_ID,
        "scope":     SCOPE,
    })
    if r.status_code != 200:
        print(f"  ❌ Could not get device code: {r.status_code} {r.text[:200]}")
        return False

    info = r.json()
    device_code      = info["device_code"]
    user_code        = info["user_code"]           # e.g. "ABCD-EFGH"
    verification_uri = info["verification_uri"]    # https://microsoft.com/devicelogin
    expires_in       = info.get("expires_in", 300) # usually 5 min
    interval         = info.get("interval", 5)     # poll every 5s

    # step 2 — copy code to clipboard + open browser
    try:
        import subprocess
        subprocess.run(["clip"], input=user_code.encode(), check=True,
                       capture_output=True)
        clipboard_ok = True
    except Exception:
        clipboard_ok = False

    print()
    print("  ╭─────────────────────────────────────────────────────╮")
    print("  │  One-time login — takes ~5 seconds                  │")
    print("  ╠═════════════════════════════════════════════════════╣")
    if clipboard_ok:
        print(f"  │  ✅ Code copied to clipboard:  {user_code:<24} │")
        print(f"  │                                                     │")
        print(f"  │  Browser is opening — just Paste + Enter.          │")
    else:
        print(f"  │  Code:  {user_code:<46} │")
        print(f"  │  URL:   {verification_uri:<46} │")
    print(f"  │                                                     │")
    print(f"  │  Then approve the push on your Authenticator app.   │")
    print("  ╰─────────────────────────────────────────────────────╯")
    print()

    webbrowser.open(verification_uri)

    # step 3 — poll until done
    deadline = time.time() + expires_in
    while time.time() < deadline:
        time.sleep(interval)
        r = requests.post(TOKEN_URL, data={
            "grant_type":  "urn:ietf:params:oauth:grant-type:device_code",
            "client_id":   PUBLIC_CLIENT_ID,
            "device_code": device_code,
        })
        if r.status_code == 200:
            _tokens.apply(r.json())
            _tokens.save()
            print("  ✅ Logged in! Token saved. You won't be asked again.")
            return True

        error = r.json().get("error", "")
        if error == "authorization_pending":
            print("  ⏳ Waiting for you to log in…", end="\r")
            continue
        if error == "slow_down":
            interval += 5
            continue
        # any other error = failed
        print(f"\n  ❌ Login failed: {r.json().get('error_description', error)}")
        return False

    print("\n  ❌ Login timed out (5 min). Run again to retry.")
    return False


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════════════════════════

async def ensure_token() -> str | None:
    """Get a valid access token — from cache, refresh, or device login."""
    if not _tokens.access_token:
        _tokens.load()

    if _tokens.is_valid():
        return _tokens.access_token

    if _tokens.refresh_token and _tokens.refresh():
        return _tokens.access_token

    # nothing cached → device code login
    if _device_code_login():
        return _tokens.access_token
    return None


async def send_mail(to: list[str], subject: str, body: str) -> dict[str, Any]:
    """Send email via Graph API."""
    token = await ensure_token()
    if not token:
        return {"status": "error", "error": "Could not obtain access token."}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }
    payload = {
        "Message": {
            "Subject": subject,
            "Body":    {"ContentType": "Text", "Content": body},
            "ToRecipients": [
                {"EmailAddress": {"Address": addr.strip()}}
                for addr in to
            ],
        },
        "SaveToSentItems": "true",
    }

    resp = requests.post(GRAPH_SEND_URL, headers=headers, json=payload)

    if resp.status_code == 202:
        return {"status": "sent", "message_id": f"graph-{resp.headers.get('x-ms-request-id','?')}"}

    # 401 → try one silent refresh + retry
    if resp.status_code == 401 and _tokens.refresh():
        headers["Authorization"] = f"Bearer {_tokens.access_token}"
        resp = requests.post(GRAPH_SEND_URL, headers=headers, json=payload)
        if resp.status_code == 202:
            return {"status": "sent", "message_id": f"graph-{resp.headers.get('x-ms-request-id','?')}"}

    return {"status": "error", "error": f"{resp.status_code}: {resp.text[:200]}"}
