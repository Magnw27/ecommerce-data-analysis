# NVIDIA Market Lab

A modular market-data engineering and analytics project for **NVIDIA Corporation (NASDAQ: NVDA)**, built as a portfolio-grade data pipeline with a Vite + React dashboard and a Python analysis layer.

The project is intentionally split into two surfaces:

- **Python analytics** — ingestion, validation, feature engineering, statistics and scheduled validation.
- **Web dashboard** — a fast React/Vite interface that reads fresh public NVDA market data through a Vercel serverless API proxy.

> **Data note:** this project uses publicly available market data. It is not NVIDIA internal/private data. Quote freshness depends on the upstream provider and may be delayed or unavailable. Nothing here is financial advice.

## Architecture

```text
                 PUBLIC NVDA MARKET DATA
                           │
             ┌─────────────┴─────────────┐
             │                           │
        Python pipeline              Vercel API
             │                           │
      fetch → validate              /api/nvda
             │                           │
        feature layer                    │
             │                           │
       CSV / statistics          React dashboard
             │                           │
             └─────────────┬─────────────┘
                           │
                     Market Lab UI
```

## Repository structure

```text
ecommerce-data-analysis/
├── api/
│   └── nvda.js                 # Vercel serverless market-data proxy
│
├── src/
│   ├── __init__.py
│   ├── config.py               # shared paths, ticker and API configuration
│   ├── data_loader.py          # schema validation, typing and de-duplication
│   ├── fetch_nvda.py           # public OHLCV ingestion
│   ├── features.py             # returns, SMA, EMA, volatility, drawdown
│   ├── metrics.py              # reusable summary metrics
│   └── analyze.py              # Python CLI entry point
│
├── data/
│   └── .gitkeep
│
├── .github/workflows/
│   └── validate.yml            # scheduled pipeline validation
│
├── src/
│   ├── App.jsx                 # dashboard application
│   ├── main.jsx                # React entry point
│   └── styles.css              # responsive visual system
│
├── dashboard.py                # optional Streamlit analysis dashboard
├── index.html
├── package.json
├── vite.config.js
├── vercel.json
├── requirements.txt
├── .gitignore
└── README.md
```

## Web dashboard

The primary preview is the React/Vite application.

### Features

- Fresh NVDA OHLCV requests through `/api/nvda`
- 1mo / 3mo / 6mo / 1y / 2y / 5y history controls
- Close price and SMA 20 visualization
- Daily move, volatility and volume metrics
- Session open/high/low/volume snapshot
- Raw latest-observation table
- CSV export directly from the browser
- Explicit data-lineage panel
- Responsive layout for mobile, tablet and desktop
- No client-side API secret required
- Vercel-compatible serverless API proxy

### Local web preview

```bash
npm install
npm run dev
```

Then open the Vite URL shown in the terminal, normally:

```text
http://localhost:5173
```

For a production build:

```bash
npm run build
npm run preview
```

## Python pipeline

Install the analytics dependencies:

```bash
python -m pip install -r requirements.txt
```

Fetch public NVDA candles:

```bash
python -m src.fetch_nvda --period 1y --interval 1d
```

Build the processed dataset:

```bash
python -m src.analyze
```

The pipeline produces:

```text
data/nvda.csv

data/nvda_processed.csv
```

Generated CSV files are intentionally ignored by Git so the repository remains source-first.

## Analytics layer

The feature module currently calculates:

| Feature | Meaning |
|---|---|
| `return_pct` | percentage change between sessions |
| `log_return` | logarithmic return |
| `sma_20` | 20-session simple moving average |
| `sma_50` | 50-session simple moving average |
| `ema_20` | 20-session exponential moving average |
| `volatility_20` | rolling standard deviation of daily returns |
| `range_pct` | high-low range relative to close |
| `volume_sma_20` | 20-session average volume |
| `drawdown_pct` | decline from the running close high |

The functions are deliberately reusable so notebooks, scripts and future APIs can share the same analytical logic.

## Vercel deployment

The repository is structured for a normal Vercel deployment:

1. Import `Magnw27/ecommerce-data-analysis` into Vercel.
2. Use the repository root as the project root.
3. Let Vercel detect the Vite application.
4. Build command: `npm run build`.
5. Output directory: `dist`.
6. The `/api/nvda` function proxies public market-data requests server-side.

No NVIDIA API key is required by the current public-data implementation.

## CI validation

GitHub Actions validates the Python pipeline on pushes, pull requests, manual runs and a scheduled six-hour interval. The workflow fetches a fresh sample, builds features and checks that the expected analytical columns exist.

## Data source

The market ingestion layer uses the public Yahoo Finance chart endpoint for ticker `NVDA`. NVIDIA's official investor-relations material should be used when authoritative company financial information is required.

## Design direction

The web interface avoids generic dashboard patterns such as excessive gradients, oversized cards and decorative animations. It uses a restrained dark market-terminal aesthetic, compact typography, visible data lineage and a strong information hierarchy so the data remains the visual focus.

## Disclaimer

Educational and portfolio project only. Public market data may be delayed, incomplete, rate-limited or temporarily unavailable. This project does not provide investment advice or recommendations.

## Author

**Magnw27** · Indonesia
