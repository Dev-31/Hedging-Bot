import pandas as pd

def correlation_matrix(asset_returns_dict):
    df = pd.DataFrame(asset_returns_dict)
    return df.corr().round(3)
