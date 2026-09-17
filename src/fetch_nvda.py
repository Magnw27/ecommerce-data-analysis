"""Fetch public NVDA market candles and save them as CSV."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "nvda.csv"


def fetch_nvda(period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    params = {
        "range": period,
        "interval": interval,
        "includePrePost": "false",
        "events": "div,splits",
    }
    response = requests.get(
        BASE_URL.format(ticker="NVDA"),
        params=params,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()
    payload = response.json()
    result = payload["chart"]["result"][0]

    timestamps = result.get("timestamp", [])
    quote = result["indicators"]["quote"][0]
    frame = pd.DataFrame(quote)
    frame.insert(0, "timestamp", pd.to_datetime(timestamps, unit="s", utc=True))
    frame = frame.rename(columns={"timestamp": "datetime"})
    frame["datetime"] = frame["datetime"].dt.tz_convert("America/New_York")
    frame["ticker"] = "NVDA"

    columns = ["datetime", "ticker", "open", "high", "low", "close", "volume"]
    frame = frame[columns].dropna(subset=["close"]).sort_values("datetime")
    return frame.reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", default="1y")
    parser.add_argument("--interval", default="1d")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = fetch_nvda(args.period, args.interval)
    frame.to_csv(output, index=False)
    print(f"Saved {len(frame):,} rows to {output}")


if __name__ == "__main__":
    main()
