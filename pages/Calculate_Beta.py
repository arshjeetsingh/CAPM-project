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
    stock = st.selectbox("Choose a stock", 
        ('TSLA', 'AAPL', 'NFLX', 'MGM', 'MSFT', 'AMZN', 'NVDA', 'GOOGL')
    )
with col2:
    year = st.number_input("Number of Years", 1, 10)

try:
    # fetching S&P 500 data
    end = datetime.date.today()
    start = datetime.date(end.year - year, end.month, end.day)
    sp500_df = yf.download('^GSPC', start=start, end=end, progress=False)[['Close']].reset_index()
    sp500_df.columns = ['Date', 'sp500']

    # fetching chosen stock data
    stock_df = yf.download(stock, start=start, end=end, progress=False)[['Close']].reset_index()
    stock_df.columns = ['Date', stock]

    # merging the two dataframes
    merged_df = pd.merge(stock_df, sp500_df, on='Date', how='inner')
    merged_df.dropna(inplace=True)
    merged_df.sort_values(by='Date', inplace=True)
    merged_df.reset_index(drop=True, inplace=True)

    # calculating daily return
    stocks_daily_return = capm_functions.daily_return(merged_df)

    # calculate beta and alpha
    beta_val, alpha_val = capm_functions.calculate_beta(stocks_daily_return, stock)

    # assume risk-free rate of return
    rf = 0.0

    # market portfolio return (annualized)
    rm = stocks_daily_return['sp500'].mean() * 252

    # calculate return using CAPM
    return_value = round(rf + beta_val * (rm - rf), 2)

    # showing results
    st.markdown(f'### Beta : {round(beta_val, 2)}')
    st.markdown(f'### Return (CAPM) : {return_value}')

    # plotting scatter and regression line
    # ensure data is float for plotting
    x = stocks_daily_return['sp500'].astype(float)
    y = stocks_daily_return[stock].astype(float)

    fig = px.scatter(
        x=x, 
        y=y, 
        title=f"{stock} vs S&P 500 Daily Returns",
        labels={'x': 'S&P 500 Daily Return (%)', 'y': f'{stock} Daily Return (%)'}
    )
    # regression line: y = beta_val * x + alpha_val
    reg_y = beta_val * x + alpha_val
    fig.add_scatter(
        x=x, 
        y=reg_y, 
        mode='lines',
        name='Regression Line'
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"An error occurred: {e}")
