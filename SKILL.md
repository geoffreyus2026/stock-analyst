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

## Patch Known Codebase Blockers Before Deploy

Apply these fixes first because they currently break documented usage and scripts:

1. Fix package exports in `stock_analyst/__init__.py`.
- Import and expose `TechnicalAnalyzer`, `FundamentalAnalyzer`, and `generate_full_analysis`.

2. Fix missing import in `scripts/process_tweets_fixed.py`.
- Add `timedelta` to `from datetime import ...`.

3. Fix dependency drift in `requirements.txt`.
- Add `pytz` because deployment scripts import it.

4. Fix README usage example.
- Replace non-existent `StockAnalyst` usage with currently available API from `stock_analyst.web_analyzer` or package-root exports after step 1.

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

3. Verify scripts execute.

```bash
python3 scripts/movers_catalyst_fixed.py
printf '[]' | python3 scripts/process_tweets_fixed.py
```

4. Verify dependency integrity.

```bash
pip check
```

## Deploy Procedure

Use the same flow for each target environment.

1. Pull latest mainline code and lock commit SHA for traceability.
2. Create clean virtual environment on target host/container.
3. Install dependencies from `requirements.txt`.
4. Inject secrets via environment variables or secret manager.
5. Run pre-deploy validation commands on target runtime.
6. Start runtime process that uses this package (scheduler, worker, API wrapper, or notebook job).
7. Record deployed commit SHA, deploy time, and operator.

## Post-Deploy Health Checks

1. Execute one live symbol analysis (`AAPL`) and verify non-error response shape.
2. Verify network calls to data providers succeed within expected latency.
3. Confirm logs do not contain repeated exceptions for missing keys/data.
4. Confirm any scheduled jobs produce output and timestamps as expected.

## Rollback Procedure

1. Keep previous known-good commit and requirements snapshot.
2. Recreate virtual environment from known-good commit.
3. Reapply previous secret configuration.
4. Run the same validation and health checks.
5. Switch traffic/jobs back to rolled-back instance.

## Common Failure Modes

1. `AttributeError` on package-root imports.
- Cause: stale `stock_analyst/__init__.py` exports.

2. `ModuleNotFoundError: pytz`.
- Cause: missing dependency in environment.

3. Empty or partial market data.
- Cause: provider/network issues or symbol not supported by source.

4. Errors from API credentials.
- Cause: missing/invalid `.env` values.

## Definition of Done

Treat deployment as complete only when all are true:

1. Dependencies install without error.
2. Import smoke tests pass.
3. Analysis function returns valid payload for at least one symbol.
4. Required scripts run without runtime exceptions.
5. Deploy metadata (commit SHA + timestamp) is recorded.
