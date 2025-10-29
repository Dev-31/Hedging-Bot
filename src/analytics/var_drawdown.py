import numpy as np

def historical_var(returns, confidence_level=0.95):
    sorted_returns = np.sort(returns)
    index = int((1 - confidence_level) * len(sorted_returns))
    return round(-sorted_returns[index], 4)

def max_drawdown(prices):
    peak = prices[0]
    max_dd = 0
    for price in prices:
        if price > peak:
            peak = price
        dd = (peak - price) / peak
        max_dd = max(max_dd, dd)
    return round(max_dd, 4)
