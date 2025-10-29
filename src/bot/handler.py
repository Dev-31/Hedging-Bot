import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from analytics.simulation.stress_test import simulate_stress_return
from telegram.ext import ConversationHandler, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from analytics.risk_monitor import risk_monitor
from analytics.greeks import calculate_greeks
from hedge.delta_perp import calculate_hedge_size
from hedge.execution_simulator import simulate_perp_hedge
from analytics.portfolio.metrics import calculate_portfolio_var, calculate_drawdown, correlation_matrix
from analytics.portfolio.history_tracker import get_hedge_history, log_hedge
from hedge.executor import execute_hedge
from analytics.portfolio.chart_gen import generate_drawdown_chart, generate_return_chart
from analytics.ml.forecast import generate_synthetic_returns, generate_vol_chart
from analytics.ml.forecast import forecast_volatility, generate_synthetic_returns
from exchanges.okx import get_okx_ticker
from exchanges.bybit import get_bybit_ticker
from exchanges.deribit import get_deribit_index_price
from hedge.straddle import simulate_straddle
from telegram.ext import CallbackQueryHandler
import numpy as np
import os
from database.queries import upsert_user, insert_risk_config, insert_hedge_log, get_user_risk_config


MONITOR_ASSET, MONITOR_SIZE, MONITOR_THRESHOLD = range(3)
AUTO_ASSET, AUTO_STRATEGY = range(2)
VIEW_CHART_ASSET, VIEW_CHART_TYPE = range(3, 5)  
VOL_FORECAST_ASSET = 5
STRESS_TEST_ASSET, STRESS_TEST_DROP = range(6, 8) 
STRADDLE_ASSET, STRADDLE_STRIKE, STRADDLE_PREMIUM = range(8, 11)
GREEKS_ASSET = 6
LIVE_MARKET_ASSET = 6 


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "cmd_greek_metrics":
       return await greeks_start(update, context)
    
    elif data == "cmd_stress_test": #for stress test
        return await stress_test_start(update, context)
    
    elif data == "cmd_straddle": #for Straddle
        return await straddle_start(update, context)

    elif data == "cmd_portfolio_summary": #for portfolio summary
        await portfolio_summary(update, context)

    elif data == "cmd_monitor_risk": #for monitor risk
        await query.edit_message_text("⚠️ Usage:\n`/monitor_risk <asset> <size> <threshold>`", parse_mode='Markdown')

    elif data == "cmd_auto_hedge": #for auto hedge
        await query.edit_message_text("🔄 Usage:\n`/auto_hedge <asset> <strategy>`", parse_mode='Markdown')

    elif data == "cmd_view_chart": #for view chart
        await query.edit_message_text("📉 Usage:\n`/view_chart <asset> <drawdown/return>`", parse_mode='Markdown')

    elif data == "cmd_vol_forecast": #for volatility forecast
        await query.edit_message_text("🔮 Usage:\n`/vol_forecast <asset>`", parse_mode='Markdown')

    elif data == "cmd_hedge_history": #for hedge history
        await hedge_history(update, context)

    elif data == "cmd_live_market":
        await query.edit_message_text("🪙 Usage:\n`/live_market <asset>` (e.g., `/live_market BTC`)", parse_mode='Markdown')

    else:
        await query.edit_message_text("❓ Unknown action.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Portfolio Summary", callback_data="cmd_portfolio_summary")],
        [InlineKeyboardButton("⚠️ Monitor Risk", callback_data="cmd_monitor_risk")],
        [InlineKeyboardButton("🔄 Auto Hedge", callback_data="cmd_auto_hedge")],
        [InlineKeyboardButton("📉 View Chart", callback_data="cmd_view_chart")],
        [InlineKeyboardButton("🔮 Volatility Forecast", callback_data="cmd_vol_forecast")],
        [InlineKeyboardButton("📘 Hedge History", callback_data="cmd_hedge_history")],
        [InlineKeyboardButton("📐 Risk Greeks", callback_data="cmd_greek_metrics")],  
        [InlineKeyboardButton("🔥 Stress Test", callback_data="cmd_stress_test")],     
        [InlineKeyboardButton("🧩 Straddle Strategy", callback_data="cmd_straddle")],
        [InlineKeyboardButton("📡 Live Market", callback_data="cmd_live_market")]
    ])

    await update.message.reply_text(
        text=(
            "👋 *Welcome to GoQuant's Risk Hedging Bot!*\n"
            "Manage your spot exposure, analyze portfolio risks, and automate hedging with one tap below."
        ),
        parse_mode='Markdown',
        reply_markup=keyboard
    )


