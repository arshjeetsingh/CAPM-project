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
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig

# Function to normalize the prices based on the initial price
def normalize(df):
    x = df.copy()
    for i in x.columns[1:]:
        x[i] = x[i] / x[i].iloc[0]  # Normalizing based on the first value
    return x

# Function to calculate the daily returns
def daily_return(df):
    df_daily_return = df.copy()
    for i in df.columns[1:]:
        # Using `.loc` to avoid SettingWithCopyWarning
        df_daily_return.loc[1:, i] = ((df[i].iloc[1:] - df[i].iloc[:-1].values) / df[i].iloc[:-1].values) * 100
        df_daily_return.loc[0, i] = 0  # Set the first row's return to 0
    return df_daily_return

# Function to calculate beta
def calculate_beta(stocks_daily_return, stock):
    # Assume risk free rate is zero
    rm = stocks_daily_return['sp500'].mean() * 252
    # Fit a polynomial between each stock and the S&P500
    b, a = np.polyfit(stocks_daily_return['sp500'], stocks_daily_return[stock], 1)
    return b, a
