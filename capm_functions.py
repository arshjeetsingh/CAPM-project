import plotly.express as px
import numpy as np
import pandas as pd

# Function to plot interactive plot
def interactive_plot(df):
    """
    Plots all columns in df (except 'Date') as interactive lines vs. 'Date'.
    """
    fig = px.line()
    # Ensure 'Date' is treated as x-axis
    for col in df.columns:
        if col != 'Date':
            fig.add_scatter(x=df['Date'], y=df[col], name=col)
    fig.update_layout(
        width=450,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig

# Function to normalize the prices based on the initial price
def normalize(df):
    """
    Returns a copy of df with each numeric column normalized to the 1st value.
    """
    x = df.copy()
    # Identify numeric columns only
    numeric_cols = x.select_dtypes(include=['float', 'int']).columns
    for col in numeric_cols:
        if x[col].iloc[0] != 0:
            x[col] = x[col] / x[col].iloc[0]
    return x

# Function to calculate daily returns (in %)
def daily_return(df):
    """
    Computes the % daily return of all numeric columns in df.
    First row of each numeric column will be set to 0.
    """
    df_daily = df.copy()
    # Identify numeric columns only (excluding 'Date')
    numeric_cols = df_daily.select_dtypes(include=['float', 'int']).columns
    df_daily[numeric_cols] = df_daily[numeric_cols].pct_change() * 100
    # Replace NaN in first row with 0
    df_daily.loc[0, numeric_cols] = 0
    return df_daily

# Function to calculate beta using linear regression (np.polyfit)
def calculate_beta(stocks_daily_return, stock):
    """
    Calculates Beta and Alpha for 'stock' relative to 'sp500'
    using the columns in stocks_daily_return DataFrame.
    """
    # Convert columns to numeric in case of any leftover object dtype
    x = stocks_daily_return['sp500'].astype(float, errors='ignore').values
    y = stocks_daily_return[stock].astype(float, errors='ignore').values
    
    # Fit a 1st-degree polynomial (straight line) y = b*x + a
    b, a = np.polyfit(x, y, 1)
    return b, a
