from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json, os
import requests as http

BASE_URL = os.environ.get("METER_API_URL", "http://47.243.132.219:8039/api/Meter")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        task_id = qs.get("taskId", [""])[0]

        result = {"ready": False, "data": None, "error": None}
        try:
            url = f"{BASE_URL}/GetReadReturnData?taskId={task_id}"
            resp = http.get(url, timeout=10).json()
            code = (resp.get("ReturnCode") or resp.get("state") or "").lower()
            data = resp.get("Data") or resp.get("data")
            if code == "success" and data:
                result["ready"] = True
                result["data"] = data
        except Exception as e:
            result["error"] = str(e)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def log_message(self, format, *args):
        pass
