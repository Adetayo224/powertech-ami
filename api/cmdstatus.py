from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json, os
import requests as http

BASE_URL = os.environ.get("METER_API_URL", "http://47.243.132.219:8039/api/Meter")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        task_id = qs.get("taskId", [""])[0]

        result = {"done": False, "ok": None, "raw": None, "error": None}
        try:
            url = f"{BASE_URL}/GetCommandTaskExecStatus?taskId={task_id}"
            resp = http.get(url, timeout=10).json()
            result["raw"] = resp
            code = (resp.get("ReturnCode") or resp.get("state") or resp.get("Status") or "").lower()
            if "success" in code:
                result["done"] = True
                result["ok"] = True
            elif any(x in code for x in ("fail", "error", "invalid")):
                result["done"] = True
                result["ok"] = False
        except Exception as e:
            result["error"] = str(e)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def log_message(self, format, *args):
        pass
