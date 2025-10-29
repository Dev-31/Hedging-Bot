from backtest.data_loader import load_data
from backtest.strategy import run_strategy
from backtest.plots import plot_pnl

def run_backtest():
    df = load_data()
    Portfolio, logs = run_strategy(df, threshold=0.1)
    plot_pnl(Portfolio.pnl_history)

    print(f"Final Hedge PnL: {sum(Portfolio.pnl_history):.2f}")
    return logs

if __name__ == "__main__":
    run_backtest()