## Portfolio Summary
async def portfolio_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    sessions = risk_monitor.get_status(user_id)

    if not sessions:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🚫 No assets in portfolio.")
        return

    # Mock return generation per asset
    returns = {asset: np.random.normal(0, 0.015, 50) for asset in sessions}
    prices = {asset: 100 + np.cumsum(r) for asset, r in returns.items()}

    var = calculate_portfolio_var(returns)
    drawdown = max(calculate_drawdown(p) for p in prices.values())
    correlation = correlation_matrix(prices)

    msg = f"📊 *Portfolio Risk Summary*\n"
    msg += f"• VaR (95%): `{var}`\n"
    msg += f"• Max Drawdown: `{drawdown}`\n\n"
    msg += f"*Correlation Matrix*\n"
    for asset, corrs in correlation.items():
        msg += f"{asset}: {', '.join([f'{k}:{round(v,2)}' for k,v in corrs.items()])}\n"
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode='Markdown')


## Monitor Risk
async def monitor_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        asset, size, threshold = context.args
        upsert_user(user_id, update.effective_user.username)
        insert_risk_config(user_id, asset.upper(), float(size), float(threshold))
        risk_monitor.start_monitoring(user_id, asset.upper(), float(size), float(threshold))
        await update.message.reply_text(f"✅ Monitoring started for {asset} with position {size} and threshold {threshold}")
    except Exception as e:
        await update.message.reply_text("❌ Usage: /monitor_risk <asset> <position_size> <risk_threshold>")

# Triggered when user clicks "Monitor Risk" button
async def monitor_risk_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await context.bot.send_message(chat_id=update.effective_chat.id, text="📌 Which asset would you like to monitor?")
    return MONITOR_ASSET

async def monitor_risk_asset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["asset"] = update.message.text.upper()
    await update.message.reply_text("📏 What is the position size?")
    return MONITOR_SIZE

async def monitor_risk_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["size"] = float(update.message.text)
        await update.message.reply_text("📉 What is the risk threshold (e.g., 0.02 for 2%)?")
        return MONITOR_THRESHOLD
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number.")
        return MONITOR_SIZE

