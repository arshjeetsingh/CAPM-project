# importing libraries
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
    # fetching S&P 500 data
    end = datetime.date.today()
    start = datetime.date(end.year - year, end.month, end.day)
    SP500 = yf.download('^GSPC', start=start, end=end)[['Close']]
    SP500.rename(columns={'Close': 'sp500'}, inplace=True)
    SP500.reset_index(inplace=True)

    # fetching stock data
    stocks_df = pd.DataFrame()
    for stock in stocks_list:
        data = yf.download(stock, start=start, end=end)
        stocks_df[f'{stock}'] = data['Close']
    stocks_df.reset_index(inplace=True)

    # merging with SP500 data
    SP500['Date'] = pd.to_datetime(SP500['Date'])
    stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
    stocks_df = stocks_df.drop(columns=["index"], errors="ignore")  # Drop residual index column
    stocks_df = pd.merge(stocks_df, SP500, on='Date', how='inner')

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('### Dataframe head')
        st.dataframe(stocks_df.head(), use_container_width=True)
    with col2:
        st.markdown('### Dataframe tail')
        st.dataframe(stocks_df.tail(), use_container_width=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('### Price of all the Stocks')
        st.plotly_chart(capm_functions.interactive_plot(stocks_df))

    with col2:
        st.markdown('### Price of all the Stocks (After Normalizing)')
        st.plotly_chart(capm_functions.interactive_plot(capm_functions.normalize(stocks_df)))

    # calculating daily return
    stocks_daily_return = capm_functions.daily_return(stocks_df)

    beta = {}
    alpha = {}

    for i in stocks_daily_return.columns:
        if i != 'Date' and i != 'sp500':
            b, a = capm_functions.calculate_beta(stocks_daily_return, i)
            beta[i] = b
            alpha[i] = a

    col1, col2 = st.columns([1, 1])

    beta_df = pd.DataFrame({'Stock': list(beta.keys()), 'Beta Value': [round(b, 2) for b in beta.values()]})

    with col1:
        st.markdown('### Calculated Beta Value ')
        st.dataframe(beta_df, use_container_width=True)

    # Calculate return for any security using CAPM
    rf = 0  # risk-free rate of return
    rm = stocks_daily_return['sp500'].mean() * 252  # market portfolio return
    return_df = pd.DataFrame({
        'Stock': list(beta.keys()),
        'Return Value': [round(rf + (beta[stock] * (rm - rf)), 2) for stock in beta.keys()]
    })

    with col2:
        st.markdown('### Calculated Return using CAPM ')
        st.dataframe(return_df, use_container_width=True)

except Exception as e:
    st.error(f"An error occurred: {e}")
