import numpy as np
from analytics.var_drawdown import historical_var

def calculate_portfolio_var(returns_dict):
    combined_returns = np.mean(list(returns_dict.values()), axis=0)
    return round(historical_var(combined_returns), 4)

def calculate_drawdown(price_series):
    max_peak = price_series[0]
    max_drawdown = 0
    for price in price_series:
        max_peak = max(max_peak, price)
        drawdown = (max_peak - price) / max_peak
        max_drawdown = max(max_drawdown, drawdown)
    return round(max_drawdown, 4)

def correlation_matrix(prices_dict):
    asset_names = list(prices_dict.keys())
    price_data = np.array([prices_dict[name] for name in asset_names])

    # Ensure at least 2 assets, else return 1.0 correlation with self
    if len(asset_names) == 1:
        return {asset_names[0]: {asset_names[0]: 1.0}}

    # Stack properly to get (n_assets, time_series)
    price_matrix = np.vstack(price_data)
    corr_matrix = np.corrcoef(price_matrix)

    return {
        asset_names[i]: {asset_names[j]: float(corr_matrix[i][j]) for j in range(len(asset_names))}
        for i in range(len(asset_names))
    }
