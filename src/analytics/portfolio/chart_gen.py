import matplotlib.pyplot as plt
import numpy as np
import io

def generate_drawdown_chart(price_series, asset):
    peak = np.maximum.accumulate(price_series)
    drawdown = (peak - price_series) / peak

    plt.figure(figsize=(6,3))
    plt.plot(drawdown, label="Drawdown", color='red')
    plt.title(f'{asset} Drawdown Chart')
    plt.xlabel("Time")
    plt.ylabel("Drawdown %")
    plt.grid(True)
    plt.tight_layout()

    # Save to memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

def generate_return_chart(returns, asset):
    plt.figure(figsize=(6,3))
    plt.plot(np.cumsum(returns), label="Cumulative Return", color='green')
    plt.title(f'{asset} Cumulative Return')
    plt.xlabel("Time")
    plt.ylabel("Return %")
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf
