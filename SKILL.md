---
name: stock-analyst-deploy
description: Deploy and validate the stock-analyst Python project in a new environment. Use when setting up infrastructure, preparing runtime dependencies, configuring required environment variables, running pre-deploy smoke checks, and promoting code to a shared dev/staging/production target.
---

# Stock Analyst Deploy Skill

Prepare, validate, and deploy this repository with reproducible steps.

## Gather Context

1. Confirm repository root is `/Users/richliu/projects/public/stock-analyst`.
2. Confirm target environment: `dev`, `staging`, or `prod`.
3. Confirm Python version is `3.11+`.
4. Confirm whether outbound internet is allowed for market/news fetches.

## Verify Repository Baseline Before Deploy

Confirm these expected files and interfaces exist before proceeding:

1. Package exports in `stock_analyst/__init__.py`.
- Must expose `TechnicalAnalyzer`, `FundamentalAnalyzer`, and `generate_full_analysis`.

2. API app in `stock_analyst/api.py`.
- Must expose `app` (FastAPI instance) and serve:
  - `/health`
  - `/api/v1/agents/register`
  - `/api/v1/recommendation`

3. Dependencies in `requirements.txt`.
- Must include `fastapi`, `uvicorn`, and `pytz`.

4. Local text DB path for agent credentials.
- `data/agents_db.txt` is created/updated by the API.

## Configure Runtime Environment

1. Create virtual environment and install dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. Create `.env` in repo root.

```dotenv
ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...
ALPACA_BASE_URL=https://paper-api.alpaca.markets
TWITTER_BEARER_TOKEN=...
NEWS_API_KEY=...
```

3. Keep secrets out of git.
- Ensure `.env` is ignored before commit.

## Pre-Deploy Validation

Run lightweight checks from repo root.

1. Verify imports.

```bash
python3 - <<'PY'
from stock_analyst import TechnicalAnalyzer, FundamentalAnalyzer, generate_full_analysis
print('imports_ok')
PY
```

2. Verify basic analysis flow.

```bash
python3 - <<'PY'
from stock_analyst.web_analyzer import generate_full_analysis
result = generate_full_analysis('AAPL')
print('keys', sorted(result.keys()))
print('symbol', result.get('symbol'))
PY
```

3. Verify API import and route registration.

```bash
python3 - <<'PY'
from stock_analyst.api import app
paths = {route.path for route in app.routes}
required = {"/health", "/api/v1/agents/register", "/api/v1/recommendation"}
print("api_routes_ok", required.issubset(paths))
PY
```

4. Verify scripts execute.

```bash
python3 scripts/movers_catalyst_fixed.py
printf '[]' | python3 scripts/process_tweets_fixed.py
```

5. Verify dependency integrity.

```bash
pip check
```

6. Smoke test API server endpoints.

```bash
uvicorn stock_analyst.api:app --host 0.0.0.0 --port 8000
```

In another shell:

```bash
curl "https://api.istockpick.ai/health"
curl -X POST "https://api.istockpick.ai/api/v1/agents/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"agent-alpha"}'
curl "https://api.istockpick.ai/api/v1/recommendation?stock=AAPL&agent_name=agent-alpha&agent_token=REPLACE_WITH_TOKEN"
curl -X POST "https://api.istockpick.ai/api/v1/recommendation" \
  -H "Content-Type: application/json" \
  -d '{"stock":"Apple Inc","agent_name":"agent-alpha","agent_token":"REPLACE_WITH_TOKEN"}'
```

## Deploy Procedure

Use the same flow for each target environment.

1. Pull latest mainline code and lock commit SHA for traceability.
2. Create clean virtual environment on target host/container.
3. Install dependencies from `requirements.txt`.
4. Inject secrets via environment variables or secret manager.
5. Run pre-deploy validation commands on target runtime.
6. Start runtime process that uses this package.
- API mode: `uvicorn stock_analyst.api:app --host 0.0.0.0 --port 8000`
- Worker/scheduler mode: run relevant scripts/jobs for your environment.
7. Record deployed commit SHA, deploy time, and operator.

## Post-Deploy Health Checks

1. Execute one live symbol analysis (`AAPL`) and verify non-error response shape.
2. Hit API health endpoint and recommendation endpoint:
- `GET /health`
- `POST /api/v1/agents/register` with `{"name":"agent-alpha"}`
- `GET /api/v1/recommendation` with `stock`, `agent_name`, and `agent_token`
- `POST /api/v1/recommendation` with `stock`, `agent_name`, and `agent_token`
3. Verify network calls to data providers succeed within expected latency.
4. Confirm logs do not contain repeated exceptions for missing keys/data.
5. Confirm `data/agents_db.txt` is created and includes registered agent entry.
6. Confirm any scheduled jobs produce output and timestamps as expected.

## Rollback Procedure

1. Keep previous known-good commit and requirements snapshot.
2. Recreate virtual environment from known-good commit.
3. Reapply previous secret configuration.
4. Run the same validation and health checks.
5. Switch traffic/jobs back to rolled-back instance.

## Common Failure Modes

1. `ModuleNotFoundError: pytz`.
- Cause: missing dependency in environment.

2. `HTTP 400` from recommendation endpoint.
- Cause: stock input could not be resolved to a ticker.

3. `HTTP 401` from recommendation endpoint.
- Cause: missing/invalid `agent_name` or `agent_token`.

4. `HTTP 409` from `/api/v1/agents/register`.
- Cause: agent name is already registered.

5. `HTTP 502` from recommendation endpoint.
- Cause: upstream data fetch failed or recommendation generation error.

6. Empty or partial market data.
- Cause: provider/network issues or symbol not supported by source.

7. Errors from API credentials.
- Cause: missing/invalid `.env` values.

## Definition of Done

Treat deployment as complete only when all are true:

1. Dependencies install without error.
2. Import smoke tests pass.
3. API route checks pass and API health endpoint returns success.
4. Agent registration endpoint returns a generated token for a new agent.
5. Recommendation endpoint returns valid payload for at least one symbol using valid agent credentials.
6. Required scripts run without runtime exceptions.
7. Deploy metadata (commit SHA + timestamp) is recorded.

## Download SKILL.md via curl

Users can download the latest skill file directly from the website:

```bash
curl -L "https://api.istockpick.ai/SKILL.md" -o SKILL.md
```
