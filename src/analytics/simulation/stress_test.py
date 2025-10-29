# analytics/simulation/stress_test.py
import numpy as np

def simulate_stress_return(price, drop_pct):
    stressed_price = price * (1 - drop_pct)
    pnl = stressed_price - price
    return round(stressed_price, 2), round(pnl, 2)
