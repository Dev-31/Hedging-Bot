def protective_put(position_size, strike_price, option_price):
    cost = option_price * position_size
    return {
        "strategy": "Protective Put",
        "cost": round(cost, 2),
        "strike": strike_price,
        "position_covered": position_size
    }

def covered_call(position_size, strike_price, option_premium):
    income = option_premium * position_size
    return {
        "strategy": "Covered Call",
        "income": round(income, 2),
        "strike": strike_price,
        "risk_tradeoff": "Cap upside"
    }
