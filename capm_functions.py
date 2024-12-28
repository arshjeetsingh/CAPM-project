import plotly.express as px
import numpy as np

# Function to plot interactive plot
def interactive_plot(df):
    fig = px.line()
    for i in df.columns[1:]:
         fig.add_scatter(x=df['Date'], y=df[i], name=i)
    fig.update_layout(
        width=450,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
    )
    return fig

# Function to normalize the prices based on the initial price
def normalize(df):
    x = df.copy()
    for i in x.columns[1:]:
        x[i] = x[i] / x[i][0]
    return x

# Function to calculate the daily returns
def daily_return(df):
    df_daily_return = df.copy()
    for i in df.columns[1:]:
        df_daily_return[i] = df[i].pct_change() * 100  # Calculate percentage change
    df_daily_return.iloc[0] = 0  # Set first row to 0
    return df_daily_return

# Function to calculate beta
def calculate_beta(stocks_daily_return, stock):
    x = stocks_daily_return['sp500'].values.ravel()  # Use ravel() to ensure 1D array
    y = stocks_daily_return[stock].values.ravel()  # Use ravel() to ensure 1D array
    b, a = np.polyfit(x, y, 1)  # Perform linear regression
    return b, a
