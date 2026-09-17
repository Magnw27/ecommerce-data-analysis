"""Data loading and validation helpers."""
from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = ["datetime", "ticker", "open", "high", "low", "close", "volume"]


def validate_market_frame(frame: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    df = frame.copy()
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    for column in ["open", "high", "low", "close", "volume"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=["datetime", "close"]).sort_values("datetime")
    df = df.drop_duplicates(subset=["datetime", "ticker"], keep="last")
    return df.reset_index(drop=True)


def load_csv(path) -> pd.DataFrame:
    return validate_market_frame(pd.read_csv(path))
