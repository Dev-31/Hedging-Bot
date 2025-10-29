import pandas as pd

def load_data(file_path="data/btc_usdt_sample.csv"):
    df = pd.read_csv(file_path, parse_dates=["timestamp"])
    df.set_index("timestamp", inplace=True)
    return df
