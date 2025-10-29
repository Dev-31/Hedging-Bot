import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import io

def generate_synthetic_returns(n=100):
    return np.random.normal(0, 0.01, n)

def rolling_volatility(returns, window=10):
    return pd.Series(returns).rolling(window).std().fillna(0)

def forecast_volatility(returns, lookahead=5):
    vol = rolling_volatility(returns)
    X = np.arange(len(vol) - lookahead).reshape(-1, 1)
    y = vol[lookahead:].values
    model = LinearRegression()
    model.fit(X, y)

    future = np.arange(len(vol), len(vol) + lookahead).reshape(-1, 1)
    forecast = model.predict(future)
    return vol.values, forecast

def generate_vol_chart(asset, returns):
    vol, forecast = forecast_volatility(returns)
    plt.figure(figsize=(6,3))
    plt.plot(vol, label="Historical Volatility", color='blue')
    plt.plot(range(len(vol), len(vol) + len(forecast)), forecast, label="Forecast", color='orange')
    plt.title(f"{asset} Volatility Forecast")
    plt.xlabel("Time")
    plt.ylabel("Volatility")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf, forecast[-1]
