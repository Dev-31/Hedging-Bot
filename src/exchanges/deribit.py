import requests

def get_deribit_index_price():
    try:
        url = "https://www.deribit.com/api/v2/public/get_index_price"
        params = {"index_name": "btc_usd"}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"[DERIBIT ERROR] Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            return None

        try:
            data = response.json()
            return data
        except requests.exceptions.JSONDecodeError as e:
            print(f"[DERIBIT JSON ERROR] {e}")
            print(f"Raw response: {response.text}")
            return None

    except Exception as e:
        print(f"[DERIBIT ERROR] {e}")
        return None
