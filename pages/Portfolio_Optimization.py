import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize

# setting page config
st.set_page_config(
    page_title="Portfolio Optimization",
    page_icon="📈",
    layout="wide",
)

st.title("Portfolio Optimization")

# User input
col1, col2 = st.columns([1, 1])
with col1:
    stocks = st.multiselect("Select Stocks", ['TSLA', 'AAPL', 'NFLX', 'MSFT', 'AMZN', 'NVDA', 'GOOGL'], ['TSLA', 'AAPL', 'NFLX'])
with col2:
    years = st.number_input("Number of Years", 1, 10)

if len(stocks) < 2:
    st.error("Please select at least two stocks for portfolio optimization.")
else:
    try:
        # Download stock data
        data_frames = []
        for stock in stocks:
            df = yf.download(stock, period=f"{years}y")['Close']
            df.name = stock  # Set the stock name as the column name
            data_frames.append(df)

        if not data_frames:
            raise ValueError("No data could be fetched for the selected stocks.")

        # Merge all stock data into a single DataFrame
        data_df = pd.concat(data_frames, axis=1)

        # Ensure DataFrame is correctly indexed
        data_df.index = pd.to_datetime(data_df.index)
        data_df.dropna(inplace=True)  # Drop any rows with missing values

        # Calculate daily returns
        returns = data_df.pct_change().dropna()

        # Portfolio optimization
        def portfolio_stats(weights):
            weights = np.array(weights)
            mean_return = np.sum(returns.mean() * weights) * 252
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
            sharpe_ratio = mean_return / portfolio_std
            return portfolio_std, mean_return, sharpe_ratio

        def negative_sharpe(weights):
            return -portfolio_stats(weights)[2]

        num_stocks = len(stocks)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(num_stocks))
        initial_weights = [1 / num_stocks] * num_stocks

        # Optimize
        result = minimize(negative_sharpe, initial_weights, bounds=bounds, constraints=constraints)
        optimal_weights = result.x

        # Display results
        std_dev, mean_return, sharpe = portfolio_stats(optimal_weights)

        st.markdown("### Optimal Portfolio Allocation")
        for i, stock in enumerate(stocks):
            st.write(f"{stock}: {round(optimal_weights[i] * 100, 2)}%")

        st.markdown(f"### Portfolio Expected Return: {round(mean_return, 2)}")
        st.markdown(f"### Portfolio Standard Deviation: {round(std_dev, 2)}")
        st.markdown(f"### Portfolio Sharpe Ratio: {round(sharpe, 2)}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
