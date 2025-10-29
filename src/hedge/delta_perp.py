def calculate_hedge_size(position_delta, perp_beta, leverage=1.0):
    """
    Compute size of the perpetual hedge based on beta-adjusted exposure.
    """
    hedge_units = -(position_delta / perp_beta) * leverage
    return round(hedge_units, 4)
