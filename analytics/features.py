"""Feature engineering for market analytics."""
from __future__ import annotations

import numpy as np
import pandas as pd


def add_features(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy().sort_values("datetime").reset_index(drop=True)
    df["return_pct"] = df["close"].pct_change().mul(100)
    df["log_return"] = np.log(df["close"]).diff()
    df["sma_20"] = df["close"].rolling(20, min_periods=1).mean()
    df["sma_50"] = df["close"].rolling(50, min_periods=1).mean()
    df["ema_20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["volatility_20"] = df["return_pct"].rolling(20, min_periods=5).std()
    df["range_pct"] = (df["high"] - df["low"]).div(df["close"]).mul(100)
    df["volume_sma_20"] = df["volume"].rolling(20, min_periods=1).mean()
    df["drawdown_pct"] = (df["close"] / df["close"].cummax() - 1).mul(100)
    return df
