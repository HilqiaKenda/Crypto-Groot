# dashboard/dash_apps/indicator_charts.py

import plotly.graph_objs as go
from tasks.binance_listener import live_candles
from indicators import *
import pandas as pd

def rsi_chart(df):
    rsi = compute_rsi(df)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=rsi, name="RSI", line=dict(color='purple')))
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.add_hline(y=30, line_dash="dash", line_color="green")
    fig.update_layout(title="Relative Strength Index (RSI)")
    return fig

def macd_chart(df):
    macd_line, signal_line, hist = compute_macd(df)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=macd_line, name="MACD Line"))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=signal_line, name="Signal Line"))
    fig.add_trace(go.Bar(x=df['timestamp'], y=hist, name="Histogram"))
    fig.update_layout(title="MACD (Moving Average Convergence Divergence)")
    return fig

def bollinger_chart(df):
    bb_upper, bb_lower = compute_bollinger_bands(df)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=bb_upper, name="Upper Band", line=dict(dash="dot")))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=bb_lower, name="Lower Band", line=dict(dash="dot")))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['close'], name="Close Price"))
    fig.update_layout(title="Bollinger Bands")
    return fig

def atr_chart(df):
    atr = compute_atr(df)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=atr, name="ATR", line=dict(color='orange')))
    fig.update_layout(title="Average True Range (ATR)")
    return fig

def stochastic_chart(df):
    k, d = compute_stochastic(df)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=k, name="%K"))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=d, name="%D"))
    fig.update_layout(title="Stochastic Oscillator")
    return fig
