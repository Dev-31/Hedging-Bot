from analytics.var_drawdown import historical_var
import random

class RiskMonitor:
    def __init__(self):
        self.sessions = {}

    def start_monitoring(self, user_id, asset, size, threshold):
        if user_id not in self.sessions:
            self.sessions[user_id] = {}
        self.sessions[user_id][asset] = {
            "size": size,
            "threshold": threshold,
        }

    def stop_monitoring(self, user_id, asset):
        if user_id in self.sessions and asset in self.sessions[user_id]:
            del self.sessions[user_id][asset]

    def get_status(self, user_id):
        return self.sessions.get(user_id, {})

    def check_risk(self, asset, price):
        mock_returns = [random.uniform(-0.02, 0.03) for _ in range(20)]
        var = historical_var(mock_returns)
        return {"VaR": var, "alert": var > 0.02}

risk_monitor = RiskMonitor()
