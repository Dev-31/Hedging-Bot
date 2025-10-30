# Spot Exposure Hedging Bot

This project is a working prototype of an automated risk management system that monitors real-time spot positions and dynamically hedges directional exposure using perpetual futures or options.  
The system integrates with live cryptocurrency exchange APIs and provides Telegram-based interactive control for monitoring and execution.

---

## Project Overview
The Spot Exposure Hedging Bot automates the process of portfolio hedging in crypto markets.  
It calculates risk metrics, monitors exposures, and executes hedge actions to maintain delta neutrality or manage volatility risks.  
The bot can operate in both manual and automated modes.

---

## Core Features

### Real-Time Risk Calculation
- Computes key option greeks: Delta, Gamma, Theta, Vega.  
- Calculates hedge ratios for perpetual futures using correlation and beta.  
- Tracks portfolio-level VaR, drawdown, and correlation matrices.

### Automated Hedging Logic
- Supports delta-neutral and options-based hedging strategies.  
- Allows both manual and automated hedge execution.  
- Includes transaction cost and slippage estimation for realistic modeling.  
- Implements configurable thresholds for hedge triggers.

### Telegram Bot Integration
- Sends interactive alerts and portfolio updates.  
- Accepts commands such as `/monitor_risk`, `/auto_hedge`, `/hedge_now`, and `/hedge_status`.  
- Provides inline buttons for quick actions like “Hedge Now” or “Adjust Threshold”.

### Portfolio Analytics
- Visualizes portfolio exposures (Delta, Gamma, Theta, Vega).  
- Offers scenario analysis and stress testing.  
- Provides performance summaries and P&L breakdowns via Telegram.

---

## Tech Stack
- **Language:** Python 3.10+  
- **Libraries:** `ccxt`, `pandas`, `NumPy`, `Matplotlib`, `TA-Lib`, `python-telegram-bot`  
- **Concurrency:** `asyncio`, `multithreading` for real-time data handling  
- **Exchanges:** OKX, Bybit, Deribit (via public/demo APIs)  
- **Environment:** Works on Kaggle, Colab, or local Python environments  

---

## Highlights
- Real-market integration (in demo mode using public exchange APIs).  
- Modular architecture for extending strategies or replacing APIs.  
- Designed for lightweight deployment and testing.  
- Reliable error handling and logging for production-like performance.  
- Built as an educational and practical demonstration of quantitative risk automation.

---

## Future Enhancements
- Machine learning for volatility forecasting and hedge timing.  
- Multi-asset portfolio optimization.  
- Advanced option strategies (Iron Condors, Collars, Butterflies).  
- Backtesting framework for historical performance validation.  
- Web-based dashboard for visualization and user control.

---

## Author
Dev Sopariwala
