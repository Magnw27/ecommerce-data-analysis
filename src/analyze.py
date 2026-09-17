"""Feature engineering and summary statistics for NVDA candles."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "nvda.csv"
DEFAULT_OUTPUT = ROOT / "data" / "nvda_processed.csv"


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    df = df.sort_values("datetime")
    df["return_pct"] = df["close"].pct_change() * 100
    df["sma_20"] = df["close"].rolling(20, min_periods=1).mean()
    df["sma_50"] = df["close"].rolling(50, min_periods=1).mean()
    df["volatility_20"] = df["return_pct"].rolling(20, min_periods=5).std()
    df["range_pct"] = ((df["high"] - df["low"]) / df["close"]) * 100
    df["volume_sma_20"] = df["volume"].rolling(20, min_periods=1).mean()
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    processed = build_features(frame)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(output, index=False)

    latest = processed.iloc[-1]
    print(f"Latest close: ${latest['close']:.2f}")
    print(f"Latest daily return: {latest['return_pct']:.2f}%")
    print(f"20-period SMA: ${latest['sma_20']:.2f}")
    print(f"20-period volatility: {latest['volatility_20']:.2f}%")


if __name__ == "__main__":
    main()
