# hedge/options/straddle.py
def simulate_straddle(asset, size):
    # Mocked logic for call + put
    strike = 100
    premium = 5  # assumed
    total_cost = 2 * premium * size

    return {
        "strategy": "Long Straddle",
        "strike": strike,
        "cost": total_cost,
        "max_loss": total_cost,
        "max_gain": "Unlimited (in either direction)"
    }
