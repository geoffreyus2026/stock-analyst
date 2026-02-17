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
