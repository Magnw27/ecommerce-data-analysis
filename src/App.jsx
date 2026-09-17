import { useEffect, useMemo, useState } from 'react'
import { Activity, ArrowDownRight, ArrowUpRight, BarChart3, CalendarDays, Database, Download, ExternalLink, Gauge, RefreshCw, Server, TrendingUp, Waves } from 'lucide-react'

const RANGES = ['1mo', '3mo', '6mo', '1y', '2y', '5y']
const money = value => value == null ? '—' : `$${Number(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
const compact = value => value == null ? '—' : Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(Number(value))
const pct = value => value == null || Number.isNaN(Number(value)) ? '—' : `${Number(value) >= 0 ? '+' : ''}${Number(value).toFixed(2)}%`

function sma(rows, window) {
  return rows.map((_, i) => {
    if (i < window - 1) return null
    const slice = rows.slice(i - window + 1, i + 1)
    return slice.reduce((sum, row) => sum + row.close, 0) / window
  })
}

function Chart({ rows, range }) {
  const width = 1000, height = 390, pad = { top: 24, right: 22, bottom: 34, left: 20 }
  const closes = rows.map(r => r.close)
  const ma20 = sma(rows, 20)
  const min = Math.min(...closes) * 0.985, max = Math.max(...closes) * 1.015
  const x = i => pad.left + (i / Math.max(rows.length - 1, 1)) * (width - pad.left - pad.right)
  const y = value => pad.top + ((max - value) / Math.max(max - min, 1)) * (height - pad.top - pad.bottom)
  const path = rows.map((r, i) => `${i ? 'L' : 'M'} ${x(i).toFixed(2)} ${y(r.close).toFixed(2)}`).join(' ')
  const maPath = ma20.filter(Boolean).map((v, j) => {
    const i = j + 19
    return `${j ? 'L' : 'M'} ${x(i).toFixed(2)} ${y(v).toFixed(2)}`
  }).join(' ')
  const area = `${path} L ${x(rows.length - 1)} ${height - pad.bottom} L ${x(0)} ${height - pad.bottom} Z`
  const ticks = [0, .25, .5, .75, 1]

  return <div className="chart-wrap">
    <svg viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" className="price-chart" role="img" aria-label={`NVDA ${range} price chart`}>
      <defs><linearGradient id="area" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopOpacity=".20"/><stop offset="100%" stopOpacity="0"/></linearGradient></defs>
      {ticks.map(t => <line key={t} x1={pad.left} x2={width-pad.right} y1={pad.top+t*(height-pad.top-pad.bottom)} y2={pad.top+t*(height-pad.top-pad.bottom)} className="grid-line" />)}
      <path d={area} fill="url(#area)" className="area-fill" />
      <path d={path} className="price-line" />
      {ma20.length > 20 && <path d={maPath} className="ma-line" />}
    </svg>
    <div className="chart-labels"><span>{new Date(rows[0].timestamp).toLocaleDateString()}</span><span>{new Date(rows.at(-1).timestamp).toLocaleDateString()}</span></div>
  </div>
}

function StatCard({ label, value, detail, icon: Icon, positive }) {
  return <article className="stat-card">
    <div className="stat-top"><span>{label}</span><Icon size={16} strokeWidth={1.7}/></div>
    <strong>{value}</strong>
    <small className={positive === true ? 'positive' : positive === false ? 'negative' : ''}>{detail}</small>
  </article>
}

export default function App() {
  const [range, setRange] = useState('6mo')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [lastRefresh, setLastRefresh] = useState(null)

  const load = async () => {
    setLoading(true); setError('')
    try {
      const response = await fetch(`/api/nvda?range=${range}&interval=1d`, { cache: 'no-store' })
      const json = await response.json()
      if (!response.ok) throw new Error(json.detail || json.error || 'Request failed')
      setData(json); setLastRefresh(new Date())
    } catch (err) { setError(err.message) }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [range])

  const stats = useMemo(() => {
    if (!data?.rows?.length) return null
    const rows = data.rows
    const latest = data.latest
    const returns = rows.slice(1).map((r, i) => ((r.close - rows[i].close) / rows[i].close) * 100)
    const recent = returns.slice(-20)
    const mean = recent.reduce((a,b) => a+b, 0) / Math.max(recent.length, 1)
    const volatility = Math.sqrt(recent.reduce((a,b) => a + (b-mean)**2, 0) / Math.max(recent.length - 1, 1))
    const high = Math.max(...rows.map(r => r.high))
    const low = Math.min(...rows.map(r => r.low))
    const avgVolume = rows.slice(-20).reduce((a,r) => a + r.volume, 0) / Math.min(rows.length, 20)
    return { latest, volatility, high, low, avgVolume, rows }
  }, [data])

  const downloadCsv = () => {
    if (!data?.rows) return
    const header = 'timestamp,open,high,low,close,volume\n'
    const body = data.rows.map(r => [r.timestamp,r.open,r.high,r.low,r.close,r.volume].join(',')).join('\n')
    const blob = new Blob([header + body], { type: 'text/csv' })
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `nvda-${range}.csv`; a.click(); URL.revokeObjectURL(a.href)
  }

  return <div className="app-shell">
    <header className="topbar">
      <a className="brand" href="/"><span className="brand-mark">N</span><span>MARKET<br/><b>LAB</b></span></a>
      <div className="top-meta"><span className="live-dot"/> LIVE DATA</div>
      <div className="top-actions"><button className="icon-btn" onClick={load} disabled={loading} title="Refresh"><RefreshCw size={17} className={loading ? 'spin' : ''}/></button><button className="download-btn" onClick={downloadCsv} disabled={!data}><Download size={16}/> Export CSV</button></div>
    </header>

    <main>
      <section className="hero">
        <div><div className="eyebrow">NASDAQ · NVIDIA CORPORATION · NVDA</div><h1>Market intelligence,<br/><em>without the noise.</em></h1><p>A focused analytics workspace for public NVIDIA market data, engineered for inspection rather than speculation.</p></div>
        <div className="hero-quote">{stats ? <><span>NVDA</span><strong>{money(stats.latest.close)}</strong><b className={stats.latest.changePct >= 0 ? 'positive' : 'negative'}>{pct(stats.latest.changePct)}</b><small>latest available close</small></> : <span className="skeleton large"/>}</div>
      </section>

      <section className="toolbar"><div className="range-tabs">{RANGES.map(r => <button key={r} className={range === r ? 'active' : ''} onClick={() => setRange(r)}>{r}</button>)}</div><div className="data-status"><Database size={14}/> <span>{loading ? 'Updating…' : error ? 'Data unavailable' : `Updated ${lastRefresh?.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}`}</span></div></section>

      {error && <div className="error-banner"><Activity size={17}/><span>{error}</span><button onClick={load}>Retry</button></div>}

      {stats && <>
        <section className="stats-grid">
          <StatCard label="Last close" value={money(stats.latest.close)} detail={`${stats.latest.change >= 0 ? '+' : ''}${money(stats.latest.change)} today`} positive={stats.latest.change >= 0} icon={TrendingUp}/>
          <StatCard label="20D volatility" value={`${stats.volatility.toFixed(2)}%`} detail="standard deviation of daily returns" icon={Waves}/>
          <StatCard label="20D avg volume" value={compact(stats.avgVolume)} detail="shares / session" icon={BarChart3}/>
          <StatCard label="Period range" value={money(stats.high)} detail={`high · low ${money(stats.low)}`} icon={Gauge}/>
        </section>

        <section className="panel chart-panel"><div className="panel-head"><div><span className="section-kicker">PRICE / MOVING AVERAGE</span><h2>Closing price</h2></div><div className="legend"><span><i className="legend-price"/> Close</span><span><i className="legend-ma"/> SMA 20</span></div></div><Chart rows={stats.rows} range={range}/></section>

        <section className="lower-grid">
          <div className="panel"><div className="panel-head compact-head"><div><span className="section-kicker">MARKET PROFILE</span><h2>Session snapshot</h2></div></div><div className="snapshot"><div><span>Open</span><b>{money(stats.latest.open)}</b></div><div><span>High</span><b>{money(stats.latest.high)}</b></div><div><span>Low</span><b>{money(stats.latest.low)}</b></div><div><span>Volume</span><b>{compact(stats.latest.volume)}</b></div></div></div>
          <div className="panel methodology"><div className="panel-head compact-head"><div><span className="section-kicker">PIPELINE</span><h2>Data lineage</h2></div></div><div className="pipeline"><div><span className="pipeline-icon"><Server size={15}/></span><p><b>Public quote endpoint</b><small>NVDA · OHLCV</small></p></div><span className="arrow">→</span><div><span className="pipeline-icon"><Database size={15}/></span><p><b>Normalize</b><small>timestamp · nulls</small></p></div><span className="arrow">→</span><div><span className="pipeline-icon"><BarChart3 size={15}/></span><p><b>Analyze</b><small>returns · SMA · σ</small></p></div></div></div>
        </section>

        <section className="panel observations"><div className="panel-head compact-head"><div><span className="section-kicker">LATEST OBSERVATIONS</span><h2>Raw OHLCV</h2></div><span className="row-count">{stats.rows.length} sessions</span></div><div className="table-scroll"><table><thead><tr><th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th><th>Move</th></tr></thead><tbody>{stats.rows.slice(-12).reverse().map((r, i, arr) => { const prev = arr[i+1] || r; const move = ((r.close-prev.close)/prev.close)*100; return <tr key={r.timestamp}><td>{new Date(r.timestamp).toLocaleDateString()}</td><td>{money(r.open)}</td><td>{money(r.high)}</td><td>{money(r.low)}</td><td className="close-cell">{money(r.close)}</td><td>{compact(r.volume)}</td><td className={move >= 0 ? 'positive' : 'negative'}>{pct(move)}</td></tr>})}</tbody></table></div></section>
      </>}

      {loading && !data && <div className="loading-state"><RefreshCw className="spin" size={20}/><span>Connecting to market data…</span></div>}

      <footer><span>MARKET LAB / MAGNW27</span><span>Public market data · Not financial advice</span><a href="https://www.nvidia.com/en-us/" target="_blank" rel="noreferrer">NVIDIA <ExternalLink size={12}/></a></footer>
    </main>
  </div>
}
