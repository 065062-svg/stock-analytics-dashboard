import streamlit as st
import pandas as pd
import yfinance as yf
import time
import plotly.graph_objects as go
import plotly.express as px

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StockSense Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── GLOBAL STYLES ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #080c14;
    color: #e2e8f0;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem; }

/* ── HEADER ── */
.dash-header {
    background: linear-gradient(135deg, #0d1526 0%, #0a1220 60%, #060d1a 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.dash-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(0,210,255,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.dash-header h1 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.2rem;
    background: linear-gradient(90deg, #00d2ff, #7b61ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.3rem;
    letter-spacing: -0.5px;
}
.dash-header p {
    color: #64748b;
    font-size: 0.9rem;
    margin: 0;
    font-family: 'Space Mono', monospace;
}

/* ── METRIC CARDS ── */
.metric-grid { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.metric-card {
    flex: 1;
    background: linear-gradient(145deg, #0d1526, #0a1220);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #00d2ff55; }
.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00d2ff, #7b61ff);
    opacity: 0.6;
}
.metric-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #00d2ff;
}
.metric-sub { font-size: 0.75rem; color: #475569; margin-top: 0.2rem; }

/* ── SECTION HEADERS ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 2rem 0 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid #1e3a5f;
}
.section-header h2 {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #cbd5e1;
    margin: 0;
}

/* ── FUNDAMENTAL TABLE ── */
.fund-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
    margin-top: 1rem;
}
.fund-table th {
    background: #0d1a2e;
    color: #64748b;
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 0.7rem;
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid #1e3a5f;
}
.fund-table td {
    padding: 0.85rem 1rem;
    border-bottom: 1px solid #0d1a2e;
    color: #cbd5e1;
}
.fund-table tr:hover td { background: #0d1526; }
.fund-table .stock-name {
    color: #00d2ff;
    font-weight: 700;
}
.fund-table .na-val { color: #334155; }
.fund-table .best-row td { background: #0a1f10 !important; }
.best-badge {
    display: inline-block;
    background: linear-gradient(90deg,#00c851,#00a040);
    color: #fff;
    font-size: 0.6rem;
    padding: 0.15rem 0.5rem;
    border-radius: 20px;
    margin-left: 0.5rem;
    letter-spacing: 0.5px;
    font-family: 'Syne', sans-serif;
}

/* ── SUGGESTION BANNER ── */
.suggest-banner {
    background: linear-gradient(135deg, #0a2010, #0d2a15);
    border: 1px solid #1a5c2a;
    border-left: 4px solid #00c851;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin-top: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: #86efac;
}
.suggest-banner strong { color: #4ade80; font-size: 1rem; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #060c18 !important;
    border-right: 1px solid #1e3a5f !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiselect label {
    color: #64748b !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'Space Mono', monospace !important;
}

/* ── WARNING / INFO ── */
.stAlert { border-radius: 10px; font-family: 'Space Mono', monospace; font-size: 0.8rem; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #00d2ff22, #7b61ff22) !important;
    border: 1px solid #00d2ff55 !important;
    color: #00d2ff !important;
    font-family: 'Space Mono', monospace !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #00d2ff44, #7b61ff44) !important;
    border-color: #00d2ff !important;
}

/* ── SLIDERS / SELECTS ── */
.stSlider > div > div { background: #1e3a5f !important; }
[data-baseweb="select"] { background: #0d1526 !important; }

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── PLOTLY DARK THEME ──────────────────────────────────────────────────────────
CHART_THEME = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Space Mono', color='#64748b', size=11),
    xaxis=dict(gridcolor='#1e3a5f', linecolor='#1e3a5f', tickcolor='#1e3a5f'),
    yaxis=dict(gridcolor='#1e3a5f', linecolor='#1e3a5f', tickcolor='#1e3a5f'),
    legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='#1e3a5f'),
    margin=dict(l=10, r=10, t=30, b=10),
)

CYAN  = '#00d2ff'
PURPLE= '#7b61ff'
GREEN = '#00c851'
AMBER = '#f59e0b'

# ─── DATA FUNCTIONS ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_stock_data(ticker):
    for _ in range(3):
        try:
            data = yf.download(ticker, start="2018-01-01", progress=False, threads=False)
            if not data.empty:
                data.columns = data.columns.get_level_values(0)
                return data
        except Exception:
            pass
        time.sleep(1)
    return None


@st.cache_data(ttl=1800)
def get_fundamentals(ticker):
    """
    Robust fundamentals fetch with multiple fallbacks.
    Priority: fast_info → info → computed from history
    """
    try:
        stock = yf.Ticker(ticker)

        # ── 1. History (most reliable) ──────────────────
        hist = stock.history(period="1y")
        high_52w = round(hist["High"].max(), 2) if not hist.empty else None
        low_52w  = round(hist["Low"].min(),  2) if not hist.empty else None

        # ── 2. fast_info (lightweight, rarely fails) ────
        try:
            fi = stock.fast_info
            market_cap = getattr(fi, "market_cap",  None)
            pe_ratio   = getattr(fi, "pe_ratio",    None)   # may be absent
        except Exception:
            market_cap = pe_ratio = None

        # ── 3. info (heavier, sometimes blocked) ────────
        try:
            info = stock.info
        except Exception:
            info = {}

        # Fallback chain for each field
        if not market_cap:
            market_cap = info.get("marketCap") or info.get("enterpriseValue")
        if not pe_ratio:
            pe_ratio = info.get("trailingPE") or info.get("forwardPE")

        dividend = info.get("dividendYield") or info.get("trailingAnnualDividendYield")
        beta      = info.get("beta")
        sector    = info.get("sector", "—")

        # ── 4. Compute PE from history if still missing ─
        if pe_ratio is None and not hist.empty:
            eps = info.get("trailingEps")
            if eps and eps > 0 and high_52w:
                pe_ratio = round(hist["Close"].iloc[-1] / eps, 2)

        # ── Format ──────────────────────────────────────
        def fmt_cap(v):
            if v is None: return None
            v = float(v)
            if v >= 1e12: return f"₹{v/1e12:.2f}T"
            if v >= 1e9:  return f"₹{v/1e9:.2f}B"
            if v >= 1e7:  return f"₹{v/1e7:.2f}Cr"
            return f"₹{v:,.0f}"

        return {
            "Market Cap":      fmt_cap(market_cap),
            "PE Ratio":        round(float(pe_ratio), 2) if pe_ratio else None,
            "Dividend Yield":  f"{round(float(dividend)*100,2)}%" if dividend else None,
            "Beta":            round(float(beta), 2) if beta else None,
            "52W High":        f"₹{high_52w}" if high_52w else None,
            "52W Low":         f"₹{low_52w}"  if low_52w  else None,
            "Sector":          sector,
        }
    except Exception as e:
        return None


# ─── STOCK LIST ─────────────────────────────────────────────────────────────────
BSE100 = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "LT.NS","ITC.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS",
    "HINDUNILVR.NS","BHARTIARTL.NS","ASIANPAINT.NS","BAJFINANCE.NS",
    "MARUTI.NS","TITAN.NS","SUNPHARMA.NS","ULTRACEMCO.NS",
    "WIPRO.NS","HCLTECH.NS","POWERGRID.NS","NTPC.NS",
    "ONGC.NS","COALINDIA.NS","ADANIENT.NS","ADANIPORTS.NS",
    "JSWSTEEL.NS","TATASTEEL.NS","GRASIM.NS","BAJAJFINSV.NS",
    "NESTLEIND.NS","HDFCLIFE.NS","SBILIFE.NS","BRITANNIA.NS",
    "EICHERMOT.NS","TATAMOTORS.NS","HEROMOTOCO.NS",
    "BAJAJ-AUTO.NS","DIVISLAB.NS","DRREDDY.NS",
    "APOLLOHOSP.NS","CIPLA.NS","BPCL.NS","IOC.NS",
    "GAIL.NS","INDUSINDBK.NS","TECHM.NS","ADANIGREEN.NS",
    "ADANITRANS.NS","TATACONSUM.NS","DABUR.NS","COLPAL.NS",
    "PIDILITIND.NS","AMBUJACEM.NS","ACC.NS","HAL.NS",
    "IRCTC.NS","ZOMATO.NS","NYKAA.NS","DMART.NS",
]
STOCKS = {s.replace(".NS", ""): s for s in BSE100}

# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:1rem 0 1.5rem;'>
        <div style='font-family:Syne,sans-serif;font-weight:800;font-size:1.3rem;
                    background:linear-gradient(90deg,#00d2ff,#7b61ff);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
            StockSense Pro
        </div>
        <div style='font-family:Space Mono,monospace;font-size:0.65rem;color:#334155;margin-top:0.2rem;'>
            NSE · REAL-TIME ANALYTICS
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected_stock = st.selectbox("Primary Stock", list(STOCKS.keys()))
    compare_stocks = st.multiselect("Compare With", list(STOCKS.keys()))
    st.markdown("---")

ticker = STOCKS[selected_stock]

# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
    <h1>📈 StockSense Pro</h1>
    <p>NSE · Indian Equity Analytics & Forecasting Platform · {selected_stock}</p>
</div>
""", unsafe_allow_html=True)

# ─── LOAD MAIN DATA ──────────────────────────────────────────────────────────────
data = load_stock_data(ticker)
if data is None:
    st.warning("⚠️ Data temporarily unavailable. Please try refreshing.")
    st.stop()

cur  = round(float(data["Close"].iloc[-1]), 2)
high = round(float(data["High"].max()), 2)
low  = round(float(data["Low"].min()), 2)
vol  = int(data["Volume"].iloc[-1]) if "Volume" in data.columns else 0
chg  = round(float(data["Close"].iloc[-1] - data["Close"].iloc[-2]), 2)
chg_pct = round(chg / float(data["Close"].iloc[-2]) * 100, 2)
chg_color = "#00c851" if chg >= 0 else "#ef4444"
chg_sign  = "▲" if chg >= 0 else "▼"

# ── Metric cards ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-label">Current Price</div>
    <div class="metric-value">₹{cur:,}</div>
    <div class="metric-sub" style="color:{chg_color};">{chg_sign} {abs(chg)} ({chg_pct}%)</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">52-Week High</div>
    <div class="metric-value" style="color:#f59e0b;">₹{high:,}</div>
    <div class="metric-sub">All-time in dataset</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">52-Week Low</div>
    <div class="metric-value" style="color:#7b61ff;">₹{low:,}</div>
    <div class="metric-sub">All-time in dataset</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Volume (Last Session)</div>
    <div class="metric-value" style="font-size:1.2rem;">{vol:,}</div>
    <div class="metric-sub">Shares traded</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── PRICE CHART ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h2>📈 Price Trend</h2></div>', unsafe_allow_html=True)

fig_price = go.Figure()
fig_price.add_trace(go.Scatter(
    x=data.index, y=data["Close"],
    mode='lines', name='Close',
    line=dict(color=CYAN, width=1.5),
    fill='tozeroy',
    fillcolor='rgba(0,210,255,0.04)'
))
fig_price.update_layout(**CHART_THEME, height=320)
st.plotly_chart(fig_price, use_container_width=True)

# ─── MOVING AVERAGES ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h2>📊 Moving Averages</h2></div>', unsafe_allow_html=True)

data["MA50"]  = data["Close"].rolling(50).mean()
data["MA200"] = data["Close"].rolling(200).mean()

fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(x=data.index, y=data["Close"],  name='Close', line=dict(color=CYAN,   width=1.2)))
fig_ma.add_trace(go.Scatter(x=data.index, y=data["MA50"],   name='MA50',  line=dict(color=AMBER,  width=1.5, dash='dot')))
fig_ma.add_trace(go.Scatter(x=data.index, y=data["MA200"],  name='MA200', line=dict(color=PURPLE, width=1.5, dash='dash')))
fig_ma.update_layout(**CHART_THEME, height=300)
st.plotly_chart(fig_ma, use_container_width=True)

# ─── RSI ─────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h2>⚡ RSI Indicator (14)</h2></div>', unsafe_allow_html=True)

delta    = data["Close"].diff()
gain     = delta.clip(lower=0).rolling(14).mean()
loss     = (-delta.clip(upper=0)).rolling(14).mean()
data["RSI"] = 100 - (100 / (1 + gain / loss))

fig_rsi = go.Figure()
fig_rsi.add_hrect(y0=70, y1=100, fillcolor="rgba(239,68,68,0.07)", line_width=0)
fig_rsi.add_hrect(y0=0,  y1=30,  fillcolor="rgba(0,200,81,0.07)",  line_width=0)
fig_rsi.add_hline(y=70, line_dash="dot", line_color="#ef4444", line_width=1, annotation_text="Overbought", annotation_position="right")
fig_rsi.add_hline(y=30, line_dash="dot", line_color="#00c851", line_width=1, annotation_text="Oversold",   annotation_position="right")
fig_rsi.add_trace(go.Scatter(x=data.index, y=data["RSI"], name='RSI', line=dict(color=PURPLE, width=1.5)))
fig_rsi.update_layout(**CHART_THEME, height=250, yaxis=dict(range=[0, 100], **CHART_THEME["yaxis"]))
st.plotly_chart(fig_rsi, use_container_width=True)

# ─── FORECAST ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h2>🔮 Price Forecast (Trend Model)</h2></div>', unsafe_allow_html=True)

forecast_years = st.slider("Forecast Horizon (Years)", 1, 5, 2)
df_f = data.reset_index()[["Date", "Close"]].copy()
slope = (float(df_f["Close"].iloc[-1]) - float(df_f["Close"].iloc[0])) / len(df_f)
future_days   = 365 * forecast_years
future_dates  = pd.date_range(start=df_f["Date"].iloc[-1], periods=future_days + 1)[1:]
future_prices = [float(df_f["Close"].iloc[-1]) + slope * i for i in range(1, future_days + 1)]

fig_fc = go.Figure()
fig_fc.add_trace(go.Scatter(
    x=df_f["Date"], y=df_f["Close"],
    name='Historical', line=dict(color=CYAN, width=1.2)
))
fig_fc.add_trace(go.Scatter(
    x=future_dates, y=future_prices,
    name='Forecast', line=dict(color=AMBER, width=2, dash='dot'),
    fill='tonexty', fillcolor='rgba(245,158,11,0.05)'
))
fig_fc.update_layout(**CHART_THEME, height=320)
st.plotly_chart(fig_fc, use_container_width=True)

# ─── MULTI-STOCK COMPARISON ───────────────────────────────────────────────────────
if compare_stocks:
    st.markdown('<div class="section-header"><h2>🔄 Normalised Performance Comparison</h2></div>', unsafe_allow_html=True)
    compare_df = pd.DataFrame()
    colors_pool = [CYAN, PURPLE, GREEN, AMBER, '#f43f5e']
    fig_cmp = go.Figure()
    for i, stock in enumerate(compare_stocks):
        df = load_stock_data(STOCKS[stock])
        if df is None: continue
        normalized = df["Close"] / float(df["Close"].iloc[0]) * 100
        fig_cmp.add_trace(go.Scatter(
            x=df.index, y=normalized, name=stock,
            line=dict(color=colors_pool[i % len(colors_pool)], width=1.5)
        ))
    fig_cmp.update_layout(**CHART_THEME, height=320)
    st.plotly_chart(fig_cmp, use_container_width=True)

# ─── FUNDAMENTALS COMPARISON ─────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h2>📋 Fundamentals Comparison</h2></div>', unsafe_allow_html=True)
st.caption("ℹ️ Data fetched via yfinance with fast_info → info → history fallback chain. Some fields may be unavailable for a few tickers.")

compare_table = st.multiselect(
    "Select stocks to compare",
    list(STOCKS.keys()),
    key="fund_compare"
)

if compare_table:
    fundamentals = []
    progress = st.progress(0, text="Fetching fundamentals…")

    for idx, stock in enumerate(compare_table):
        time.sleep(0.4)
        info = get_fundamentals(STOCKS[stock])
        if info is None:
            info = {k: None for k in ["Market Cap","PE Ratio","Dividend Yield","Beta","52W High","52W Low","Sector"]}
        fundamentals.append({"Stock": stock, **info})
        progress.progress((idx + 1) / len(compare_table), text=f"Loaded {stock}…")

    progress.empty()
    df_fund = pd.DataFrame(fundamentals)

    # ── Score each stock ──────────────────────────────────────────────────────
    df_score = df_fund.copy()

    def safe_pe(v):
        try: return float(str(v).replace("N/A","")) if v else 100
        except: return 100
    def safe_div(v):
        try: return float(str(v).replace("%","")) / 100 if v else 0
        except: return 0
    def safe_beta(v):
        try: return float(v) if v else 1
        except: return 1

    df_score["_pe"]   = df_score["PE Ratio"].apply(safe_pe)
    df_score["_div"]  = df_score["Dividend Yield"].apply(safe_div)
    df_score["_beta"] = df_score["Beta"].apply(safe_beta)
    df_score["_score"] = (
        0.4 / df_score["_pe"].replace(0, 999) +
        0.3 * df_score["_div"] +
        0.3 / df_score["_beta"].replace(0, 1)
    )
    best_stock = df_score.sort_values("_score", ascending=False).iloc[0]["Stock"]

    # ── Render custom HTML table ─────────────────────────────────────────────
    FIELDS = ["Market Cap","PE Ratio","Dividend Yield","Beta","52W High","52W Low","Sector"]
    rows_html = ""
    for _, row in df_fund.iterrows():
        is_best = row["Stock"] == best_stock
        row_cls = 'class="best-row"' if is_best else ""
        badge   = '<span class="best-badge">BEST</span>' if is_best else ""
        cells   = f'<td class="stock-name">{row["Stock"]}{badge}</td>'
        for field in FIELDS:
            val = row.get(field)
            if val is None or str(val) in ("None","nan",""):
                cells += '<td class="na-val">—</td>'
            else:
                cells += f"<td>{val}</td>"
        rows_html += f"<tr {row_cls}>{cells}</tr>"

    headers = "".join(f"<th>{f}</th>" for f in ["Stock"] + FIELDS)

    st.markdown(f"""
    <div style="overflow-x:auto;border:1px solid #1e3a5f;border-radius:12px;background:#0a1220;padding:0.5rem;">
        <table class="fund-table">
            <thead><tr>{headers}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="suggest-banner">
        ⭐&nbsp;&nbsp;Suggested stock among selected: <strong>{best_stock}</strong>
        &nbsp;·&nbsp; Based on PE ratio, dividend yield & beta weighting
    </div>
    """, unsafe_allow_html=True)

# ─── PORTFOLIO BUILDER ───────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h2>🤖 Smart Portfolio Builder</h2></div>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)
with col_a:
    investment_amount = st.number_input("Total Investment (₹)", 1000, 10_000_000, 100_000, step=10_000)
with col_b:
    risk_level = st.selectbox("Risk Appetite", ["Low Risk", "Moderate Risk", "High Risk"])
with col_c:
    years = st.slider("Investment Horizon (Years)", 1, 10, 5)

if st.button("🚀 Generate Portfolio"):
    portfolio = []
    pb = st.progress(0, text="Scanning stocks…")
    for idx, stock in enumerate(BSE100):
        df = load_stock_data(stock)
        pb.progress((idx+1)/len(BSE100), text=f"Analyzing {stock.replace('.NS','')}…")
        if df is None: continue
        vol_val = float(df["Close"].pct_change().std())
        portfolio.append({"Stock": stock.replace(".NS",""), "Volatility": vol_val})
    pb.empty()

    df_port = pd.DataFrame(portfolio)
    thresholds = {"Low Risk": 0.02, "Moderate Risk": 0.035, "High Risk": 999}
    df_port = df_port[df_port["Volatility"] < thresholds[risk_level]].sort_values("Volatility").head(5)

    if df_port.empty:
        st.warning("No stocks matched the selected risk level.")
    else:
        alloc = round(investment_amount / len(df_port), 2)
        df_port["Allocation (₹)"] = alloc
        df_port["Volatility"] = df_port["Volatility"].apply(lambda x: f"{x:.4f}")
        st.dataframe(df_port.reset_index(drop=True), use_container_width=True)
        st.markdown(f"""
        <div class="suggest-banner">
            💰 Suggested allocation per stock: <strong>₹{alloc:,}</strong>
            &nbsp;·&nbsp; {risk_level} · {years}-year horizon
        </div>
        """, unsafe_allow_html=True)








