async def monitor_risk_threshold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        threshold = float(update.message.text)
        asset = context.user_data["asset"]
        size = context.user_data["size"]
        user_id = update.effective_user.id
        upsert_user(user_id, update.effective_user.username)
        insert_risk_config(user_id, asset, size, threshold)
        risk_monitor.start_monitoring(user_id, asset, size, threshold)
        risk_monitor.start_monitoring(user_id, asset, size, threshold)

        await update.message.reply_text(
            f"✅ Monitoring started for `{asset}` with position `{size}` and threshold `{threshold}`",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ Invalid threshold. Try again.")
        return MONITOR_THRESHOLD

async def stop_risk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        asset = context.args[0]
        risk_monitor.stop_monitoring(user_id, asset.upper())
        await update.message.reply_text(f"🛑 Monitoring stopped for {asset}")
    except Exception as e:
        await update.message.reply_text("❌ Usage: /stop_risk <asset>")


## Auto Hedge
async def auto_hedge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        asset = context.args[0].upper()
        strategy = context.args[1].lower()

        returns = generate_synthetic_returns()
        _, forecast = forecast_volatility(returns)
        future_vol = forecast[-1]

        if future_vol < 0.005:
            await update.message.reply_text(f"📉 Volatility is predicted to stay low. Skipping hedge.\nForecasted vol: `{round(future_vol, 4)}`")
            return
        sessions = risk_monitor.get_status(user_id)

        if asset not in sessions:
            await update.message.reply_text("❌ Asset not being monitored.")
            return

        position_size = sessions[asset]["size"]
        mock_beta = 0.95  # Static beta for demo
        mock_delta = position_size * 1.0  # Assuming 1 delta per unit

        if strategy == "perp":
            hedge_size = calculate_hedge_size(mock_delta, mock_beta)
            result = execute_hedge(asset, hedge_size, user_id)
            await update.message.reply_text(
                f"✅ *Smart Hedge Executed*\n"
                f"Asset: `{asset}`\n"
                f"Exchange: `{result['exchange']}`\n"
                f"Hedge Size: `{hedge_size}`\n"
                f"Slippage: `{result['slippage']}`\n"
                f"Fee: `{result['cost']}`",
                parse_mode='Markdown'
            )

        elif strategy == "straddle":
            result = simulate_straddle(asset, position_size, user_id)
            await update.message.reply_text(
                f"📘 *Straddle Executed*\n"
                f"Asset: `{asset}`\n"
                f"Strategy: `Straddle`\n"
                f"Premium Paid: `{result['premium']}`\n"
                f"Strike: `{result['strike']}`\n"
                f"Contracts: `{result['contracts']}`",
                parse_mode='Markdown'
            )

        else:
            await update.message.reply_text("❌ Unsupported strategy. Try: `perp` or `straddle`")

    except:
        await update.message.reply_text("❌ Usage: /auto_hedge <asset> perp")

async def auto_hedge_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("🔄 Which asset would you like to hedge? (e.g., BTC)")
    return AUTO_ASSET

async def auto_hedge_asset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["asset"] = update.message.text.upper()
    await update.message.reply_text("🧠 What strategy to use? (e.g., `perp`)")
    return AUTO_STRATEGY

async def auto_hedge_strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    strategy = update.message.text.lower()
    asset = context.user_data.get("asset")
    user_id = update.effective_user.id

    try:
        # Generate forecast
        returns = generate_synthetic_returns()
        _, forecast = forecast_volatility(returns)
        future_vol = forecast[-1]

        if future_vol < 0.005:
            await update.message.reply_text(
                f"📉 Volatility is low. Skipping hedge.\nForecasted vol: `{round(future_vol, 4)}`",
                parse_mode='Markdown'
            )
            return ConversationHandler.END

        sessions = risk_monitor.get_status(user_id)
        if asset not in sessions:
            await update.message.reply_text("❌ Asset not being monitored.")
            return ConversationHandler.END

        position_size = sessions[asset]["size"]
        mock_beta = 0.95
        mock_delta = position_size * 1.0

        if strategy == "perp":
            hedge_size = calculate_hedge_size(mock_delta, mock_beta)
            result = execute_hedge(asset, hedge_size, user_id)
            await update.message.reply_text(
                f"✅ *Smart Hedge Executed*\n"
                f"Asset: `{asset}`\n"
                f"Exchange: `{result['exchange']}`\n"
                f"Hedge Size: `{hedge_size}`\n"
                f"Slippage: `{result['slippage']}`\n"
                f"Fee: `{result['cost']}`",
                parse_mode='Markdown'
            )
        
        elif strategy == "straddle":
            result = simulate_straddle(asset, user_id)  
            await update.message.reply_text(
                f"🧩 *Straddle Strategy Executed*\n"
                f"Asset: `{asset}`\n"
                f"Strike: `{result['strike']}`\n"
                f"Cost: `{result['cost']}`\n"
                f"Max Loss: `{result['max_loss']}`\n"
                f"Max Gain: `{result['max_gain']}`",
                parse_mode="Markdown"
            )
    
        else:
            await update.message.reply_text("❌ Unsupported strategy. Use: `perp` or `straddle`")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

    return ConversationHandler.END


## View Chart
async def view_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        asset = context.args[0].upper()
        chart_type = context.args[1].lower()
        returns = np.random.normal(0, 0.01, 50)
        prices = 100 + np.cumsum(returns)

        if chart_type == "drawdown":
            chart = generate_drawdown_chart(prices, asset)
        elif chart_type == "return":
            chart = generate_return_chart(returns, asset)
        else:
            await update.message.reply_text("❌ Invalid type. Use 'drawdown' or 'return'")
            return

        await update.message.reply_photo(photo=chart, caption=f"{asset} - {chart_type.capitalize()} Chart")
    except Exception as e:
        await update.message.reply_text("❌ Usage: /view_chart <asset> <drawdown/return>")

async def view_chart_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("📈 Which asset would you like to view?")
    return VIEW_CHART_ASSET

async def view_chart_asset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["asset"] = update.message.text.upper()
    await update.message.reply_text("📊 What type of chart? (`drawdown` or `return`)")
    return VIEW_CHART_TYPE
async def view_chart_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asset = context.user_data.get("asset")
    chart_type = update.message.text.lower()

    try:
        returns = np.random.normal(0, 0.01, 50)
        prices = 100 + np.cumsum(returns)

        if chart_type == "drawdown":
            chart = generate_drawdown_chart(prices, asset)
        elif chart_type == "return":
            chart = generate_return_chart(returns, asset)
        else:
            await update.message.reply_text("❌ Invalid chart type. Use `drawdown` or `return`.")
            return VIEW_CHART_TYPE

        await update.message.reply_photo(
            photo=chart,
            caption=f"📊 *{asset}* - *{chart_type.capitalize()} Chart*",
            parse_mode='Markdown'
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error generating chart: {e}")

    return ConversationHandler.END


## Volatility Forecast
async def vol_forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        asset = context.args[0].upper()
        returns = generate_synthetic_returns()
        chart, prediction = generate_vol_chart(asset, returns)

        await update.message.reply_photo(
            photo=chart,
            caption=f"📈 *{asset} Volatility Forecast*\nNext-period forecast: `{round(prediction, 4)}`",
            parse_mode='Markdown'
        )
    except:
        await update.message.reply_text("❌ Usage: /vol_forecast <asset>")

async def vol_forecast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("🔍 Which asset do you want the volatility forecast for?")
    return VOL_FORECAST_ASSET

async def vol_forecast_asset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asset = update.message.text.upper()
    try:
        returns = generate_synthetic_returns()
        chart, prediction = generate_vol_chart(asset, returns)

        await update.message.reply_photo(
            photo=chart,
            caption=f"📈 *{asset} Volatility Forecast*\nNext-period forecast: `{round(prediction, 4)}`",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Failed to generate forecast: {e}")

    return ConversationHandler.END


async def greeks_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("📐 Please enter the asset symbol to calculate Greeks (e.g., BTC):")
    return GREEKS_ASSET

async def greeks_asset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asset = update.message.text.upper()
  
    delta = 1.0
    gamma = 0.002
    theta = -0.01
    vega = 0.03

    await update.message.reply_text(
        f"📐 *Risk Greeks for {asset}*\n"
        f"• Delta: `{delta}`\n"
        f"• Gamma: `{gamma}`\n"
        f"• Theta: `{theta}`\n"
        f"• Vega: `{vega}`",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


## Stress Start
async def stress_test_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("📌 Which asset do you want to run a stress test on?")
    return STRESS_TEST_ASSET

async def stress_test_asset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["asset"] = update.message.text.upper()
    await update.message.reply_text("📉 Enter the expected market drop as a percentage (e.g., 10 for 10%)")
    return STRESS_TEST_DROP

async def stress_test_drop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asset = context.user_data["asset"]
    try:
        drop = float(update.message.text)
        pnl = round(-drop * 0.8, 2)  # Mocked P&L
        await update.message.reply_text(
            f"🧪 Stress Test Result\n"
            f"Asset: {asset}\n"
            f"Drop: {drop}%\n"
            f"Estimated P&L Impact: {pnl}%",
            parse_mode='Markdown'
        )
    except:
        await update.message.reply_text("❌ Invalid drop. Try again.")
        return STRESS_TEST_DROP
    return ConversationHandler.END


## Hedge History
async def hedge_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg_target = update.message or update.callback_query.message  # Smart fallback

    try:
        asset = context.args[0] if context.args else None
        history = get_hedge_history(user_id, asset)

        if not history:
            await msg_target.reply_text("📭 No hedge records found.")
            return

        msg = f"📘 *Hedge History ({asset or 'All'})*\n"
        for h in history[-10:]:
            msg += (
                f"{h['timestamp'][:19]} | {h['asset']} | Size: {h['size']} | "
                f"Cost: {h['cost']} | Method: {h['method']}\n"
            )

        await msg_target.reply_text(msg, parse_mode='Markdown')

    except Exception as e:
        await msg_target.reply_text("❌ Usage: /hedge_history [asset]")


async def stress_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        asset = context.args[0].upper()
        shock = float(context.args[1])
        result = simulate_stress_return(asset, shock)

        await update.message.reply_text(
            f"🔥 *Stress Test Result for {asset}*\n"
            f"• Price drop: {shock*100:.1f}%\n"
            f"• Stressed price: {result['stressed_price']}\n"
            f"• Estimated PnL: {result['estimated_pnl']}",
            parse_mode="Markdown"
        )
    except:
        await update.message.reply_text("❌ Usage: /stress_test <asset> <shock>")


## Straddle Strategy
async def straddle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("💼 Which asset do you want to simulate a straddle strategy for?")
    return STRADDLE_ASSET

async def straddle_asset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["asset"] = update.message.text.upper()
    await update.message.reply_text("💵 What is the current strike price?")
    return STRADDLE_STRIKE

async def straddle_strike(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["strike"] = float(update.message.text)
        await update.message.reply_text("📉 Enter total premium paid (optional, default = 0):")
        return STRADDLE_PREMIUM
    except:
        await update.message.reply_text("❌ Invalid price. Try again.")
        return STRADDLE_STRIKE

async def straddle_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        premium = float(update.message.text)
    except:
        premium = 0.0

    asset = context.user_data["asset"]
    strike = context.user_data["strike"]

    # Simulate simple straddle payoff (long call + long put)
    prices = np.linspace(strike - 100, strike + 100, 100)
    payoff = [max(p - strike, 0) + max(strike - p, 0) - premium for p in prices]

    # Plot the payoff
    import matplotlib.pyplot as plt
    import io

    plt.figure(figsize=(6, 4))
    plt.plot(prices, payoff, label='Straddle Payoff')
    plt.axhline(0, color='black', linestyle='--')
    plt.title(f"{asset} Straddle Strategy")
    plt.xlabel("Price at Expiry")
    plt.ylabel("Profit / Loss")
    plt.legend()
    plt.grid(True)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    await update.message.reply_photo(
        photo=buffer,
        caption=f"📈 *Straddle Strategy for {asset}*\nStrike: `{strike}` | Premium: `{premium}`",
        parse_mode='Markdown'
    )

    return ConversationHandler.END


#Live Market
async def live_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        asset = context.args[0].upper() if context.args else "BTC"

        # --- OKX ---
        okx_data = get_okx_ticker(f"{asset}-USDT")
        okx_price = okx_data['last'] if okx_data else "N/A"

        # --- BYBIT ---
        bybit_data = get_bybit_ticker()
        bybit_price = "N/A"
        if bybit_data and bybit_data.get("result"):
            for ticker in bybit_data["result"].get("list", []):
                if ticker["symbol"] == f"{asset}USDT":
                    bybit_price = ticker["lastPrice"]
                    break

        # --- DERIBIT ---
        deribit_data = get_deribit_index_price()
        deribit_price = deribit_data["result"]["index_price"] if deribit_data else "N/A"

        msg = (
            f"📡 *Live Market Price: {asset}/USDT*\n"
            f"• OKX: `{okx_price}`\n"
            f"• Bybit: `{bybit_price}`\n"
            f"• Deribit: `{deribit_price}`"
        )

        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Error fetching market data: {e}")

async def live_market_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("📡 Which asset do you want to fetch prices for? (e.g., BTC)")
    return LIVE_MARKET_ASSET

async def live_market_asset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    asset = update.message.text.upper()

    okx = get_okx_ticker(f"{asset}-USDT")
    bybit = get_bybit_ticker()
    deribit = get_deribit_index_price()

    message = f"📡 *Live Market Prices for {asset}*\n"

    # OKX
    if okx:
        message += f"• OKX: `{okx['last']}` USDT\n"
    else:
        message += "• OKX: `Error fetching`\n"

    # Bybit
    try:
        price = [x for x in bybit["result"]["list"] if x["symbol"] == f"{asset}USDT"][0]["lastPrice"]
        message += f"• Bybit: `{price}` USDT\n"
    except:
        message += "• Bybit: `Error fetching`\n"

    # Deribit
    if deribit:
        message += f"• Deribit Index: `{deribit['result']['index_price']}` USD\n"
    else:
        message += "• Deribit: `Error fetching`\n"

    await update.message.reply_text(message, parse_mode='Markdown')
    return ConversationHandler.END


def get_app():
    from dotenv import load_dotenv
    load_dotenv()
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_API_KEY")).build()

## monitor risk
    monitor_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(monitor_risk_start, pattern="^cmd_monitor_risk$")],
        states={
            MONITOR_ASSET: [MessageHandler(filters.TEXT & ~filters.COMMAND, monitor_risk_asset)],
            MONITOR_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, monitor_risk_size)],
            MONITOR_THRESHOLD: [MessageHandler(filters.TEXT & ~filters.COMMAND, monitor_risk_threshold)],
        },
        fallbacks=[],
    )
    app.add_handler(monitor_conv)

## Auto Hedge
    auto_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(auto_hedge_start, pattern="^cmd_auto_hedge$")],
        states={
            AUTO_ASSET: [MessageHandler(filters.TEXT & ~filters.COMMAND, auto_hedge_asset)],
            AUTO_STRATEGY: [MessageHandler(filters.TEXT & ~filters.COMMAND, auto_hedge_strategy)],
        },
        fallbacks=[],
    )
    app.add_handler(auto_conv)

