from backtest.Portfolio import Portfolio
def run_strategy(data, threshold=0.05):
    portfolio = Portfolio(spot_position=1)
    logs = []

    for i in range(1, len(data)):
        row = data.iloc[i]
        spot = row["spot_price"]
        perp = row["perp_price"]

        delta = portfolio.calculate_delta()

        # Trigger hedge if delta exposure > threshold
        if abs(delta) > threshold:
            hedge_size = -delta
            portfolio.apply_hedge(hedge_size)
            logs.append({
                "time": row.name,
                "spot": spot,
                "perp": perp,
                "delta": delta,
                "hedge_size": hedge_size,
            })

        portfolio.compute_pnl(spot, perp)

    return portfolio, logs
