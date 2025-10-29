from collections import defaultdict
import datetime

hedge_logs = defaultdict(list)

def log_hedge(user_id, asset, size, cost, method):
    hedge_logs[user_id].append({
        "asset": asset,
        "size": size,
        "cost": cost,
        "method": method,
        "timestamp": datetime.datetime.now().isoformat()
    })

def get_hedge_history(user_id, asset=None):
    records = hedge_logs[user_id]
    if asset:
        return [r for r in records if r['asset'] == asset.upper()]
    return records
