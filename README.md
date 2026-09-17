# NVIDIA Market Data Analysis

A real-time-style data analysis project for **NVIDIA Corporation (NASDAQ: NVDA)**.

> Note: this repository analyzes publicly available market data. Quote freshness depends on the upstream market-data provider; it should not be treated as NVIDIA's internal/private data or as an investment recommendation.

## What this project does

- Fetches recent NVDA market candles from a public market-data endpoint
- Stores normalized OHLCV data as CSV
- Calculates daily return, moving averages, volatility and volume statistics
- Provides an interactive Streamlit dashboard
- Can refresh the dataset automatically with GitHub Actions
- Keeps generated data and Python source separated for a clean portfolio structure

## Project structure

```text
ecommerce-data-analysis/
├── .github/workflows/update-data.yml
├── data/
│   └── .gitkeep
├── src/
│   ├── fetch_nvda.py
│   └── analyze.py
├── dashboard.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Quick start

```bash
python -m pip install -r requirements.txt
python src/fetch_nvda.py
python src/analyze.py
streamlit run dashboard.py
```

The dashboard can also fetch fresh data itself, so a pre-generated CSV is not required for local viewing.

## Metrics

- Current / latest available price
- Daily percentage change
- Volume
- 20-period moving average
- 50-period moving average
- Rolling volatility
- High/low range
- Recent price and volume charts

## Data source

The project uses publicly accessible market quote data for the NVDA ticker. NVIDIA's official investor materials identify NVIDIA as **NASDAQ: NVDA** and publish company financial information separately.

Official NVIDIA investor relations: https://investor.nvidia.com/

## Disclaimer

This is an educational data-analysis project. Market data can be delayed, incomplete, or temporarily unavailable. Nothing in this repository is financial advice or a recommendation to buy or sell securities.

## Author

**Magnw27** — Indonesia
