#!/usr/bin/env python3
"""
Scan S&P 500 tickers through iStockPick recommendation API and
return symbols matching a target recommendation action.

Example:
  python3 istockpick_reco_scan.py --rec sell --agent Geoffrey_US --token YOUR_TOKEN
  python3 istockpick_reco_scan.py --rec buy --agent Geoffrey_US --token YOUR_TOKEN --limit 50 --output buys.json
"""

import argparse
import csv
import io
import json
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

SP500_CSV_URL = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
API_URL = "https://api.istockpick.ai/api/v1/recommendation"


def fetch_sp500_symbols() -> list[str]:
    text = urllib.request.urlopen(SP500_CSV_URL, timeout=20).read().decode("utf-8", "ignore")
    rows = csv.DictReader(io.StringIO(text))
    symbols = []
    for row in rows:
        sym = (row.get("Symbol") or "").strip()
        if sym:
            symbols.append(sym.replace(".", "-"))
    return symbols


def call_reco(symbol: str, agent_name: str, agent_token: str, timeout: int) -> dict:
    params = urllib.parse.urlencode(
        {
            "stock": symbol,
            "agent_name": agent_name,
            "agent_token": agent_token,
        }
    )
    req = urllib.request.Request(f"{API_URL}?{params}", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "ignore"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan S&P 500 recommendations from iStockPick")
    parser.add_argument("--rec", required=True, choices=["buy", "hold", "sell"], help="Recommendation to filter")
    parser.add_argument("--agent", required=True, help="Registered agent name")
    parser.add_argument("--token", required=True, help="Registered agent token")
    parser.add_argument("--limit", type=int, default=0, help="Optional number of symbols to scan (0 = all)")
    parser.add_argument("--workers", type=int, default=12, help="Parallel requests")
    parser.add_argument("--timeout", type=int, default=15, help="Per-request timeout seconds")
    parser.add_argument("--output", default="", help="Optional output JSON path")
    args = parser.parse_args()

    target = args.rec.upper()
    symbols = fetch_sp500_symbols()
    if args.limit and args.limit > 0:
        symbols = symbols[: args.limit]

    matches = []
    errors = []
    ok = 0

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {
            pool.submit(call_reco, sym, args.agent, args.token, args.timeout): sym
            for sym in symbols
        }
        for i, fut in enumerate(as_completed(futures), 1):
            sym = futures[fut]
            try:
                payload = fut.result()
                rec = ((payload.get("recommendation") or {}).get("action") or "").upper()
                conf = (payload.get("recommendation") or {}).get("confidence")
                ok += 1
                if rec == target:
                    matches.append(
                        {
                            "symbol": payload.get("resolved_symbol") or sym,
                            "company": payload.get("company") or sym,
                            "action": rec,
                            "confidence": conf,
                            "summary": (payload.get("recommendation") or {}).get("summary"),
                            "generated_at": payload.get("generated_at"),
                        }
                    )
            except Exception as exc:
                errors.append({"symbol": sym, "error": str(exc)})

            if i % 50 == 0:
                print(f"progress {i}/{len(symbols)} ok={ok} match={len(matches)} err={len(errors)}", flush=True)

    matches.sort(key=lambda x: (x["confidence"] is None, -(x["confidence"] or 0), x["symbol"]))

    result = {
        "target": target,
        "scanned": len(symbols),
        "ok": ok,
        "errors": len(errors),
        "matches": matches,
        "error_details": errors,
    }

    print(json.dumps({k: result[k] for k in ["target", "scanned", "ok", "errors"]}, indent=2))
    print(f"\n{target} symbols ({len(matches)}):")
    for item in matches:
        print(f"- {item['symbol']} (confidence={item['confidence']})")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"\nSaved full output to: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
