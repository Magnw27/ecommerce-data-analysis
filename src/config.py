"""Shared configuration for the NVIDIA analytics pipeline."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_PATH = DATA_DIR / "nvda.csv"
PROCESSED_PATH = DATA_DIR / "nvda_processed.csv"
TICKER = "NVDA"
EXCHANGE_TZ = "America/New_York"
MARKET_API = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
