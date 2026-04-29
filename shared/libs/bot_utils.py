import uuid
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def make_order(bot_id, symbol, side, quantity, order_type="MARKET", price=None):
    return {
        "order_id": str(uuid.uuid4()),
        "bot_id": bot_id,
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "price": price,
        "order_type": order_type,
        "timestamp": utc_now()
    }

class RollingWindow:
    def __init__(self, size):
        self.size = size
        self.values = []

    def add(self, value):
        self.values.append(float(value))
        if len(self.values) > self.size:
            self.values.pop(0)

    def ready(self):
        return len(self.values) >= self.size

    def mean(self):
        if not self.values:
            return 0.0
        return sum(self.values) / len(self.values)

    def last(self):
        if not self.values:
            return None
        return self.values[-1]

    def first(self):
        if not self.values:
            return None
        return self.values[0]
