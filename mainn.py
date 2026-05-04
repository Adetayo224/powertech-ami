import requests
import time

# ── Configuration ──────────────────────────────────────────
BASE_URL   = "http://47.243.132.219:8039/api/Meter"
USER_ID    = "N245"
PASSWORD   = "nig0115"
METER_CODE = "046252417921"
# ───────────────────────────────────────────────────────────

def get_task_id(response):
    """Extract task ID from API response."""
    data = response.json().get("data", "")
    if not data:
        data = response.json().get("Data", "")
    return str(data).replace("Command taskId:", "").strip()

def get_read_result(task_id, retries=10, delay=3):
    """Poll for read result using task ID."""
    url = f"{BASE_URL}/GetReadReturnData?taskId={task_id}"
    for i in range(retries):
        resp = requests.get(url).json()
        code = resp.get("ReturnCode", "") or resp.get("state", "")
        data = resp.get("Data") or resp.get("data")
        if str(code).lower() == "success" and data:
            return data
        print(f"    Waiting for result... ({i+1}/{retries})")
        time.sleep(delay)
    return None

def get_available_credit():
    print("\n📊 Reading Available Credit...")
    try:
        url = f"{BASE_URL}/GetAvailableCredit?UserId={USER_ID}&Pwd={PASSWORD}&MeterCode={METER_CODE}"
        resp = requests.get(url)
        print(f"    Status: {resp.status_code}")
        task_id = get_task_id(resp)
        print(f"    Task ID: {task_id}")
        result = get_read_result(task_id)
        if result:
            if isinstance(result, list):
                for item in result:
                    print(f"    {item.get('Param_Name')}: {item.get('Data_Str')} {item.get('Data_Unit')}")
            else:
                print(f"    Result: {result}")
        else:
            print("    No data returned yet — meter may still be processing")
        return result
    except Exception as e:
        print(f"    Error: {e}")
        return None

def get_active_energy():
    print("\n⚡ Reading Active Energy...")
    try:
        url = f"{BASE_URL}/GetActiveEnergy?UserId={USER_ID}&Pwd={PASSWORD}&MeterCode={METER_CODE}"
        resp = requests.get(url)
        print(f"    Status: {resp.status_code}")
        task_id = get_task_id(resp)
        print(f"    Task ID: {task_id}")
        result = get_read_result(task_id)
        if result:
            if isinstance(result, list):
                for item in result:
                    print(f"    {item.get('Param_Name')}: {item.get('Data_Str')} {item.get('Data_Unit')}")
            else:
                print(f"    Result: {result}")
        else:
            print("    No data returned yet — meter may still be processing")
        return result
    except Exception as e:
        print(f"    Error: {e}")
        return None

def get_monthly_usage():
    print("\n📅 Reading Monthly Usage...")
    try:
        url = f"{BASE_URL}/GetMonthlyUsage?UserId={USER_ID}&Pwd={PASSWORD}&MeterCode={METER_CODE}"
        resp = requests.get(url)
        print(f"    Status: {resp.status_code}")
        task_id = get_task_id(resp)
        print(f"    Task ID: {task_id}")
        result = get_read_result(task_id)
        if result:
            if isinstance(result, list):
                for item in result:
                    print(f"    {item.get('Param_Name')}: {item.get('Data_Str')} {item.get('Data_Unit')}")
            else:
                print(f"    Result: {result}")
        else:
            print("    No data returned yet — meter may still be processing")
        return result
    except Exception as e:
        print(f"    Error: {e}")
        return None


if __name__ == "__main__":
    print("=" * 50)
    print("   PowerTech — Hexcell DDSY1088 Live Reader")
    print("=" * 50)
    print(f"   Meter  : {METER_CODE}")
    print(f"   Server : {BASE_URL}")
    print("=" * 50)

    credit  = get_available_credit()
    energy  = get_active_energy()
    monthly = get_monthly_usage()

    print("\n" + "=" * 50)
    print("   Summary")
    print("=" * 50)
    print(f"   Credit  : {'✓ Retrieved' if credit  else '✗ No data'}")
    print(f"   Energy  : {'✓ Retrieved' if energy  else '✗ No data'}")
    print(f"   Monthly : {'✓ Retrieved' if monthly else '✗ No data'}")
    print("=" * 50)
    print("\nDone! 🎉")