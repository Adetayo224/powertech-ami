# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**PowerTech AMI Dashboard** — A web application for monitoring and controlling a Hexcell DDSY1088 smart meter via the AMI API. Features live meter readings (credit, energy, monthly usage), remote STS token injection, and relay control.

- Meter serial: `046252417921`
- AMI API base: `http://47.243.132.219:8039/api/Meter`
- AMI portal: `http://47.243.132.219:8091/Admin/Login` (credentials: N245 / nig0115)
- Hosted on Vercel, source on GitHub (Adetayo224)

## Architecture

**Static frontend + Python serverless functions** (Vercel-native pattern):
- `public/index.html` — full dashboard (HTML + CSS + JS, no framework)
- `api/*.py` — Python serverless functions, each exporting a `handler(BaseHTTPRequestHandler)` class

**API flow** — the AMI API is async: every action triggers a background task and returns a `taskId`. The frontend polls for completion.

| File | Route | Purpose |
|---|---|---|
| `api/trigger.py` | `GET /api/trigger?type=credit\|energy\|monthly` | Trigger a meter read, returns `{taskId}` |
| `api/poll.py` | `GET /api/poll?taskId=` | Check read result via `GetReadReturnData` |
| `api/vend.py` | `POST /api/vend` body `{token}` | Inject STS token via `VendToken` |
| `api/relay.py` | `POST /api/relay` body `{action}` | Connect/disconnect relay |
| `api/cmdstatus.py` | `GET /api/cmdstatus?taskId=` | Poll command completion via `GetCommandTaskExecStatus` |

Read operations use `poll.py`; write operations (vend, relay) use `cmdstatus.py`.

**Credentials** are hardcoded as `os.environ.get("VAR", "default")` fallbacks. Override via Vercel env vars: `METER_USER_ID`, `METER_PASSWORD`, `METER_CODE`, `METER_API_URL`.

## AMI API Response Shapes

- Task trigger responses: `{"data": "Command taskId: 12345"}` or `{"Data": "..."}`
- `GetReadReturnData`: `{"ReturnCode": "Success", "Data": [{Param_Name, Data_Str, Data_Unit}, ...]}`
- `GetCommandTaskExecStatus`: `{"ReturnCode": "Success"}` or `{"state": "success"}` (field name varies)
- The API uses inconsistent casing (`ReturnCode` vs `state`, `Data` vs `data`) — all parsers handle both.

## CLI Script

`mainn.py` — standalone reader (no web server). Run with the venv active:
```powershell
.\venv\Scripts\Activate.ps1
python mainn.py
```

## Deployment

Vercel auto-detects:
- Python files in `api/` → serverless functions
- Files in `public/` → static CDN assets
- `requirements.txt` → installs `requests` for each function
