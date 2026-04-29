import csv
import os
import random
import time
from datetime import datetime, timezone

from shared.libs.mq import setup_channel, publish_json

DEFAULT_CSV = "data/raw/sample_prices.csv"
SYMBOL = os.getenv("MARKET_SYMBOL", "AAPL")
REPLAY_SPEED_SECONDS = float(os.getenv("REPLAY_SPEED_SECONDS", "1.0"))

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def infer_regime(prev_price, current_price, recent_changes):
    if len(recent_changes) >= 3:
        avg_abs_change = sum(abs(x) for x in recent_changes[-3:]) / 3
    else:
        avg_abs_change = abs(current_price - prev_price)

    change = current_price - prev_price

    if avg_abs_change > 0.45:
        return "VOLATILE"
    if change > 0.15:
        return "TREND_UP"
    if change < -0.15:
        return "TREND_DOWN"
    return "MEAN_REVERT"

def generate_synthetic_depth(mid_price, regime):
    if regime == "VOLATILE":
        spread = random.uniform(0.12, 0.22)
        base_depth = random.randint(50, 120)
    elif regime in ["TREND_UP", "TREND_DOWN"]:
        spread = random.uniform(0.05, 0.10)
        base_depth = random.randint(100, 250)
    else:
        spread = random.uniform(0.03, 0.07)
        base_depth = random.randint(150, 350)

    best_bid = round(mid_price - spread / 2, 2)
    best_ask = round(mid_price + spread / 2, 2)

    bids = []
    asks = []

    for level in range(5):
        bids.append({
            "price": round(best_bid - level * 0.03, 2),
            "quantity": base_depth + random.randint(-20, 40)
        })
        asks.append({
            "price": round(best_ask + level * 0.03, 2),
            "quantity": base_depth + random.randint(-20, 40)
        })

    return {
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread": round(best_ask - best_bid, 2),
        "bids": bids,
        "asks": asks
    }

def make_snapshot(row, prev_price, recent_changes):
    close_price = float(row["close"])
    regime = infer_regime(prev_price, close_price, recent_changes)
    depth = generate_synthetic_depth(close_price, regime)

    return {
        "symbol": row["symbol"],
        "source": "HYBRID_CSV_REPLAY",
        "historical_timestamp": row["timestamp"],
        "mid_price": round(close_price, 2),
        "best_bid": depth["best_bid"],
        "best_ask": depth["best_ask"],
        "spread": depth["spread"],
        "bids": depth["bids"],
        "asks": depth["asks"],
        "regime": regime,
        "volume": int(row["volume"]),
        "timestamp": utc_now()
    }

def load_rows(csv_path):
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader if row["symbol"] == SYMBOL]

def main():
    csv_path = os.getenv("MARKET_CSV", DEFAULT_CSV)
    rows = load_rows(csv_path)

    if not rows:
        raise RuntimeError(f"No rows found for symbol={SYMBOL} in {csv_path}")

    connection, channel = setup_channel()

    print(f"[replay-service] Starting HYBRID replay from {csv_path}")
    print(f"[replay-service] Loaded {len(rows)} rows for {SYMBOL}")

    prev_price = float(rows[0]["close"])
    recent_changes = []

    try:
        while True:
            for row in rows:
                current_price = float(row["close"])
                recent_changes.append(current_price - prev_price)
                recent_changes = recent_changes[-10:]

                snapshot = make_snapshot(row, prev_price, recent_changes)

                publish_json(channel, "market.snapshot", snapshot)

                print(
                    f"[replay-service] {snapshot['symbol']} "
                    f"hist_ts={snapshot['historical_timestamp']} "
                    f"mid={snapshot['mid_price']} "
                    f"bid={snapshot['best_bid']} "
                    f"ask={snapshot['best_ask']} "
                    f"regime={snapshot['regime']} "
                    f"source={snapshot['source']}"
                )

                prev_price = current_price
                time.sleep(REPLAY_SPEED_SECONDS)

            print("[replay-service] Reached end of CSV. Replaying from beginning...")

    except KeyboardInterrupt:
        print("[replay-service] Stopping...")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
