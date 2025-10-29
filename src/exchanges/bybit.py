import requests

def get_bybit_ticker():
    try:
        url = "https://api.bybit.com/v5/market/tickers"
        params = {"category": "spot", "symbol": "BTCUSDT"}
        response = requests.get(url, params=params, timeout=10)

        # Validate HTTP response
        if response.status_code != 200:
            print(f"[BYBIT ERROR] Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            return None

        # Try decoding JSON
        try:
            data = response.json()
            return data
        except requests.exceptions.JSONDecodeError as e:
            print(f"[BYBIT JSON ERROR] {e}")
            print(f"Raw response: {response.text}")
            return None

    except Exception as e:
        print(f"[BYBIT ERROR] {e}")
        return None
