import random

from shared.libs.mq import setup_channel, publish_json, decode_json
from shared.libs.bot_utils import make_order

BOT_ID = "baseline-bot"
SYMBOL = "AAPL"

def main():
    connection, channel = setup_channel()

    queue = f"{BOT_ID}.market.queue"
    channel.queue_declare(queue=queue, durable=True)
    channel.queue_bind(exchange="metaml.events", queue=queue, routing_key="market.snapshot")

    print(f"[{BOT_ID}] Starting baseline random strategy...")

    def callback(ch, method, properties, body):
        snapshot = decode_json(body)

        print(
            f"[{BOT_ID}] Snapshot "
            f"mid={snapshot['mid_price']} regime={snapshot['regime']}"
        )

        if random.random() < 0.35:
            side = random.choice(["BUY", "SELL"])
            quantity = random.choice([1, 2, 5])

            order = make_order(
                bot_id=BOT_ID,
                symbol=SYMBOL,
                side=side,
                quantity=quantity,
                order_type="MARKET"
            )

            publish_json(channel, "orders.new", order)

            print(
                f"[{BOT_ID}] Sent MARKET order: "
                f"{side} qty={quantity}"
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
