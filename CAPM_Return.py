import streamlit as st
import datetime
import pandas as pd
import yfinance as yf
import capm_functions

# setting page config
st.set_page_config(
    page_title="Calculate Beta",
    page_icon="📈",
    layout="wide",
)

st.title('Capital Asset Pricing Model 📈')

# getting input from user
col1, col2 = st.columns([1, 1])
with col1:
    stocks_list = st.multiselect(
        "Choose 4 Stocks",
        ('TSLA', 'AAPL', 'NFLX', 'MGM', 'MSFT', 'AMZN', 'NVDA', 'GOOGL'),
        ['TSLA', 'AAPL', 'MSFT', 'NFLX'],
        key="stock_list",
    )
with col2:
    year = st.number_input("Number of Years", 1, 10)

try:
    # Fetching S&P 500 data
    end = datetime.date.today()
    start = datetime.date(end.year - year, end.month, end.day)
    SP500 = yf.download('^GSPC', start=start, end=end, progress=False)[['Close']].reset_index()
    SP500.columns = ['Date', 'sp500']  # rename to have 'Date' and 'sp500'

    # Fetching stock data
    # We'll build a dataframe that has 'Date' in the first column,
    # then each chosen stock as its own column
    all_stocks = pd.DataFrame()
    for idx, stock in enumerate(stocks_list):
        data = yf.download(stock, start=start, end=end, progress=False)[['Close']].reset_index()
        data.columns = ['Date', stock]
        if idx == 0:
            # start our all_stocks DataFrame
            all_stocks = data
        else:
            all_stocks = pd.merge(all_stocks, data, on='Date', how='outer')
    
    # Drop any rows with no price data and sort by Date
    all_stocks.dropna(inplace=True)
    all_stocks.sort_values(by='Date', inplace=True)
    all_stocks.reset_index(drop=True, inplace=True)

    # Merge with SP500 data
    combined_df = pd.merge(all_stocks, SP500, on='Date', how='inner')
    combined_df.sort_values(by='Date', inplace=True)
    combined_df.reset_index(drop=True, inplace=True)

    # Quick peek
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('### Dataframe head')
        st.dataframe(combined_df.head(), use_container_width=True)
    with col2:
        st.markdown('### Dataframe tail')
        st.dataframe(combined_df.tail(), use_container_width=True)

    # Plot raw and normalized prices
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('### Price of all the Stocks')
        st.plotly_chart(capm_functions.interactive_plot(combined_df), use_container_width=True)

    with col2:
        st.markdown('### Price of all the Stocks (After Normalizing)')
        normalized_df = capm_functions.normalize(combined_df)
        st.plotly_chart(capm_functions.interactive_plot(normalized_df), use_container_width=True)

    # Calculate daily returns
    stocks_daily_return = capm_functions.daily_return(combined_df)

    # Calculate Beta & Alpha for each chosen stock
    beta = {}
    alpha = {}
    for col in stocks_list:
        b, a = capm_functions.calculate_beta(stocks_daily_return, col)
        beta[col] = b
        alpha[col] = a

    # Show Beta values
    beta_df = pd.DataFrame({
        'Stock': list(beta.keys()),
        'Beta Value': [round(b, 2) for b in beta.values()]
    })

    # Calculate return for each security using CAPM
    # risk-free rate of return (assume 0 for simplicity or set your own)
    rf = 0.0
    # market portfolio return (annualized)
    rm = stocks_daily_return['sp500'].mean() * 252

    return_df = pd.DataFrame({
        'Stock': list(beta.keys()),
        'Return Value': [
            round(rf + (beta[stock] * (rm - rf)), 2)
            for stock in beta.keys()
        ]
    })

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('### Calculated Beta Value')
        st.dataframe(beta_df, use_container_width=True)
    with col2:
        st.markdown('### Calculated Return using CAPM')
        st.dataframe(return_df, use_container_width=True)

except Exception as e:
    st.error(f"An error occurred: {e}")
