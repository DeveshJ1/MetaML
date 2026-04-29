import csv
import os

from shared.libs.mq import setup_channel, decode_json

LOG_PATH = "data/logs/trades.csv"

FIELDS = [
    "trade_id",
    "symbol",
    "price",
    "quantity",
    "buyer_bot_id",
    "seller_bot_id",
    "source_order_id",
    "order_type",
    "market_regime",
    "mid_price",
    "spread",
    "timestamp"
]

def ensure_log_file():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()

def append_trade(trade):
    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writerow({field: trade.get(field) for field in FIELDS})

def main():
    ensure_log_file()

    connection, channel = setup_channel()

    queue = "trade_logger.queue"
    channel.queue_declare(queue=queue, durable=True)
    channel.queue_bind(exchange="metaml.events", queue=queue, routing_key="trade.executed")

    print(f"[trade-logger] Logging trades to {LOG_PATH}")

    def callback(ch, method, properties, body):
        trade = decode_json(body)
        append_trade(trade)
        print(
            f"[trade-logger] Logged trade "
            f"{trade['symbol']} price={trade['price']} qty={trade['quantity']}"
        )

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("[trade-logger] Stopping...")
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == "__main__":
    main()
