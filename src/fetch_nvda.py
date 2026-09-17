"""Fetch public NVDA market candles and save a normalized CSV."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import requests

from .config import EXCHANGE_TZ, MARKET_API, RAW_PATH, TICKER
from .data_loader import validate_market_frame


def fetch_market_data(period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    params = {"range": period, "interval": interval, "includePrePost": "false", "events": "div,splits"}
    response = requests.get(
        MARKET_API.format(ticker=TICKER),
        params=params,
        timeout=20,
        headers={"User-Agent": "Magnw27-NVDA-Market-Lab/2.0"},
    )
    response.raise_for_status()
    result = response.json().get("chart", {}).get("result", [None])[0]
    if not result:
        raise RuntimeError("The market-data provider returned no NVDA result")

    timestamps = result.get("timestamp", [])
    quote = result.get("indicators", {}).get("quote", [{}])[0]
    frame = pd.DataFrame(quote)
    frame.insert(0, "datetime", pd.to_datetime(timestamps, unit="s", utc=True))
    frame["datetime"] = frame["datetime"].dt.tz_convert(EXCHANGE_TZ)
    frame["ticker"] = TICKER
    columns = ["datetime", "ticker", "open", "high", "low", "close", "volume"]
    return validate_market_frame(frame[columns])


def save_market_data(frame: pd.DataFrame, output: Path = RAW_PATH) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Download public NVDA OHLCV data")
    parser.add_argument("--period", default="1y", choices=["1mo", "3mo", "6mo", "1y", "2y", "5y"])
    parser.add_argument("--interval", default="1d", choices=["1d", "1h", "5m"])
    parser.add_argument("--output", default=str(RAW_PATH))
    args = parser.parse_args()
    frame = fetch_market_data(args.period, args.interval)
    path = save_market_data(frame, Path(args.output))
    print(f"Saved {len(frame):,} rows to {path}")


if __name__ == "__main__":
    main()
