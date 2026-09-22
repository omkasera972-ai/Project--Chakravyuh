import sys
import os
import urllib.request
import json

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_dir = os.path.join(root_dir, 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

import hmac as _hmac
import hashlib as _hashlib
import base64 as _base64
import time as _time
import json as _json

SECRET_KEY = os.getenv("SECRET_KEY", "chakravyuh-secret-key-2026")

def create_admin_token(admin_id: str, username: str, module_id: str) -> str:
    payload = {
        "admin_id": admin_id,
        "username": username,
        "role": "admin",
        "moduleId": module_id,
        "iat": int(_time.time()),
        "exp": int(_time.time()) + (86400 * 7)
    }
    raw_json = _json.dumps(payload).encode("utf-8")
    b64_payload = _base64.urlsafe_b64encode(raw_json).decode("utf-8")
    signature = _hmac.new(SECRET_KEY.encode("utf-8"), b64_payload.encode("utf-8"), _hashlib.sha256).hexdigest()
    return f"{b64_payload}.{signature}"

token = create_admin_token("ADM-CRIM-1789132093", "admin", "criminal")

url = "http://127.0.0.1:8000/api/alerts/dispatch-auto"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}
payload = {
    "targetName": "Automatic Detection Test",
    "targetId": "CRIM-TEST-422",
    "crimeType": "Armed Robbery Surveillance",
    "cameraNode": "WEB-Cam01",
    "confidence": "98.5%",
    "lat": 24.515996,
    "lng": 75.702526
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as resp:
        print("STATUS CODE:", resp.status)
        print("RESPONSE:", json.loads(resp.read().decode("utf-8")))
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code)
    print("BODY:", e.read().decode("utf-8"))
