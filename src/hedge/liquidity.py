import random

# Simulate exchange-specific slippage
def estimate_slippage(exchange, volatility=0.015):
    base = {
        "okx": 0.002,
        "bybit": 0.003,
        "deribit": 0.004
    }.get(exchange.lower(), 0.005)
    return round(base + random.uniform(0, volatility), 4)

def estimate_cost(size, fee_pct=0.001):
    return round(abs(size) * fee_pct, 4)
