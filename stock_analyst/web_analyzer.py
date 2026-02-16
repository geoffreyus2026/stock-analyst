import csv
import io
import urllib.parse
import urllib.request
from datetime import datetime


def _fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "iStockPick/1.0 (admin@istockpick.ai)"})
    with urllib.request.urlopen(req, timeout=8) as response:
        return response.read().decode("utf-8", errors="ignore")


def _to_float(value, default=None):
    try:
        return float(value)
    except Exception:
        return default


def get_stock_snapshot(symbol: str) -> dict:
    code = f"{symbol.lower()}.us"

    # Latest quote (Open,High,Low,Close,Volume)
    quote_url = f"https://stooq.com/q/l/?s={urllib.parse.quote(code)}&i=d"
    quote_raw = _fetch_text(quote_url).strip()
    parts = quote_raw.split(",")
    if len(parts) < 8:
        raise ValueError(f"No quote data for {symbol}")

    open_price = _to_float(parts[3], 0)
    high_price = _to_float(parts[4], 0)
    low_price = _to_float(parts[5], 0)
    close_price = _to_float(parts[6], 0)
    volume = _to_float(parts[7], 0)

    # Historical data for trend + averages
    hist_url = f"https://stooq.com/q/d/l/?s={urllib.parse.quote(code)}&i=d"
    hist_csv = _fetch_text(hist_url)
    reader = csv.DictReader(io.StringIO(hist_csv))
    rows = [r for r in reader if r.get("Close")]
    if not rows:
        raise ValueError(f"No historical data for {symbol}")

    closes = [_to_float(r["Close"], 0) for r in rows if _to_float(r["Close"], None) is not None]
    volumes = [_to_float(r["Volume"], 0) for r in rows if _to_float(r["Volume"], None) is not None]

    prev_close = closes[-2] if len(closes) > 1 else close_price
    change_pct = ((close_price - prev_close) / prev_close * 100) if prev_close else 0

    ma50 = sum(closes[-50:]) / min(len(closes), 50)
    ma200 = sum(closes[-200:]) / min(len(closes), 200)
    avg_volume_20 = sum(volumes[-20:]) / min(len(volumes), 20) if volumes else 0

    trend = "NEUTRAL"
    if change_pct > 2:
        trend = "BULLISH"
    elif change_pct < -2:
        trend = "BEARISH"

    return {
        "symbol": symbol,
        "name": symbol,
        "price": close_price,
        "change_pct": change_pct,
        "volume_ratio": (volume / avg_volume_20) if avg_volume_20 else 1,
        "trend": trend,
        "fifty_day_avg": ma50,
        "two_hundred_day_avg": ma200,
        "open": open_price,
        "high": high_price,
        "low": low_price,
        "volume": volume,
    }


def get_sentiment(snapshot: dict) -> dict:
    score = 50
    drivers = []

    if snapshot["trend"] == "BULLISH":
        score += 15
        drivers.append("positive price momentum")
    elif snapshot["trend"] == "BEARISH":
        score -= 15
        drivers.append("negative price momentum")

    if snapshot.get("volume_ratio", 1) > 1.5:
        score += 8
        drivers.append("elevated trading volume")

    if snapshot["fifty_day_avg"] > snapshot["two_hundred_day_avg"]:
        score += 7
        drivers.append("50D MA above 200D MA")
    else:
        score -= 7
        drivers.append("50D MA below 200D MA")

    score = max(0, min(100, score))
    label = "neutral"
    if score >= 65:
        label = "bullish"
    elif score <= 35:
        label = "bearish"

    return {
        "score": score,
        "label": label,
        "summary": f"Market sentiment appears {label} (score {score}/100).",
        "drivers": drivers,
    }


def get_ai_recommendation(snapshot: dict, sentiment: dict) -> dict:
    score = sentiment["score"]

    if snapshot["price"] > snapshot["fifty_day_avg"]:
        score += 5
    else:
        score -= 5

    score = max(0, min(100, score))

    action = "HOLD"
    if score >= 65:
        action = "BUY"
    elif score <= 35:
        action = "SELL"

    return {
        "action": action,
        "confidence": score,
        "summary": f"AI recommendation: {action} based on trend, volume, and sentiment.",
        "disclaimer": "For informational purposes only, not financial advice.",
    }


def generate_full_analysis(symbol: str) -> dict:
    snapshot = get_stock_snapshot(symbol)
    sentiment = get_sentiment(snapshot)
    ai_reco = get_ai_recommendation(snapshot, sentiment)

    stock_summary = {
        "summary": f"${snapshot['price']:.2f} • Trend: {snapshot['trend']} • 1D change: {snapshot['change_pct']:.2f}%",
        "details": snapshot,
    }

    return {
        "symbol": snapshot["symbol"],
        "company": snapshot["name"],
        "stock_analysis": stock_summary,
        "sentiment_analysis": sentiment,
        "ai_recommendation": ai_reco,
        "generated_at": datetime.now().isoformat(),
    }
