from shared.libs.mq import setup_channel, publish_json, decode_json
from shared.libs.bot_utils import make_order, RollingWindow

BOT_ID = "mean-reversion-bot"
SYMBOL = "AAPL"

PRICE_WINDOW = 5
TRADE_QTY = 3
DEVIATION_THRESHOLD = 0.25

prices = RollingWindow(PRICE_WINDOW)

def main():
    connection, channel = setup_channel()

    queue = f"{BOT_ID}.market.queue"
    channel.queue_declare(queue=queue, durable=True)
    channel.queue_bind(exchange="metaml.events", queue=queue, routing_key="market.snapshot")

    print(f"[{BOT_ID}] Starting mean reversion strategy...")

    def callback(ch, method, properties, body):
        snapshot = decode_json(body)
        mid = float(snapshot["mid_price"])
        prices.add(mid)

        print(
            f"[{BOT_ID}] Snapshot mid={mid} "
            f"regime={snapshot['regime']}"
        )

        if not prices.ready():
            print(f"[{BOT_ID}] Waiting for enough price history...")
            return

        avg_price = prices.mean()
        deviation = mid - avg_price

        if deviation > DEVIATION_THRESHOLD:
            side = "SELL"
        elif deviation < -DEVIATION_THRESHOLD:
            side = "BUY"
        else:
            print(
                f"[{BOT_ID}] No strong mean-reversion signal. "
                f"deviation={deviation:.2f}"
            )
            return

        order = make_order(
            bot_id=BOT_ID,
            symbol=SYMBOL,
            side=side,
            quantity=TRADE_QTY,
            order_type="MARKET"
        )

        publish_json(channel, "orders.new", order)

        print(
            f"[{BOT_ID}] Mean-reversion signal deviation={deviation:.2f}. "
            f"Sent {side} qty={TRADE_QTY}"
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
