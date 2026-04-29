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
    order_type = random.choice(["MARKET", "LIMIT"])

    price = None

    if order_type == "LIMIT":
        if side == "BUY":
            # Sometimes aggressive, sometimes passive.
            price = round(snapshot["best_ask"] if random.random() < 0.5 else snapshot["best_bid"], 2)
        else:
            price = round(snapshot["best_bid"] if random.random() < 0.5 else snapshot["best_ask"], 2)

    return {
        "order_id": str(uuid.uuid4()),
        "bot_id": BOT_ID,
        "symbol": SYMBOL,
        "side": side,
        "quantity": random.choice([1, 2, 5, 10]),
        "price": price,
        "order_type": order_type,
        "timestamp": utc_now()
    }

def main():
    connection, channel = setup_channel()

    queue = f"{BOT_ID}.market.queue"
    channel.queue_declare(queue=queue, durable=True)
    channel.queue_bind(exchange="metaml.events", queue=queue, routing_key="market.snapshot")

    print(f"[{BOT_ID}] Waiting for market snapshots...")

    def callback(ch, method, properties, body):
        snapshot = decode_json(body)

        print(
            f"[{BOT_ID}] Snapshot "
            f"mid={snapshot['mid_price']} "
            f"bid={snapshot['best_bid']} ask={snapshot['best_ask']} "
            f"regime={snapshot['regime']}"
        )

        if random.random() < 0.40:
            order = make_order(snapshot)
            publish_json(channel, "orders.new", order)

            print(
                f"[{BOT_ID}] Sent {order['order_type']} order: "
                f"{order['side']} qty={order['quantity']} price={order['price']}"
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
