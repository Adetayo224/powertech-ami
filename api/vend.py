from http.server import BaseHTTPRequestHandler
import json, os, re
import requests as http

BASE_URL   = os.environ.get("METER_API_URL", "http://47.243.132.219:8039/api/Meter")
USER_ID    = os.environ.get("METER_USER_ID", "N245")
PASSWORD   = os.environ.get("METER_PASSWORD", "nig0115")
METER_CODE = os.environ.get("METER_CODE", "046252417921")

def extract_task_id(resp):
    try:
        body = resp.json()
        raw = body.get("data") or body.get("Data", "")
        return str(raw).replace("Command taskId:", "").strip()
    except Exception:
        return ""

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) if length > 0 else b"{}")
        token = re.sub(r"\D", "", body.get("token", ""))

        result = {"taskId": "", "error": None}
        if len(token) != 20:
            result["error"] = "Token must be exactly 20 digits"
        else:
            try:
                url = f"{BASE_URL}/VendToken"
                payload = {
                    "UserId": USER_ID, "Pwd": PASSWORD,
                    "MeterCode": METER_CODE, "Token": token
                }
                resp = http.post(url, json=payload, timeout=10)
                result["taskId"] = extract_task_id(resp)
            except Exception as e:
                result["error"] = str(e)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass
