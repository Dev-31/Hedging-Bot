class Portfolio:
    def __init__(self, spot_position):
        self.spot_position = spot_position
        self.hedge_position = 0
        self.pnl_history = []

    def calculate_delta(self):
        return self.spot_position + self.hedge_position

    def apply_hedge(self, hedge_size):
        self.hedge_position += hedge_size

    def compute_pnl(self, spot_price, perp_price):
        hedge_pnl = self.hedge_position * (perp_price - spot_price)
        self.pnl_history.append(hedge_pnl)
