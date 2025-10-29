import requests

def get_okx_ticker(symbol="BTC-USDT"):
    url = f"https://www.okx.com/api/v5/market/ticker?instId={symbol}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["data"][0] if data.get("data") else None
    except Exception as e:
        print(f"[OKX ERROR] {e}")
        return None 
    
