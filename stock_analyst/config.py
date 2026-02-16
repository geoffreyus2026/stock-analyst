import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys and Configuration
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', 'your_alpaca_api_key')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', 'your_alpaca_secret_key')
ALPACA_BASE_URL = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')

# Twitter/X API Credentials
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', 'your_twitter_bearer_token')

# News API Keys
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'your_news_api_key')

# Analysis Configuration
RISK_FREE_RATE = 0.05  # 5% risk-free rate
MARKET_BENCHMARK = 'SPY'
MIN_VOLUME_THRESHOLD = 1000000  # Minimum daily volume
PRICE_CHANGE_THRESHOLD = 0.02  # 2% minimum price change for alerts

# Trading Configuration
MAX_POSITION_SIZE = 0.1  # Maximum 10% of portfolio per position
STOP_LOSS_PERCENTAGE = 0.05  # 5% stop loss
TAKE_PROFIT_PERCENTAGE = 0.15  # 15% take profit

# Sentiment Configuration
SENTIMENT_THRESHOLD_BULLISH = 0.6
SENTIMENT_THRESHOLD_BEARISH = 0.4
NEWS_LOOKBACK_DAYS = 7
TWEET_COUNT_MINIMUM = 50