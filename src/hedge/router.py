from hedge.liquidity import estimate_slippage

# Exchange fees and latency values (demo)
EXCHANGES = {
    "OKX": {"fee": 0.001, "latency": 50},
    "Bybit": {"fee": 0.0012, "latency": 80},
    "Deribit": {"fee": 0.0009, "latency": 120},
}

def select_best_exchange(asset, hedge_size):
    candidates = []
    for name, info in EXCHANGES.items():
        slippage = estimate_slippage(name)
        cost = abs(hedge_size) * info["fee"] + slippage
        score = cost + (info["latency"] / 1000)  # simplified score
        candidates.append((name, round(score, 4)))

    best = min(candidates, key=lambda x: x[1])
    return best[0], best[1]  # return exchange name and score
