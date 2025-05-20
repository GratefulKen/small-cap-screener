
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Small-Cap Stock Screener", layout="wide")

# --- Sidebar Filters ---
st.sidebar.header("Stock Screener Filters")

# --- Define tickers (sample small-caps) ---
TICKERS = ["BJRI", "BLMN", "CORT", "BOOT", "CCRN", "COLM", "ENSG", "GIII", "HZO", "MTH"]

@st.cache_data(ttl=3600)
def fetch_stock_data(ticker_list):
    stock_data = []
    for ticker in ticker_list:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            data = {
                "Ticker": ticker,
                "Name": info.get("longName", "N/A"),
                "Sector": info.get("sector", "N/A"),
                "Industry": info.get("industry", "N/A"),
                "Market Cap": info.get("marketCap"),
                "Revenue": info.get("totalRevenue"),
                "YoY Growth": info.get("revenueGrowth"),
                "Debt/Equity": info.get("debtToEquity"),
                "Current Ratio": info.get("currentRatio"),
                "Gross Margin": info.get("grossMargins"),
                "Free Cash Flow": info.get("freeCashflow"),
                "Insider Ownership": info.get("heldPercentInsiders"),
                "PE Ratio": info.get("trailingPE"),
                "PB Ratio": info.get("priceToBook"),
                "PEG Ratio": info.get("pegRatio"),
                "Description": info.get("longBusinessSummary")
            }
            stock_data.append(data)
        except Exception as e:
            st.warning(f"Error fetching data for {ticker}: {e}")
    return pd.DataFrame(stock_data)

df = fetch_stock_data(TICKERS)

# --- Screening Logic ---
filtered_df = df[
    (df["Market Cap"] >= 1e8) & (df["Market Cap"] <= 2e9) &
    (df["YoY Growth"] > 0.10) &
    (df["Debt/Equity"] < 1.0) &
    (df["Current Ratio"] > 1.5) &
    (df["Gross Margin"] > 0.30) &
    (df["Free Cash Flow"] > 0) &
    (df["Insider Ownership"] > 0.05)
]

st.title("Small-Cap Stock Screener")

st.dataframe(
    filtered_df[[
        "Ticker", "Name", "Market Cap", "YoY Growth", "Debt/Equity",
        "Current Ratio", "Gross Margin", "Free Cash Flow", "PE Ratio", "PB Ratio", "PEG Ratio"
    ]],
    use_container_width=True
)

# --- Detail View ---
selected = st.selectbox("Select a stock to view details", filtered_df["Ticker"].tolist() if not filtered_df.empty else [])

if selected:
    stock = filtered_df[filtered_df["Ticker"] == selected].iloc[0]
    st.subheader(f"{stock['Name']} ({stock['Ticker']})")
    st.markdown(f"**Sector:** {stock['Sector']} | **Industry:** {stock['Industry']}")
    st.markdown(f"""
    **Valuation Metrics:**
    - P/E Ratio: {stock['PE Ratio']}
    - P/B Ratio: {stock['PB Ratio']}
    - PEG Ratio: {stock['PEG Ratio']}
    """)
    st.markdown(stock["Description"])

    hist = yf.Ticker(selected).history(period="3mo")
    fig = go.Figure(data=go.Scatter(x=hist.index, y=hist["Close"], name="Close"))
    fig.update_layout(title=f"{selected} - Last 3 Months", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig, use_container_width=True)
