from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import json
from urllib.request import Request, urlopen

YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/NVDA"
ALLOWED_RANGES = {"1mo", "3mo", "6mo", "1y", "2y", "5y"}
ALLOWED_INTERVALS = {"1d", "1h", "5m"}


def fetch_nvda(range_name: str, interval: str):
    url = (
        f"{YAHOO_URL}?range={range_name}&interval={interval}"
        "&includePrePost=false&events=div%2Csplits"
    )
    request = Request(url, headers={"User-Agent": "Magnw27-NVDA-Market-Lab/3.0"})
    with urlopen(request, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))

    result = (payload.get("chart", {}).get("result") or [None])[0]
    if not result:
        raise RuntimeError("No NVDA market data returned")

    quote = (result.get("indicators", {}).get("quote") or [{}])[0]
    timestamps = result.get("timestamp") or []
    rows = []
    opens = quote.get("open") or []
    highs = quote.get("high") or []
    lows = quote.get("low") or []
    closes = quote.get("close") or []
    volumes = quote.get("volume") or []

    for i, timestamp in enumerate(timestamps):
        close = closes[i] if i < len(closes) else None
        if close is None:
            continue
        rows.append({
            "timestamp": timestamp,
            "open": opens[i] if i < len(opens) else None,
            "high": highs[i] if i < len(highs) else None,
            "low": lows[i] if i < len(lows) else None,
            "close": close,
            "volume": volumes[i] if i < len(volumes) else None,
        })

    latest = rows[-1] if rows else None
    previous = rows[-2] if len(rows) > 1 else latest
    change = 0
    change_pct = 0
    if latest and previous and previous.get("close"):
        change = latest["close"] - previous["close"]
        change_pct = (change / previous["close"]) * 100

    return {
        "ticker": "NVDA",
        "currency": result.get("meta", {}).get("currency", "USD"),
        "exchange": result.get("meta", {}).get("exchangeName", "NASDAQ"),
        "range": range_name,
        "interval": interval,
        "latest": {**latest, "change": change, "changePct": change_pct} if latest else None,
        "rows": rows,
    }


class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "s-maxage=30, stale-while-revalidate=60")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            range_name = query.get("range", ["6mo"])[0]
            interval = query.get("interval", ["1d"])[0]
            if range_name not in ALLOWED_RANGES:
                range_name = "6mo"
            if interval not in ALLOWED_INTERVALS:
                interval = "1d"
            self._send(200, fetch_nvda(range_name, interval))
        except Exception as exc:
            self._send(502, {"error": "Unable to fetch NVDA market data", "detail": str(exc)})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
