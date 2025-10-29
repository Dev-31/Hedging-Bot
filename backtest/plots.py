import matplotlib.pyplot as plt

def plot_pnl(pnl_history):
    plt.figure(figsize=(6,3))
    plt.plot(pnl_history, label="Hedge PnL")
    plt.title("Backtest Hedge PnL")
    plt.xlabel("Step")
    plt.ylabel("PnL")
    plt.grid(True)
    plt.legend()
    plt.show()
