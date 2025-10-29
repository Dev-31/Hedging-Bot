from hedge.router import select_best_exchange
from hedge.liquidity import estimate_slippage, estimate_cost
from analytics.portfolio.history_tracker import log_hedge

def execute_hedge(asset, hedge_size, user_id=None):
    exchange, score = select_best_exchange(asset, hedge_size)
    slippage = estimate_slippage(exchange)
    cost = estimate_cost(hedge_size)

    response = {
        "status": "executed",
        "exchange": exchange,
        "slippage": slippage,
        "cost": cost,
        "hedge_size": hedge_size,
        "score": score,
    }

    if user_id:
        log_hedge(user_id, asset, hedge_size, cost, f"perp@{exchange}")
    return response
