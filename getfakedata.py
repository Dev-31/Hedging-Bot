# generate_csv.py

import pandas as pd
import numpy as np

# seed for reproducibility
np.random.seed(42)

# Defining parameters
num_points = 288  # 24 hours × 12 (5-minute intervals)
start_price = 43000
spread_std_dev = 2  # typical spot-perp spread noise

# Creating timestamps
timestamps = pd.date_range(start="2024-01-01 00:00", periods=num_points, freq="5min")

# Generating spot price as random walk
spot_changes = np.random.normal(0, 5, size=num_points)  # random walk noise
spot_prices = np.cumsum(spot_changes) + start_price

# Creating perp prices with small variation from spot
perp_prices = spot_prices + np.random.normal(0, spread_std_dev, size=num_points)

# DataFrame
df = pd.DataFrame({
    "timestamp": timestamps,
    "spot_price": spot_prices,
    "perp_price": perp_prices
})

df.to_csv("data/btc_usdt_sample.csv", index=False)

print("✅ BTC USDT sample data generated at data/btc_usdt_sample.csv")
