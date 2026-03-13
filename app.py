import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from prophet import Prophet

st.set_page_config(page_title="Stock Analytics Dashboard", layout="wide")

# ---------- Custom Styling ----------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
}

h1, h2, h3, h4 {
    color: #00ffd5 !important;
}

.stMarkdown, .stText, .stMetric {
    color: yellow !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background-color: #132b38;
    border: 1px solid #00ffd5;
    padding: 15px;
    border-radius: 10px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111;
}

section[data-testid="stSidebar"] * {
    color: #00ff88 !important;
}

/* Buttons */
button {
    color: #00ff88 !important;
    font-weight: bold !important;
}

/* Dropdown styling */
[data-baseweb="select"] > div {
    background-color: #132b38 !important;
}

[data-baseweb="select"] span {
    color: #00ff88 !important;
}

div[role="listbox"] {
    background-color: #132b38 !important;
}

div[role="listbox"] span {
    color: #00ff88 !important;
}

span[data-baseweb="tag"] {
    background-color: #132b38 !important;
    color: #00ff88 !important;
}
/* Force dropdown options to green */
div[role="option"] span {
    color: #00ff88 !important;
}

/* Multiselect dropdown list */
div[data-baseweb="menu"] span {
    color: #00ff88 !important;
}

/* Dropdown hover highlight */
div[role="option"]:hover {
    background-color: #132b38 !important;
}

/* Select all option */
div[role="option"] {
    color: #00ff88 !important;
}
/* Dropdown text color */
[data-baseweb="select"] span {
    color: #00ff88 !important;
}

/* Dropdown menu */
div[role="listbox"] {
    background-color: #132b38 !important;
}

/* Dropdown options */
div[role="option"] span {
    color: #00ff88 !important;
}

/* Selected tags in multiselect */
span[data-baseweb="tag"] {
    background-color: #132b38 !important;
    color: #00ff88 !important;
}
/* Metric title text */
[data-testid="stMetricLabel"] {
    color: #00ffd5 !important;
    font-weight: bold;
}

/* Metric value text */
[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 28px !important;
}

/* Metric delta text (if used later) */
[data-testid="stMetricDelta"] {
    color: #00ff88 !important;
}
/* Input box text */
input {
    color: #ffffff !important;
    background-color: #132b38 !important;
}

/* Selectbox text */
[data-baseweb="select"] {
    color: #ffffff !important;
}

/* Selectbox value */
[data-baseweb="select"] span {
    color: #00ff88 !important;
}

/* Number input */
.stNumberInput input {
    color: #ffffff !important;
    background-color: #132b38 !important;
}

/* Slider labels */
.stSlider label {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📈 Stock Analytics & Forecast Platform")

# ---------- BSE100 Stock List ----------
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

# ---------- CAGR Functions ----------
def historical_cagr(data, years):
    start_price = data["Close"].iloc[0]
    end_price = data["Close"].iloc[-1]
    return (end_price/start_price)**(1/years) - 1


def forecast_cagr(data, years):

    df = data.reset_index()[["Date","Close"]]
    df.columns = ["ds","y"]

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=365*years)
    forecast = model.predict(future)

    future_price = forecast["yhat"].iloc[-1]
    current_price = data["Close"].iloc[-1]

    return (future_price/current_price)**(1/years) - 1


# ---------- Sidebar ----------
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

# ---------- Download Data ----------
data = yf.download(ticker, start="2018-01-01")
data.columns = data.columns.get_level_values(0)

# ---------- Metrics ----------
st.markdown("---")
col1,col2,col3 = st.columns(3)

col1.metric("Current Price", round(data["Close"].iloc[-1],2))
col2.metric("52 Week High", round(data["High"].max(),2))
col3.metric("52 Week Low", round(data["Low"].min(),2))

# ---------- Price Chart ----------
st.subheader(f"📈 {selected_stock} Price Trend")

fig = px.line(data, x=data.index, y="Close", template="plotly_dark")

