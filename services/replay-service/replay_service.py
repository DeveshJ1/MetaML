import random
import time
from datetime import datetime, timezone

from shared.libs.mq import setup_channel, publish_json

SYMBOL = "AAPL"

REGIMES = ["TREND_UP", "MEAN_REVERT", "VOLATILE"]

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def generate_next_price(price, regime):
    if regime == "TREND_UP":
        drift = 0.05
        shock = random.gauss(0, 0.2)
        return max(1.0, price + drift + shock)

    if regime == "MEAN_REVERT":
        mean_price = 100.0
        pull = 0.08 * (mean_price - price)
        shock = random.gauss(0, 0.15)
        return max(1.0, price + pull + shock)

    if regime == "VOLATILE":
        shock = random.gauss(0, 0.8)
        return max(1.0, price + shock)

    return price

def make_snapshot(price, regime):
    spread = {
        "TREND_UP": 0.05,
        "MEAN_REVERT": 0.04,
        "VOLATILE": 0.15
    }[regime]

    best_bid = round(price - spread / 2, 2)
    best_ask = round(price + spread / 2, 2)

    return {
        "symbol": SYMBOL,
        "mid_price": round(price, 2),
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread": round(best_ask - best_bid, 2),
        "regime": regime,
        "timestamp": utc_now()
    }

def main():
    connection, channel = setup_channel()

    price = 100.0
    tick = 0
    regime = "TREND_UP"

    print("[replay-service] Starting market replay/synthetic feed...")

    try:
        while True:
            if tick % 30 == 0:
                regime = random.choice(REGIMES)
                print(f"[replay-service] Switching regime to {regime}")

            price = generate_next_price(price, regime)
            snapshot = make_snapshot(price, regime)

            publish_json(channel, "market.snapshot", snapshot)

            print(
                f"[replay-service] {snapshot['symbol']} "
                f"mid={snapshot['mid_price']} "
                f"bid={snapshot['best_bid']} "
                f"ask={snapshot['best_ask']} "
                f"regime={snapshot['regime']}"
            )

            tick += 1
            time.sleep(1)

    except KeyboardInterrupt:
        print("[replay-service] Stopping...")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
