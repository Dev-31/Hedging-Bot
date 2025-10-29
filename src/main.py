import sys
import os

# Add 'src' to sys.path so all internal modules like `database`, `bot` are recognized
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import logging
from bot.handler import get_app

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    try:
        app = get_app()
        print("🚀 Starting GoQuant Hedging Bot...")
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("Bot stopped")
    except Exception as e:
        print(f"Error: {e}")