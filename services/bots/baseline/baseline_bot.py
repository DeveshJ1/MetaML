import random
import uuid
from datetime import datetime, timezone

from shared.libs.mq import setup_channel, publish_json, decode_json

BOT_ID = "baseline-bot"
SYMBOL = "AAPL"

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def make_order(snapshot):
    side = random.choice(["BUY", "SELL"])

    return {
        "order_id": str(uuid.uuid4()),
        "bot_id": BOT_ID,
        "symbol": SYMBOL,
        "side": side,
        "quantity": random.choice([1, 2, 5, 10]),
        "price": None,
        "order_type": "MARKET",
        "timestamp": utc_now()
    }

def main():
    connection, channel = setup_channel()

    queue = f"{BOT_ID}.market.queue"
    channel.queue_declare(queue=queue, durable=True)

    channel.queue_bind(
        exchange="metaml.events",
        queue=queue,
        routing_key="market.snapshot"
    )

    print(f"[{BOT_ID}] Waiting for market snapshots...")

    def callback(ch, method, properties, body):
        snapshot = decode_json(body)

        # Only trade sometimes so output is readable.
        should_trade = random.random() < 0.35

        print(
            f"[{BOT_ID}] Snapshot received: "
            f"mid={snapshot['mid_price']} regime={snapshot['regime']}"
        )

        if should_trade:
            order = make_order(snapshot)
            publish_json(channel, "orders.new", order)

            print(
                f"[{BOT_ID}] Sent order: "
                f"{order['side']} qty={order['quantity']} symbol={order['symbol']}"
            )

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"[{BOT_ID}] Stopping...")
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == "__main__":
    main()
