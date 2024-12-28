# importing libraries
import streamlit as st
import seaborn as sns
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# setting page config
st.set_page_config(
    page_title="Correlation Matrix",
    page_icon="📊",
    layout="wide",
)

st.title("Stock Correlation Matrix")

# User input
stocks = st.multiselect("Select Stocks", ['TSLA', 'AAPL', 'NFLX', 'MSFT', 'AMZN', 'NVDA', 'GOOGL'], ['TSLA', 'AAPL', 'NFLX'])
years = st.number_input("Number of Years", 1, 10)

if len(stocks) < 2:
    st.error("Please select at least two stocks for correlation analysis.")
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

        # Calculate correlation matrix
        corr = data_df.corr()

        # Plot correlation heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"An error occurred: {e}")