fig.update_layout(
    plot_bgcolor="#0b1f2a",
    paper_bgcolor="#0b1f2a",
    font=dict(color="white", size=15),
    xaxis=dict(showgrid=True, gridcolor="#2c5364"),
    yaxis=dict(showgrid=True, gridcolor="#2c5364")
)

st.plotly_chart(fig, use_container_width=True)

# ---------- Moving Averages ----------
st.subheader("📊 Moving Averages")

data["MA50"] = data["Close"].rolling(50).mean()
data["MA200"] = data["Close"].rolling(200).mean()

fig_ma = px.line(data, x=data.index, y=["Close","MA50","MA200"], template="plotly_dark")

fig_ma.update_layout(
    plot_bgcolor="#0b1f2a",
    paper_bgcolor="#0b1f2a",
    font=dict(color="white"),
    xaxis=dict(gridcolor="#2c5364"),
    yaxis=dict(gridcolor="#2c5364")
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

fig_rsi.update_layout(
    plot_bgcolor="#0b1f2a",
    paper_bgcolor="#0b1f2a",
    font=dict(color="white"),
    xaxis=dict(gridcolor="#2c5364"),
    yaxis=dict(gridcolor="#2c5364")
)

st.plotly_chart(fig_rsi, use_container_width=True)

# ---------- MULTI STOCK COMPARISON ----------
st.markdown("---")
st.subheader("📊 Multi-Stock Performance Comparison")

if compare_stocks:

    compare_df = pd.DataFrame()

    for stock in compare_stocks:

        ticker = stocks[stock]

        df = yf.download(ticker,start="2018-01-01")
        df.columns = df.columns.get_level_values(0)

        normalized = df["Close"] / df["Close"].iloc[0] * 100

        compare_df[stock] = normalized

    fig_compare = px.line(compare_df, template="plotly_dark")

    fig_compare.update_layout(
        plot_bgcolor="#0b1f2a",
        paper_bgcolor="#0b1f2a",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#2c5364"),
        yaxis=dict(gridcolor="#2c5364"),
        yaxis_title="Relative Performance (Base = 100)"
    )

    st.plotly_chart(fig_compare,use_container_width=True)

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
        info = yf.Ticker(ticker).info

        fundamentals.append({
            "Stock": stock,
            "Market Cap": info.get("marketCap"),
            "PE Ratio": info.get("trailingPE"),
            "Dividend Yield": info.get("dividendYield"),
            "Beta": info.get("beta"),
            "52W High": info.get("fiftyTwoWeekHigh"),
            "52W Low": info.get("fiftyTwoWeekLow")
        })

    df_fund = pd.DataFrame(fundamentals)

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

# ---------- Robo Portfolio Advisor ----------
st.markdown("---")
st.subheader("🤖 Smart Portfolio Builder")

investment_amount = st.number_input("Total Investment Amount (₹)",1000,10000000,100000)

target_return = st.slider("Expected Annual Return (%)",5,25,12,key="robo_return")

risk_level = st.selectbox("Risk Appetite",["Low Risk","Moderate Risk","High Risk"])

years = st.slider("Investment Horizon (Years)",1,10,5,key="robo_years")

if st.button("Generate Portfolio"):

    portfolio=[]

    for stock in bse100:

        try:

            df=yf.download(stock,start="2018-01-01")
            df.columns=df.columns.get_level_values(0)

            hist=historical_cagr(df,5)
            future=forecast_cagr(df,years)

            score=(hist+future)/2
            vol=df["Close"].pct_change().std()

            portfolio.append({
            "Stock":stock,
            "Score":score,
            "Volatility":vol
            })

        except:
            pass

    df_port=pd.DataFrame(portfolio)

    if risk_level=="Low Risk":
        df_port=df_port[df_port["Volatility"]<0.02]

    elif risk_level=="Moderate Risk":
        df_port=df_port[df_port["Volatility"]<0.035]

    df_port=df_port.sort_values("Score",ascending=False)

    selected=df_port.head(5)

    if len(selected)>0:

        allocation=investment_amount/len(selected)
        selected["Investment Allocation"]=allocation

        st.dataframe(selected)

        st.write("Suggested investment per stock:",round(allocation,2))







