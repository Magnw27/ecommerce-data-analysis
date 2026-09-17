# NVIDIA Market Lab

A modular market-data engineering and analytics project for **NVIDIA Corporation (NASDAQ: NVDA)**. The repository combines a Python analytics pipeline with a production-ready Vite + React dashboard served through Vercel.

> **Data note:** this project uses publicly available market data. It is not NVIDIA internal/private data. Quote freshness depends on the upstream provider and may be delayed or unavailable. Nothing here is financial advice.

## Architecture

```text
PUBLIC NVDA MARKET DATA
          │
     ┌────┴─────┐
     │          │
 Python       Vercel
 pipeline       API
     │          │
     │       /api/nvda
     │          │
     └────┬─────┘
          │
   React / Vite UI
          │
     Market Lab
```

## Repository structure

```text
ecommerce-data-analysis/
├── api/
│   └── nvda.js                 # Vercel serverless proxy
├── analytics/
│   ├── __init__.py
│   ├── config.py               # shared configuration
│   ├── data_loader.py          # validation + normalization
│   ├── fetch_nvda.py           # OHLCV ingestion
│   ├── features.py             # feature engineering
│   ├── metrics.py              # summary statistics
│   └── analyze.py              # pipeline CLI
├── src/
│   ├── App.jsx                 # React application
│   ├── main.jsx                # React entry point
│   └── styles.css              # responsive design system
├── data/
│   └── .gitkeep
├── .github/workflows/
│   └── validate.yml            # scheduled Python validation
├── dashboard.py                # optional Streamlit dashboard
├── index.html                  # Vite entry document
├── package.json                # frontend dependencies/scripts
├── vite.config.js              # Vite configuration
├── vercel.json                 # Vercel SPA routing
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

## Web dashboard

The main preview is the React/Vite dashboard.

### Included

- Public NVDA OHLCV data through a server-side Vercel proxy
- 1mo / 3mo / 6mo / 1y / 2y / 5y history
- Closing-price chart with SMA 20
- Daily change, volatility, volume and period range metrics
- Open / high / low / volume session snapshot
- Raw OHLCV observation table
- Browser CSV export
- Explicit data-lineage view
- Responsive mobile/tablet/desktop layout
- No browser-side API secret
- Minimal, information-first market-terminal visual language

### Local preview

```bash
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`.

Production build:

```bash
npm run build
npm run preview
```

## Python analytics

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Fetch data:

```bash
python -m analytics.fetch_nvda --period 1y --interval 1d
```

Engineer features:

```bash
python -m analytics.analyze
```

Generated files:

```text
data/nvda.csv
data/nvda_processed.csv
```

CSV output is ignored by Git to keep the repository source-first.

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

Each layer has a single responsibility so the same functions can be reused by scripts, notebooks, Streamlit and future APIs.

## Vercel

The project is structured for deployment from the repository root:

```text
Build command: npm run build
Output: dist
```

Vercel serves the Vite application and exposes `api/nvda.js` as a serverless function. The browser calls `/api/nvda`, while the serverless function calls the public upstream market-data endpoint. This avoids exposing provider-specific configuration in frontend code.

No NVIDIA API key is required by the current implementation.

## CI

GitHub Actions runs on pushes, pull requests, manual dispatch and every six hours. It installs Python dependencies, downloads a fresh NVDA sample, runs feature engineering and verifies the resulting schema.

## Data source

The ingestion layer uses the public Yahoo Finance chart endpoint for ticker `NVDA`. For authoritative NVIDIA corporate financial information, use NVIDIA's official investor-relations resources.

## Design principles

This is deliberately **not** a generic AI-generated dashboard. The interface favors:

- restrained motion instead of decorative animation
- compact information density
- readable numerical hierarchy
- clear provenance and data lineage
- responsive behavior without a separate mobile UI
- CSS/SVG visuals instead of a heavy charting/UI framework

## Disclaimer

Educational and portfolio project only. Public market data can be delayed, incomplete, rate-limited or temporarily unavailable. This project does not provide investment advice or recommendations.

## Author

**Magnw27** · Indonesia
