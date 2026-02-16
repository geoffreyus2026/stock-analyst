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
