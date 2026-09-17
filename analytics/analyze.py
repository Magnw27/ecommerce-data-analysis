"""CLI entry point for feature engineering and market summaries."""
from __future__ import annotations

import argparse
from pathlib import Path

from .config import PROCESSED_PATH, RAW_PATH
from .data_loader import load_csv
from .features import add_features
from .metrics import summarize


def build_features(frame):
    return add_features(frame)


def main() -> None:
    parser = argparse.ArgumentParser(description="Engineer features from NVDA OHLCV data")
    parser.add_argument("--input", default=str(RAW_PATH))
    parser.add_argument("--output", default=str(PROCESSED_PATH))
    args = parser.parse_args()
    processed = add_features(load_csv(args.input))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(output, index=False)
    print(summarize(processed))


if __name__ == "__main__":
    main()
