# importing libraries
import streamlit as st
import yfinance as yf
import pandas as pd
import capm_functions

# setting page config
st.set_page_config(
    page_title="Sharpe Ratio",
    page_icon="📊",
    layout="wide",
)

st.title("Calculate Sharpe Ratio")

# Input from user
col1, col2 = st.columns([1, 1])
with col1:
    stock = st.selectbox("Choose a stock", ('TSLA', 'AAPL', 'NFLX', 'MSFT', 'AMZN', 'NVDA', 'GOOGL'))
with col2:
    year = st.number_input("Number of Years", 1, 10)

try:
    # Download stock data
    stock_data = yf.download(stock, period=f'{year}y')
    stock_data['Daily Return'] = stock_data['Close'].pct_change()
    mean_return = stock_data['Daily Return'].mean() * 252  # Annualized mean return
    std_dev = stock_data['Daily Return'].std() * (252 ** 0.5)  # Annualized standard deviation

    # Risk-free rate assumption
    risk_free_rate = 0.03  # 3% risk-free rate

    # Calculate Sharpe Ratio
    sharpe_ratio = (mean_return - risk_free_rate) / std_dev

    st.markdown(f"### Sharpe Ratio for {stock}: {round(sharpe_ratio, 2)}")
    st.markdown("### Stock Performance Overview")
    st.line_chart(stock_data['Close'])

except Exception as e:
    st.error(f"An error occurred: {e}")
