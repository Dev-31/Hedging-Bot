import numpy as np

def calculate_beta(x_returns, y_returns):
    cov_matrix = np.cov(x_returns, y_returns)
    beta = cov_matrix[0, 1] / cov_matrix[1, 1]
    return round(beta, 4)

def hedge_ratio(position_size, beta):
    return position_size * beta

