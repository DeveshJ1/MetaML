import csv
import json
import os
import time
from collections import defaultdict
from datetime import datetime, timezone

from shared.libs.mq import setup_channel, decode_json

BOT_TAXONOMY_PATH = "shared/schemas/bot_taxonomy.json"
FINGERPRINT_LOG = "data/logs/bot_fingerprints.csv"

WINDOW_SECONDS = int(os.getenv("FINGERPRINT_WINDOW_SECONDS", "30"))
INITIAL_CASH = 100000.0

FIELDS = [
    "window_start",
    "window_end",
    "bot_id",
    "strategy_type",
    "risk_profile",
    "market_regime",
    "trade_count",
    "buy_count",
    "sell_count",
    "net_position",
    "cash",
    "equity",
    "pnl",
    "drawdown",
    "fill_rate",
    "avg_trade_size",
    "avg_execution_price",
    "price_volatility",
    "recommended_for_future"
]

bot_cash = defaultdict(lambda: INITIAL_CASH)
bot_position = defaultdict(float)
bot_peak_equity = defaultdict(lambda: INITIAL_CASH)

window_trades = defaultdict(list)
window_prices = []
window_regimes = []

window_start_time = time.time()
window_start_iso = datetime.now(timezone.utc).isoformat()

last_mid_price = None

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def load_taxonomy():
    with open(BOT_TAXONOMY_PATH, "r") as f:
        return json.load(f)

def ensure_log_file():
    os.makedirs(os.path.dirname(FINGERPRINT_LOG), exist_ok=True)
    if not os.path.exists(FINGERPRINT_LOG):
        with open(FINGERPRINT_LOG, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()

def most_common(values):
    if not values:
        return "UNKNOWN"
    counts = defaultdict(int)
    for value in values:
        counts[value] += 1
    return max(counts, key=counts.get)

def simple_volatility(prices):
    if len(prices) < 2:
        return 0.0

    changes = []
    for i in range(1, len(prices)):
        changes.append(prices[i] - prices[i - 1])

    mean_change = sum(changes) / len(changes)
    variance = sum((x - mean_change) ** 2 for x in changes) / len(changes)
    return variance ** 0.5

def mark_to_market(bot_id):
    if last_mid_price is None:
        return bot_cash[bot_id]
    return bot_cash[bot_id] + bot_position[bot_id] * last_mid_price

def update_bot_trade(bot_id, side, price, qty, trade):
    if side == "BUY":
        bot_position[bot_id] += qty
        bot_cash[bot_id] -= price * qty
    elif side == "SELL":
        bot_position[bot_id] -= qty
        bot_cash[bot_id] += price * qty

    window_trades[bot_id].append({
        "side": side,
        "price": price,
        "quantity": qty,
        "trade": trade
    })

def handle_trade(trade):
    price = float(trade["price"])
    qty = float(trade["quantity"])

    buyer = trade["buyer_bot_id"]
    seller = trade["seller_bot_id"]

    if buyer != "simulated-liquidity-provider":
        update_bot_trade(buyer, "BUY", price, qty, trade)

    if seller != "simulated-liquidity-provider":
        update_bot_trade(seller, "SELL", price, qty, trade)

def handle_snapshot(snapshot):
    global last_mid_price

    last_mid_price = float(snapshot["mid_price"])
    window_prices.append(last_mid_price)
    window_regimes.append(snapshot.get("regime", "UNKNOWN"))

def build_fingerprint(bot_id, taxonomy, window_end_iso):
    trades = window_trades[bot_id]

    trade_count = len(trades)
    buy_count = sum(1 for t in trades if t["side"] == "BUY")
    sell_count = sum(1 for t in trades if t["side"] == "SELL")

    total_qty = sum(t["quantity"] for t in trades)
    avg_trade_size = total_qty / trade_count if trade_count else 0.0

    avg_execution_price = (
        sum(t["price"] for t in trades) / trade_count if trade_count else 0.0
    )

    equity = mark_to_market(bot_id)
    bot_peak_equity[bot_id] = max(bot_peak_equity[bot_id], equity)

    pnl = equity - INITIAL_CASH
    drawdown = bot_peak_equity[bot_id] - equity

    fill_rate = 1.0 if trade_count > 0 else 0.0

    metadata = taxonomy.get(bot_id, {
        "strategy_type": "unknown",
        "risk_profile": "unknown"
    })

    # temporary heuristic label for future ML:
    # positive PnL in this window means it was a good future candidate.
    recommended_for_future = pnl > 0

    return {
        "window_start": window_start_iso,
        "window_end": window_end_iso,
        "bot_id": bot_id,
        "strategy_type": metadata["strategy_type"],
        "risk_profile": metadata["risk_profile"],
        "market_regime": most_common(window_regimes),
        "trade_count": trade_count,
        "buy_count": buy_count,
        "sell_count": sell_count,
        "net_position": round(bot_position[bot_id], 4),
        "cash": round(bot_cash[bot_id], 4),
        "equity": round(equity, 4),
        "pnl": round(pnl, 4),
        "drawdown": round(drawdown, 4),
        "fill_rate": round(fill_rate, 4),
        "avg_trade_size": round(avg_trade_size, 4),
        "avg_execution_price": round(avg_execution_price, 4),
        "price_volatility": round(simple_volatility(window_prices), 6),
        "recommended_for_future": recommended_for_future
    }

def flush_fingerprints():
    global window_start_time, window_start_iso, window_trades, window_prices, window_regimes

    taxonomy = load_taxonomy()
    window_end_iso = utc_now()

    bot_ids = set(taxonomy.keys()) | set(window_trades.keys())

    if not bot_ids:
        return

    rows = []

    for bot_id in sorted(bot_ids):
        row = build_fingerprint(bot_id, taxonomy, window_end_iso)
        rows.append(row)

    with open(FINGERPRINT_LOG, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        for row in rows:
            writer.writerow(row)

    print("\n[fingerprint-service] Wrote fingerprints")
    print("-" * 80)
    for row in rows:
        print(
            f"{row['bot_id']:24s} "
            f"regime={row['market_regime']:12s} "
            f"trades={row['trade_count']:3d} "
            f"pnl={row['pnl']:9.2f} "
            f"drawdown={row['drawdown']:8.2f} "
            f"recommend={row['recommended_for_future']}"
        )
    print("-" * 80)

    window_start_time = time.time()
    window_start_iso = utc_now()
    window_trades = defaultdict(list)
    window_prices = []
    window_regimes = []

def maybe_flush():
    if time.time() - window_start_time >= WINDOW_SECONDS:
        flush_fingerprints()

def main():
    ensure_log_file()

    connection, channel = setup_channel()

    queue = "fingerprint_service.queue"
    channel.queue_declare(queue=queue, durable=True)

    channel.queue_bind(exchange="metaml.events", queue=queue, routing_key="market.snapshot")
    channel.queue_bind(exchange="metaml.events", queue=queue, routing_key="trade.executed")

    print(f"[fingerprint-service] Running with {WINDOW_SECONDS}s windows")
    print(f"[fingerprint-service] Writing to {FINGERPRINT_LOG}")

    def callback(ch, method, properties, body):
        msg = decode_json(body)

        if method.routing_key == "market.snapshot":
            handle_snapshot(msg)
        elif method.routing_key == "trade.executed":
            handle_trade(msg)

        maybe_flush()

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("[fingerprint-service] Final flush before stopping...")
        flush_fingerprints()
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == "__main__":
    main()