## View chart
    view_chart_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(view_chart_start, pattern="^cmd_view_chart$")],
        states={
            VIEW_CHART_ASSET: [MessageHandler(filters.TEXT & ~filters.COMMAND, view_chart_asset)],
            VIEW_CHART_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, view_chart_type)],
        },
        fallbacks=[],
    )
    app.add_handler(view_chart_conv)

## Volatility Forecast
    vol_forecast_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(vol_forecast_start, pattern="^cmd_vol_forecast$")],
        states={
            VOL_FORECAST_ASSET: [MessageHandler(filters.TEXT & ~filters.COMMAND, vol_forecast_asset)],
        },
        fallbacks=[],
    )
    app.add_handler(vol_forecast_conv)

## Stress Test
    stress_test_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(stress_test_start, pattern="^cmd_stress_test$")],
        states={
            STRESS_TEST_ASSET: [MessageHandler(filters.TEXT & ~filters.COMMAND, stress_test_asset)],
            STRESS_TEST_DROP: [MessageHandler(filters.TEXT & ~filters.COMMAND, stress_test_drop)],
        },
        fallbacks=[],
    )
    app.add_handler(stress_test_conv)

## Risk greek
    greeks_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(greeks_start, pattern="^cmd_greek_metrics$")],
        states={
            GREEKS_ASSET: [MessageHandler(filters.TEXT & ~filters.COMMAND, greeks_asset)],
        },
        fallbacks=[],
    )
    app.add_handler(greeks_conv)

