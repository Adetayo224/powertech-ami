from flask import Flask, jsonify, request
import os, re
import requests as http

app = Flask(__name__)

BASE_URL   = os.environ.get("METER_API_URL", "http://47.243.132.219:8039/api/Meter")
USER_ID    = os.environ.get("METER_USER_ID", "N245")
PASSWORD   = os.environ.get("METER_PASSWORD", "nig0115")
METER_CODE = os.environ.get("METER_CODE", "046252417921")

READ_ENDPOINTS = {
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


@app.route("/api/trigger")
def trigger():
    meter_type = request.args.get("type", "credit")
    endpoint = READ_ENDPOINTS.get(meter_type, "GetAvailableCredit")
    try:
        url = f"{BASE_URL}/{endpoint}?UserId={USER_ID}&Pwd={PASSWORD}&MeterCode={METER_CODE}"
        resp = http.get(url, timeout=10)
        return jsonify({"taskId": extract_task_id(resp)})
    except Exception as e:
        return jsonify({"taskId": "", "error": str(e)})


@app.route("/api/poll")
def poll():
    task_id = request.args.get("taskId", "")
    try:
        url = f"{BASE_URL}/GetReadReturnData?taskId={task_id}"
        resp = http.get(url, timeout=10).json()
        code = (resp.get("ReturnCode") or resp.get("state") or "").lower()
        data = resp.get("Data") or resp.get("data")
        ready = code == "success" and bool(data)
        return jsonify({"ready": ready, "data": data if ready else None})
    except Exception as e:
        return jsonify({"ready": False, "data": None, "error": str(e)})


@app.route("/api/vend", methods=["POST"])
def vend():
    body = request.get_json(silent=True) or {}
    token = re.sub(r"\D", "", body.get("token", ""))
    if len(token) != 20:
        return jsonify({"taskId": "", "error": "Token must be exactly 20 digits"})
    try:
        payload = {"UserId": USER_ID, "Pwd": PASSWORD, "MeterCode": METER_CODE, "Token": token}
        resp = http.post(f"{BASE_URL}/VendToken", json=payload, timeout=10)
        return jsonify({"taskId": extract_task_id(resp)})
    except Exception as e:
        return jsonify({"taskId": "", "error": str(e)})


@app.route("/api/relay", methods=["POST"])
def relay():
    body = request.get_json(silent=True) or {}
    action = body.get("action", "connect")
    endpoint = "ConnectMeter" if action == "connect" else "DisconnectMeter"
    try:
        url = f"{BASE_URL}/{endpoint}?UserId={USER_ID}&Pwd={PASSWORD}&MeterCode={METER_CODE}"
        resp = http.post(url, timeout=10)
        return jsonify({"taskId": extract_task_id(resp), "action": action})
    except Exception as e:
        return jsonify({"taskId": "", "action": action, "error": str(e)})


@app.route("/api/cmdstatus")
def cmdstatus():
    task_id = request.args.get("taskId", "")
    try:
        url = f"{BASE_URL}/GetCommandTaskExecStatus?taskId={task_id}"
        resp = http.get(url, timeout=10).json()
        val = resp.get("data") if resp.get("data") is not None else resp.get("Data")
        done = str(val) in ("0", "1")
        ok = (str(val) == "1") if done else None
        return jsonify({"done": done, "ok": ok, "raw": resp})
    except Exception as e:
        return jsonify({"done": False, "ok": None, "error": str(e)})
