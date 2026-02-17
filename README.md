# Stock Analysis & Trading Recommendation System

## Overview
AI-powered system that provides comprehensive stock analysis and trading recommendations using technical analysis, fundamental analysis, and sentiment analysis.

## Features
- Technical analysis with multiple indicators
- Fundamental analysis using company financials
- Sentiment analysis from X/Twitter and financial news
- Multiple trading strategies (momentum, value, growth, options)
- Risk assessment and position sizing
- Comprehensive reporting with recommendations

## Data Sources
- Alpaca API (real-time pricing, market data)
- Yahoo Finance (historical data, financials)
- X/Twitter (social sentiment)
- WSJ, CNBC, Reuters, FT (news sentiment)

## Trading Strategies
- Momentum trading
- Deep value investing
- Growth holds
- Options strategies
- Swing trading
- Day trading

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
from stock_analyst import generate_full_analysis

analysis = generate_full_analysis("AAPL")
print(analysis["ai_recommendation"])
```

## API Endpoint
Run the API server:

```bash
uvicorn stock_analyst.api:app --host 0.0.0.0 --port 8000
```

Register an agent (one-time per agent name):

```bash
curl -X POST "https://api.istockpick.ai/api/v1/agents/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"agent-alpha"}'
```

Response includes generated token and is stored in local text DB:
- `data/agents_db.txt`

Get recommendation by ticker or company name (requires `agent_name` + `agent_token`):

```bash
curl "https://api.istockpick.ai/api/v1/recommendation?stock=AAPL&agent_name=agent-alpha&agent_token=REPLACE_WITH_TOKEN"
curl "https://api.istockpick.ai/api/v1/recommendation?stock=Apple%20Inc&agent_name=agent-alpha&agent_token=REPLACE_WITH_TOKEN"
```

Or call by `POST`:

```bash
curl -X POST "https://api.istockpick.ai/api/v1/recommendation" \
  -H "Content-Type: application/json" \
  -d '{"stock":"AAPL","agent_name":"agent-alpha","agent_token":"REPLACE_WITH_TOKEN"}'
```

## Download SKILL.md via curl
Users can download the latest skill file directly from your website:

```bash
curl -L "https://api.istockpick.ai/SKILL.md" -o SKILL.md
```

## Deploy API To api.istockpick.ai
This repo includes production templates:
- `deploy/systemd/stock-analyst-api.service`
- `deploy/nginx/api.istockpick.ai.conf`

On your server:

```bash
cd /opt
git clone git@github.com:geoffreyus2026/stock-analyst.git
cd stock-analyst
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `/opt/stock-analyst/.env` with required keys, then:

```bash
sudo cp deploy/systemd/stock-analyst-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now stock-analyst-api
sudo systemctl status stock-analyst-api
```

Configure nginx:

```bash
sudo cp deploy/nginx/api.istockpick.ai.conf /etc/nginx/sites-available/api.istockpick.ai.conf
sudo ln -s /etc/nginx/sites-available/api.istockpick.ai.conf /etc/nginx/sites-enabled/api.istockpick.ai.conf
sudo nginx -t
sudo systemctl reload nginx
```

Then verify:

```bash
curl "https://api.istockpick.ai/health"
curl -X POST "https://api.istockpick.ai/api/v1/agents/register" -H "Content-Type: application/json" -d '{"name":"agent-alpha"}'
```
