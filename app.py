import streamlit as st
import pandas as pd
import yfinance as yf
import time
import plotly.express as px
from prophet import Prophet

st.set_page_config(page_title="Stock Analytics Dashboard", layout="wide")

st.title("📈 Stock Analytics & Forecast Platform")


# ---------- DATA FUNCTIONS ----------

@st.cache_data
def load_stock_data(ticker):
    data = yf.download(ticker, start="2018-01-01")

    if data.empty:
        return None

    data.columns = data.columns.get_level_values(0)
    return data


@st.cache_data
def get_fundamentals(ticker):

    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        time.sleep(1)

    except:
        return None

    if not info:
        return None

    return {
        "Market Cap": info.get("marketCap"),
        "PE Ratio": info.get("trailingPE"),
        "Dividend Yield": info.get("dividendYield"),
        "Beta": info.get("beta"),
        "52W High": info.get("fiftyTwoWeekHigh"),
        "52W Low": info.get("fiftyTwoWeekLow")
    }


# ---------- BSE100 STOCK LIST ----------

bse100 = [
"RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
"LT.NS","ITC.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS",
"HINDUNILVR.NS","BHARTIARTL.NS","ASIANPAINT.NS","BAJFINANCE.NS",
"MARUTI.NS","TITAN.NS","SUNPHARMA.NS","ULTRACEMCO.NS",
"WIPRO.NS","HCLTECH.NS","POWERGRID.NS","NTPC.NS",
"ONGC.NS","COALINDIA.NS","ADANIENT.NS","ADANIPORTS.NS",
"JSWSTEEL.NS","TATASTEEL.NS","GRASIM.NS","BAJAJFINSV.NS"
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
    st.error("Failed to fetch stock data.")
    st.stop()


# ---------- METRICS ----------

st.markdown("---")
col1,col2,col3 = st.columns(3)

col1.metric("Current Price", round(data["Close"].iloc[-1],2))
col2.metric("52 Week High", round(data["High"].max(),2))
col3.metric("52 Week Low", round(data["Low"].min(),2))


# ---------- PRICE CHART ----------

st.subheader(f"📈 {selected_stock} Price Trend")

fig = px.line(data, x=data.index, y="Close", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)


# ---------- MOVING AVERAGES ----------

st.subheader("📊 Moving Averages")

data["MA50"] = data["Close"].rolling(50).mean()
data["MA200"] = data["Close"].rolling(200).mean()

fig_ma = px.line(data, x=data.index, y=["Close","MA50","MA200"], template="plotly_dark")
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


# ---------- MULTI STOCK COMPARISON ----------

st.markdown("---")
st.subheader("📊 Multi-Stock Performance Comparison")

if compare_stocks:

    compare_df = pd.DataFrame()

    for stock in compare_stocks:

        ticker = stocks[stock]
        df = load_stock_data(ticker)

        if df is None:
            continue

        normalized = df["Close"] / df["Close"].iloc[0] * 100
        compare_df[stock] = normalized

    if not compare_df.empty:

        fig_compare = px.line(compare_df, template="plotly_dark")
        st.plotly_chart(fig_compare,use_container_width=True)

    else:
        st.warning("Could not fetch comparison data.")


# ---------- FUNDAMENTAL COMPARISON ----------

st.markdown("---")
st.subheader("📊 Stock Fundamentals Comparison")

compare_table = st.multiselect(
    "Select stocks for fundamentals comparison",
    list(stocks.keys()),
    key="fund_compare"
)

if compare_table:

    fundamentals = []

    for stock in compare_table:

        ticker = stocks[stock]
        info = get_fundamentals(ticker)

        if info is None:
            continue

        fundamentals.append({
            "Stock": stock,
            **info
        })

    df_fund = pd.DataFrame(fundamentals)

    if df_fund.empty:
        st.warning("Fundamental data could not be fetched. Try selecting different stocks.")

    else:

        st.dataframe(df_fund)

        df_score = df_fund.copy()

        df_score["PE Ratio"] = df_score["PE Ratio"].fillna(100)
        df_score["Dividend Yield"] = df_score["Dividend Yield"].fillna(0)
        df_score["Beta"] = df_score["Beta"].fillna(1)

        df_score["pe_score"] = 1 / df_score["PE Ratio"]
        df_score["div_score"] = df_score["Dividend Yield"]
        df_score["risk_score"] = 1 / df_score["Beta"]

        df_score["total_score"] = (
            0.4 * df_score["pe_score"] +
            0.3 * df_score["div_score"] +
            0.3 * df_score["risk_score"]
        )

        best_stock = df_score.sort_values("total_score",ascending=False).iloc[0]["Stock"]

        st.success(f"⭐ Suggested Stock Among Selected: **{best_stock}**")


# ---------- PORTFOLIO BUILDER ----------

st.markdown("---")
st.subheader("🤖 Smart Portfolio Builder")

investment_amount = st.number_input("Total Investment Amount (₹)",1000,10000000,100000)

risk_level = st.selectbox("Risk Appetite",["Low Risk","Moderate Risk","High Risk"])

years = st.slider("Investment Horizon (Years)",1,10,5)

st.write("Suggested diversified portfolio based on volatility")

if st.button("Generate Portfolio"):

    portfolio=[]

    for stock in bse100:

        df = load_stock_data(stock)

        if df is None:
            continue

        vol=df["Close"].pct_change().std()

        portfolio.append({
            "Stock":stock,
            "Volatility":vol
        })

    df_port=pd.DataFrame(portfolio)

    if risk_level=="Low Risk":
        df_port=df_port[df_port["Volatility"]<0.02]

    elif risk_level=="Moderate Risk":
        df_port=df_port[df_port["Volatility"]<0.035]

    df_port=df_port.sort_values("Volatility")

    selected=df_port.head(5)

    if selected.empty:
        st.warning("No stocks match the selected risk level.")

    else:

        allocation=investment_amount/len(selected)

        selected["Investment Allocation"]=allocation

        st.dataframe(selected)

        st.write("Suggested investment per stock:",round(allocation,2))








