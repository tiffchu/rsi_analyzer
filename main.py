import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

st.set_page_config(page_title="RSI Analyzer", layout="centered")

st.title("📈 RSI Analyzer")
st.write("Enter a stock ticker to compute RSI values.")

# User input
ticker = st.text_input("Ticker symbol", value="AAPL").upper()
rsi_period = st.slider("RSI period", min_value=5, max_value=30, value=14)

# Helpe r
def get_rsi_windows(ticker, period=14, lookback_days=120):
    df = yf.download(
        ticker,
        period=f"{lookback_days}d",
        interval="1d",
        auto_adjust=False,
        progress=False
    )

    if df.empty:
        return None, "No data returned."

    # Handle MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if "Close" not in df.columns:
        return None, "Close price not found."

    # Compute RSI
    df["RSI"] = ta.rsi(df["Close"], length=period)

    # Drop warm-up NaNs
    df = df.dropna(subset=["RSI"])

    if len(df) < 14:
        return None, "Not enough data to compute RSI windows."

    results = {
        "most_recent": round(df["RSI"].iloc[-1], 2),
        "last_7": round(df["RSI"].iloc[-7:].mean(), 2),
        "prior_7": round(df["RSI"].iloc[-14:-7].mean(), 2),
        "data": df
    }

    return results, None

#  analysis

if st.button("Compute RSI"):
    with st.spinner("Fetching data and computing RSI..."):
        results, error = get_rsi_windows(ticker, rsi_period)

    if error:
        st.error(error)
    else:
        st.subheader(f"RSI Summary for {ticker}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Most Recent RSI", results["most_recent"])
        col2.metric("Avg RSI (Last 7 days)", results["last_7"])
        col3.metric("Avg RSI (Prior 7 days)", results["prior_7"])

        st.divider()

        #Table
        st.subheader("Recent RSI Values")
        st.dataframe(
            results["data"][["Close", "RSI"]].tail(20),
            use_container_width=True
        )

        # Plot
        st.subheader("RSI Chart")
        fig, ax = plt.subplots()
        ax.plot(results["data"].index, results["data"]["RSI"])
        ax.axhline(70, linestyle="--")
        ax.axhline(30, linestyle="--")
        ax.set_ylabel("RSI")
        ax.set_xlabel("Date")
        st.pyplot(fig)
