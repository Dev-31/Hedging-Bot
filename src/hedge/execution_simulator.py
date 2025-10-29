import random
from analytics.portfolio.history_tracker import log_hedge
def estimate_slippage(market_volatility=0.015):
    return round(random.uniform(0.001, market_volatility), 4)

def estimate_transaction_cost(hedge_size, fee_perc=0.001):
    return round(abs(hedge_size) * fee_perc, 4)

def simulate_perp_hedge(asset, hedge_size, user_id=None):
    slippage = estimate_slippage()
    fee = estimate_transaction_cost(hedge_size)
    result = {
        "asset": asset,
        "hedge_size": hedge_size,
        "slippage": slippage,
        "fee": fee,
        "status": "executed"
    }

    if user_id:
        log_hedge(user_id, asset, hedge_size, fee, "perp")
    return result