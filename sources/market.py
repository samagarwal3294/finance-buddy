"""Fetch index / commodity / FX levels and daily % change via yfinance."""
import json
import os
import yfinance as yf

CONFIG = os.path.join(os.path.dirname(__file__), "..", "config", "markets.json")


def _quote(ticker):
    """Return (last_close, pct_change) using the last two daily closes."""
    try:
        hist = yf.Ticker(ticker).history(period="5d", interval="1d")
        closes = hist["Close"].dropna()
        if len(closes) < 2:
            return None, None
        last, prev = float(closes.iloc[-1]), float(closes.iloc[-2])
        pct = (last - prev) / prev * 100 if prev else None
        return last, pct
    except Exception as e:
        print(f"[market] {ticker} failed: {e}")
        return None, None


def fetch_market():
    with open(CONFIG) as f:
        groups = json.load(f)

    result = {}
    for group, tickers in groups.items():
        rows = []
        for name, ticker in tickers.items():
            last, pct = _quote(ticker)
            rows.append({"name": name, "last": last, "pct": pct})
        result[group] = rows
    return result


if __name__ == "__main__":
    from pprint import pprint
    pprint(fetch_market())
