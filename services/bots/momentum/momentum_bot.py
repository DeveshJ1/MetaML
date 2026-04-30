from shared.libs.mq import setup_channel, publish_json, decode_json
from shared.libs.bot_utils import make_order, RollingWindow
from shared.libs.active_bot import is_active_bot, get_active_bot

BOT_ID = "momentum-bot"
SYMBOL = "AAPL"

PRICE_WINDOW = 4
TRADE_QTY = 3
THRESHOLD = 0.20

prices = RollingWindow(PRICE_WINDOW)

def main():
    connection, channel = setup_channel()

    queue = f"{BOT_ID}.market.queue"
    channel.queue_declare(queue=queue, durable=True)
    channel.queue_bind(exchange="metaml.events", queue=queue, routing_key="market.snapshot")

    print(f"[{BOT_ID}] Starting momentum strategy...")
    print(f"[{BOT_ID}] Will only trade when active_bot == {BOT_ID}")

    def callback(ch, method, properties, body):
        snapshot = decode_json(body)
        active_bot = get_active_bot()

        mid = float(snapshot["mid_price"])
        prices.add(mid)

        print(
            f"[{BOT_ID}] Snapshot mid={mid} "
            f"regime={snapshot['regime']} active_bot={active_bot}"
        )

        if not prices.ready():
            print(f"[{BOT_ID}] Waiting for enough price history...")
            return

        if not is_active_bot(BOT_ID):
            print(f"[{BOT_ID}] Idle: not currently active.")
            return

        price_change = prices.last() - prices.first()

        if price_change > THRESHOLD:
            side = "BUY"
        elif price_change < -THRESHOLD:
            side = "SELL"
        else:
            print(f"[{BOT_ID}] ACTIVE but no strong momentum. change={price_change:.2f}")
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
            f"[{BOT_ID}] ACTIVE: Momentum change={price_change:.2f}. "
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
