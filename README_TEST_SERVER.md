# KrisBot Test Server

This repository includes `test_server.py`, a small FastAPI-based HTTP server that exposes KrisBot's scraping and username-probing helpers. It's intended for local testing with deterministic mock data.

Quick start

1. Create a virtualenv and install requirements:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2. Run the test server (mock mode is enabled by default):

```bash
python3 test_server.py
# or using uvicorn for production-like server
uvicorn test_server:app --host 127.0.0.1 --port 8000
```

3. Example curl requests:

```bash
curl -sS -X POST http://127.0.0.1:8000/tiktok/search -H 'Content-Type: application/json' -d '{"email":"a@b.com","phone":"+123"}' | jq .
curl -sS -X POST http://127.0.0.1:8000/tiktok/by_url -H 'Content-Type: application/json' -d '{"url":"https://www.tiktok.com/@someuser"}' | jq .
curl -sS -X POST http://127.0.0.1:8000/probe -H 'Content-Type: application/json' -d '{"pattern":"foo*"}' | jq .
```

Notes

- The server forces `MOCK_MODE=1` so it returns deterministic mock data without calling external APIs. This is safe for testing and CI.
- If you want to test against real APIs, unset `MOCK_MODE` and configure `TIKTOK_API_URL`, `INSTAGRAM_API_URL`, etc., in the environment.
