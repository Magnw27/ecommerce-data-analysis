from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.fetch_nvda import fetch_nvda  # noqa: E402
from src.analyze import build_features  # noqa: E402

st.set_page_config(page_title="NVDA Data Analytics", page_icon="◈", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1400px; padding-top: 2rem;}
.hero {padding: 1.4rem 1.6rem; border: 1px solid rgba(255,255,255,.10); border-radius: 22px;
       background: linear-gradient(135deg, rgba(118,185,0,.16), rgba(20,25,35,.70)); margin-bottom: 1rem;}
.hero h1 {margin: 0; font-size: 2.4rem;}
.hero p {opacity: .72; margin: .35rem 0 0;}
[data-testid="stMetric"] {border: 1px solid rgba(255,255,255,.08); padding: 14px; border-radius: 16px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>NVDA Market Analytics</h1><p>Public NVIDIA market data • refreshed on demand • analytical, not financial advice</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Data controls")
    period = st.selectbox("History", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    refresh = st.button("Refresh market data", use_container_width=True)
    st.caption("The upstream quote source may be delayed or temporarily unavailable.")

@st.cache_data(ttl=60, show_spinner=False)
def load_data(selected_period: str) -> pd.DataFrame:
    return build_features(fetch_nvda(selected_period, "1d"))

try:
    if refresh:
        st.cache_data.clear()
    df = load_data(period)
except Exception as exc:
    st.error(f"Could not fetch NVDA data: {exc}")
    st.stop()

latest = df.iloc[-1]
previous = df.iloc[-2] if len(df) > 1 else latest
change = float(latest["close"] - previous["close"])
change_pct = float(latest["return_pct"]) if pd.notna(latest["return_pct"]) else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("NVDA close", f"${latest['close']:,.2f}", f"{change:+.2f} ({change_pct:+.2f}%)")
m2.metric("Volume", f"{latest['volume']:,.0f}")
m3.metric("SMA 20", f"${latest['sma_20']:,.2f}")
m4.metric("20D volatility", f"{latest['volatility_20']:.2f}%" if pd.notna(latest['volatility_20']) else "—")

st.subheader("Price trend")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["datetime"], y=df["close"], name="Close", mode="lines", line={"width": 2}))
fig.add_trace(go.Scatter(x=df["datetime"], y=df["sma_20"], name="SMA 20", mode="lines", line={"width": 1.5}))
fig.add_trace(go.Scatter(x=df["datetime"], y=df["sma_50"], name="SMA 50", mode="lines", line={"width": 1.5}))
fig.update_layout(height=430, margin=dict(l=10, r=10, t=20, b=10), hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Daily returns")
    returns = go.Figure(go.Bar(x=df["datetime"], y=df["return_pct"], name="Return"))
    returns.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(returns, use_container_width=True)
with right:
    st.subheader("Volume")
    volume = go.Figure(go.Bar(x=df["datetime"], y=df["volume"], name="Volume"))
    volume.update_layout(height=320, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(volume, use_container_width=True)

st.subheader("Latest observations")
st.dataframe(
    df.tail(15).sort_values("datetime", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.caption(f"Latest observation: {latest['datetime']} • Rows analyzed: {len(df):,}")
