const YAHOO_URL = 'https://query1.finance.yahoo.com/v8/finance/chart/NVDA'

export default async function handler(req, res) {
  const url = new URL(YAHOO_URL)
  const range = ['1mo', '3mo', '6mo', '1y', '2y', '5y'].includes(req.query?.range) ? req.query.range : '6mo'
  const interval = ['1d', '1h', '5m'].includes(req.query?.interval) ? req.query.interval : '1d'

  url.searchParams.set('range', range)
  url.searchParams.set('interval', interval)
  url.searchParams.set('includePrePost', 'false')
  url.searchParams.set('events', 'div,splits')

  try {
    const response = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0 NVDA-Market-Analytics' },
    })
    if (!response.ok) throw new Error(`Upstream returned ${response.status}`)

    const payload = await response.json()
    const result = payload?.chart?.result?.[0]
    if (!result) throw new Error('No NVDA market data returned')

    const quote = result.indicators?.quote?.[0] ?? {}
    const timestamps = result.timestamp ?? []
    const rows = timestamps.map((timestamp, i) => ({
      timestamp: new Date(timestamp * 1000).toISOString(),
      open: quote.open?.[i] ?? null,
      high: quote.high?.[i] ?? null,
      low: quote.low?.[i] ?? null,
      close: quote.close?.[i] ?? null,
      volume: quote.volume?.[i] ?? null,
    })).filter(row => row.close != null)

    const latest = rows.at(-1)
    const previous = rows.at(-2) ?? latest
    const change = latest ? latest.close - previous.close : 0
    const changePct = previous?.close ? (change / previous.close) * 100 : 0

    res.setHeader('Cache-Control', 's-maxage=30, stale-while-revalidate=60')
    return res.status(200).json({
      ticker: 'NVDA',
      currency: result.meta?.currency ?? 'USD',
      exchange: result.meta?.exchangeName ?? 'NASDAQ',
      range,
      interval,
      updatedAt: new Date().toISOString(),
      latest: latest ? { ...latest, change, changePct } : null,
      rows,
    })
  } catch (error) {
    return res.status(502).json({ error: 'Unable to fetch NVDA market data', detail: error.message })
  }
}
