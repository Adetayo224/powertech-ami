from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json, os
import requests as http

BASE_URL   = os.environ.get("METER_API_URL", "http://47.243.132.219:8039/api/Meter")
USER_ID    = os.environ.get("METER_USER_ID", "N245")
PASSWORD   = os.environ.get("METER_PASSWORD", "nig0115")
METER_CODE = os.environ.get("METER_CODE", "046252417921")

ENDPOINTS = {
    "credit":  "GetAvailableCredit",
    "energy":  "GetActiveEnergy",
    "monthly": "GetMonthlyUsage",
}

def extract_task_id(resp):
    try:
        body = resp.json()
        raw = body.get("data") or body.get("Data", "")
        return str(raw).replace("Command taskId:", "").strip()
    except Exception:
        return ""

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        meter_type = qs.get("type", ["credit"])[0]
        endpoint = ENDPOINTS.get(meter_type, "GetAvailableCredit")

        result = {"taskId": "", "error": None}
        try:
            url = f"{BASE_URL}/{endpoint}?UserId={USER_ID}&Pwd={PASSWORD}&MeterCode={METER_CODE}"
            resp = http.get(url, timeout=10)
            result["taskId"] = extract_task_id(resp)
        except Exception as e:
            result["error"] = str(e)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def log_message(self, format, *args):
        pass
