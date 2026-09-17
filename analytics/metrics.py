"""Pure summary metrics used by notebooks, scripts and dashboards."""
from __future__ import annotations

import pandas as pd


def summarize(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {}
    latest = frame.iloc[-1]
    previous = frame.iloc[-2] if len(frame) > 1 else latest
    returns = frame["return_pct"].dropna().tail(20)
    return {
        "latest_close": float(latest["close"]),
        "daily_change": float(latest["close"] - previous["close"]),
        "daily_change_pct": float(latest["return_pct"]) if pd.notna(latest["return_pct"]) else 0.0,
        "period_high": float(frame["high"].max()),
        "period_low": float(frame["low"].min()),
        "avg_volume_20": float(frame["volume"].tail(20).mean()),
        "volatility_20": float(returns.std()) if len(returns) > 1 else 0.0,
        "max_drawdown": float(frame["drawdown_pct"].min()) if "drawdown_pct" in frame else 0.0,
        "observations": int(len(frame)),
    }
