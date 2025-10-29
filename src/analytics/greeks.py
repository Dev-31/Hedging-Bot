import math
from scipy.stats import norm

def calculate_greeks(S, K, T, r, sigma, option_type="call"):
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    delta = norm.cdf(d1) if option_type == "call" else -norm.cdf(-d1)
    gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
    theta = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T)) -
             r * K * math.exp(-r * T) * norm.cdf(d2 if option_type == "call" else -d2))
    vega = S * norm.pdf(d1) * math.sqrt(T)

    return {
        "delta": round(delta, 4),
        "gamma": round(gamma, 4),
        "theta": round(theta, 4),
        "vega": round(vega / 100, 4),  # vega per 1% volatility change
    }
