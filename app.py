import streamlit as st
import pandas as pd
import yfinance as yf
import time
import plotly.express as px
from prophet import Prophet


# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Stock Analytics Dashboard", layout="wide")


# ---------- VISUAL THEME ----------
st.markdown("""
<style>

/* Main background */
.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
}

/* Title */
h1 {
    text-align:center;
    color:#00ffd5;
    font-size:42px;
}

/* Section headings */
h2, h3 {
    color:#00ffd5 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color:#111;
}

section[data-testid="stSidebar"] * {
    color:#00ff88 !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background-color:#132b38;
    border:1px solid #00ffd5;
    padding:15px;
    border-radius:12px;
}

/* Metric labels */
[data-testid="stMetricLabel"] {
    color:#00ffd5 !important;
}

/* Metric values */
[data-testid="stMetricValue"] {
    color:white !important;
}

/* Dropdowns */
[data-baseweb="select"] > div {
    background-color:#132b38 !important;
}

[data-baseweb="select"] span {
    color:#00ff88 !important;
}

/* Dropdown menu */
div[role="listbox"] {
    background-color:#132b38 !important;
}

div[role="option"] span {
    color:#00ff88 !important;
}

/* Buttons */
button {
    background-color:#00ffd5 !important;
    color:black !important;
    font-weight:bold !important;
}

/* Tables */
[data-testid="stDataFrame"] {
    background-color:#132b38;
}

/* Inputs */
input {
    background-color:#132b38 !important;
    color:white !important;
}

</style>
""", unsafe_allow_html=True)


# ---------- DASHBOARD TITLE ----------
st.markdown("<h1>📈 Stock Analytics & Forecast Platform</h1>", unsafe_allow_html=True)


@st.cache_data
def load_stock_data(ticker):

    for i in range(3):

        try:
            data = yf.download(
                ticker,
                start="2018-01-01",
                progress=False,
                threads=False
            )

            if not data.empty:
                data.columns = data.columns.get_level_values(0)
                return data

        except:
            pass

        time.sleep(1)

    return None


@st.cache_data
def get_fundamentals(ticker):

    try:
        stock = yf.Ticker(ticker)

        fast = stock.fast_info
        info = stock.info
        hist = stock.history(period="1y")

        if hist.empty:
            return None

        market_cap = fast.get("market_cap") or info.get("marketCap")
        pe_ratio = info.get("trailingPE")
        dividend = info.get("dividendYield")
        beta = info.get("beta")

        return {
            "Market Cap": market_cap if market_cap else "N/A",
            "PE Ratio": pe_ratio if pe_ratio else "N/A",
            "Dividend Yield": dividend if dividend else "N/A",
            "Beta": beta if beta else "N/A",
            "52W High": hist["High"].max(),
            "52W Low": hist["Low"].min()
        }

    except:
        return None


# ---------- BSE STOCK LIST ----------

bse100 = [
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
"IRCTC.NS","ZOMATO.NS","NYKAA.NS","DMART.NS"
]

stocks = {s.replace(".NS",""): s for s in bse100}


# ---------- SIDEBAR ----------

st.sidebar.markdown("## 📊 Dashboard Controls")

selected_stock = st.sidebar.selectbox(
    "Choose a stock",
    list(stocks.keys())
)

compare_stocks = st.sidebar.multiselect(
    "Compare with other stocks",
    list(stocks.keys())
)

ticker = stocks[selected_stock]


# ---------- LOAD DATA ----------

data = load_stock_data(ticker)

if data is None:
    st.warning("⚠️ Data temporarily unavailable. Try refreshing the app.")
    st.stop()


# ---------- METRICS ----------

st.markdown("---")
col1,col2,col3 = st.columns(3)

col1.metric("Current Price", round(data["Close"].iloc[-1],2))
col2.metric("52 Week High", round(data["High"].max(),2))
col3.metric("52 Week Low", round(data["Low"].min(),2))


# ---------- PRICE CHART ----------

st.subheader(f"📈 {selected_stock} Price Trend")

fig = px.line(
    data,
    x=data.index,
    y="Close",
    template="plotly_dark",
    color_discrete_sequence=["#00ffd5"]
)

st.plotly_chart(fig, use_container_width=True)


# ---------- MOVING AVERAGES ----------

st.subheader("📊 Moving Averages")

data["MA50"] = data["Close"].rolling(50).mean()
data["MA200"] = data["Close"].rolling(200).mean()

fig_ma = px.line(
    data,
    x=data.index,
    y=["Close","MA50","MA200"],
    template="plotly_dark"
)

st.plotly_chart(fig_ma, use_container_width=True)


# ---------- RSI ----------

st.subheader("⚡ RSI Indicator")

delta = data["Close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain/avg_loss
data["RSI"] = 100-(100/(1+rs))

fig_rsi = px.line(data, x=data.index, y="RSI", template="plotly_dark")

st.plotly_chart(fig_rsi, use_container_width=True)


# ---------- AI STOCK FORECAST ----------

st.markdown("---")
st.subheader("📊 AI Stock Price Forecast")

forecast_years = st.slider("Forecast Years",1,5,2)

df_forecast = data.reset_index()[["Date","Close"]]
df_forecast["t"] = range(len(df_forecast))

coef = pd.Series(df_forecast["Close"]).corr(pd.Series(df_forecast["t"]))

slope = (df_forecast["Close"].iloc[-1] - df_forecast["Close"].iloc[0]) / len(df_forecast)

future_days = 365 * forecast_years

future_prices = [
    df_forecast["Close"].iloc[-1] + slope * i
    for i in range(1, future_days+1)
]

future_dates = pd.date_range(
    start=df_forecast["Date"].iloc[-1],
    periods=future_days+1
)[1:]

forecast_df = pd.DataFrame({
    "Date": future_dates,
    "Forecast Price": future_prices
})

fig_forecast = px.line(
    forecast_df,
    x="Date",
    y="Forecast Price",
    template="plotly_dark",
    color_discrete_sequence=["#00ffd5"]
)

st.plotly_chart(fig_forecast, use_container_width=True)


















