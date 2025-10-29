from src.exchanges.okx import get_okx_ticker
from src.exchanges.bybit import get_bybit_ticker
from src.exchanges.deribit import get_deribit_index_price

print("📈 Testing Exchange API Connections...\n")

okx_data = get_okx_ticker()
bybit_data = get_bybit_ticker()
deribit_price = get_deribit_index_price()

print(f"OKX BTC-USDT Ticker: {okx_data}")
print(f"Bybit BTCUSDT Ticker: {bybit_data}")
print(f"Deribit BTC Index Price: {deribit_price}")
