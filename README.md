# NVIDIA Market Lab

A modular market-data engineering and analytics project for **NVIDIA Corporation (NASDAQ: NVDA)**. It combines a Python analytics pipeline with a React/Vite dashboard and a **Python Vercel Function** for the live data layer.

> **Data note:** this project uses publicly available market data. It is not NVIDIA internal/private data. Quote freshness depends on the upstream provider and may be delayed or unavailable. Nothing here is financial advice.

## Architecture

```text
                 PUBLIC NVDA DATA
                       │
                       ▼
              ┌─────────────────┐
              │ Vercel Python   │
              │ /api/nvda.py    │
              └────────┬────────┘
                       │ JSON
                       ▼
              ┌─────────────────┐
              │ React + Vite    │
              │ Market Lab UI   │
              └─────────────────┘

        Offline / scheduled analytics
                       │
                       ▼
              ┌─────────────────┐
              │ analytics/*.py  │
              │ fetch → features│
              │ → metrics       │
              └────────┬────────┘
                       ▼
                 data/*.csv
```

## Repository structure

```text
ecommerce-data-analysis/
├── api/
│   └── nvda.py                 # Vercel Python Function
├── analytics/
│   ├── __init__.py
│   ├── config.py               # shared configuration
│   ├── data_loader.py          # validation + normalization
│   ├── fetch_nvda.py           # OHLCV ingestion
│   ├── features.py             # feature engineering
│   ├── metrics.py              # summary statistics
│   └── analyze.py              # pipeline CLI
├── src/
│   ├── App.jsx                 # React dashboard
│   ├── main.jsx                # React entry point
│   └── styles.css              # responsive design system
├── data/
│   └── .gitkeep
├── .github/workflows/
│   └── validate.yml            # scheduled Python validation
├── dashboard.py                # optional Streamlit dashboard
├── index.html
├── package.json
├── vite.config.js
├── vercel.json
├── requirements.txt
├── .gitignore
└── README.md
```

## Dashboard preview

The production-facing preview remains **React/Vite**. It includes:

- live public NVDA OHLCV data through `/api/nvda`
- 1mo / 3mo / 6mo / 1y / 2y / 5y ranges
- closing-price chart with SMA 20
- daily change, volatility, volume and period range metrics
- session OHLCV snapshot
- latest observation table
- browser CSV export
- data-lineage panel
- responsive mobile/tablet/desktop layout
- no API key in browser code
- restrained motion and information-first visual hierarchy

### Local frontend

```bash
npm install
npm run dev
```

Production preview:

```bash
npm run build
npm run preview
```

## Python analytics

```bash
python -m pip install -r requirements.txt
python -m analytics.fetch_nvda --period 1y --interval 1d
python -m analytics.analyze
```

Generated datasets:

```text
data/nvda.csv
data/nvda_processed.csv
```

## Feature layer

| Feature | Description |
|---|---|
| `return_pct` | session-to-session percentage return |
| `log_return` | logarithmic return |
| `sma_20` | 20-session simple moving average |
| `sma_50` | 50-session simple moving average |
| `ema_20` | 20-session exponential moving average |
| `volatility_20` | rolling standard deviation of daily returns |
| `range_pct` | high-low range relative to close |
| `volume_sma_20` | 20-session average volume |
| `drawdown_pct` | drawdown from running close high |

## Vercel deployment

Deploy from the repository root with:

```text
Build Command: npm run build
Output Directory: dist
```

The important split is:

```text
React/Vite → static dashboard
api/nvda.py → Python serverless API
```

The dashboard calls `/api/nvda`, and the Python function fetches the public upstream market-data endpoint. The frontend never needs a provider API key.

If the Vercel dashboard asks for a framework preset, the Python function is already defined by `api/nvda.py`; the frontend still uses the normal Vite build command and `dist` output configured in `vercel.json`.

## CI

GitHub Actions validates the Python pipeline on pushes, pull requests, manual runs and a six-hour schedule. It installs dependencies, downloads a fresh NVDA sample, runs feature engineering and validates the processed schema.

## Data source

The ingestion layer uses the public Yahoo Finance chart endpoint for `NVDA`. NVIDIA corporate information should be checked against NVIDIA's official investor-relations resources.

## Design principles

The UI is intentionally designed as a focused market workspace rather than a generic AI dashboard:

- restrained motion instead of decorative effects
- compact but readable information density
- clear numerical hierarchy
- explicit data provenance
- responsive layout without a separate mobile codebase
- lightweight SVG/CSS visualization
- modular Python and frontend layers

## Disclaimer

Educational and portfolio project only. Public market data can be delayed, incomplete, rate-limited or temporarily unavailable. This project does not provide investment advice or recommendations.

## Author

**Magnw27** · Indonesia
