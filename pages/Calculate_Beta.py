# importing libraries
import streamlit as st
import datetime
import pandas as pd
import yfinance as yf
import capm_functions
import plotly.express as px

# setting page config
st.set_page_config(
    page_title="CAPM",
    page_icon="📈",
    layout="wide",
)

st.title('Calculate Beta and Return for Individual Stock')

# getting input from user
col1, col2 = st.columns([1, 1])
with col1:
    stock = st.selectbox("Choose a stock", ('TSLA', 'AAPL', 'NFLX', 'MGM', 'MSFT', 'AMZN', 'NVDA', 'GOOGL'))
with col2:
    year = st.number_input("Number of Years", 1, 10)

try:
    # fetching S&P 500 data
    end = datetime.date.today()
    start = datetime.date(end.year - year, end.month, end.day)
    SP500 = yf.download('^GSPC', start=start, end=end)[['Close']]
    SP500.rename(columns={'Close': 'sp500'}, inplace=True)
    SP500.reset_index(inplace=True)

    # fetching stock data
    stock_df = yf.download(stock, start=start, end=end)[['Close']]
    stock_df.rename(columns={'Close': stock}, inplace=True)
    stock_df.reset_index(inplace=True)

    # merging with SP500 data
    SP500['Date'] = pd.to_datetime(SP500['Date'])
    stock_df['Date'] = pd.to_datetime(stock_df['Date'])
    merged_df = pd.merge(stock_df, SP500, on='Date', how='inner')

    # calculating daily return
    stocks_daily_return = capm_functions.daily_return(merged_df)

    # calculate beta and alpha
    beta, alpha = capm_functions.calculate_beta(stocks_daily_return, stock)

    # risk-free rate of return
    rf = 0

    # market portfolio return
    rm = stocks_daily_return['sp500'].mean() * 252

    # calculate return
    return_value = round(rf + (beta * (rm - rf)), 2)

    # showing results
    st.markdown(f'### Beta : {round(beta, 2)}')
    st.markdown(f'### Return : {return_value}')

    # plotting scatter and regression line
    fig = px.scatter(stocks_daily_return, x='sp500', y=stock, title=stock)
    fig.add_scatter(
        x=stocks_daily_return['sp500'],
        y=beta * stocks_daily_return['sp500'] + alpha,
        mode='lines',
        name='Regression Line'
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"An error occurred: {e}")