## Straddle
    straddle_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(straddle_start, pattern="^cmd_straddle$")],
        states={
            STRADDLE_ASSET: [MessageHandler(filters.TEXT & ~filters.COMMAND, straddle_asset)],
            STRADDLE_STRIKE: [MessageHandler(filters.TEXT & ~filters.COMMAND, straddle_strike)],
            STRADDLE_PREMIUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, straddle_premium)],
        },
        fallbacks=[],
    )
    app.add_handler(straddle_conv)

    ## Live Market
    live_market_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(live_market_start, pattern="^cmd_live_market$")],
        states={
            LIVE_MARKET_ASSET: [MessageHandler(filters.TEXT & ~filters.COMMAND, live_market_asset)],
        },
        fallbacks=[],
    )
    app.add_handler(live_market_conv)

    InlineKeyboardButton("⚠️ Monitor Risk", callback_data="cmd_monitor_risk")
    app.add_handler(CommandHandler("stop_risk", stop_risk))
    app.add_handler(CommandHandler("risk_status", greeks_asset))
    app.add_handler(CommandHandler("portfolio_summary", portfolio_summary))
    app.add_handler(CommandHandler("hedge_history", hedge_history))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stress_test", stress_test))
    app.add_handler(CommandHandler("live_market", live_market))
    
    app.add_handler(CallbackQueryHandler(button_callback))

    return app
