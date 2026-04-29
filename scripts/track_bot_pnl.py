from shared.libs.mq import setup_channel, decode_json

BOT_ID = "baseline-bot"

cash = 100000.0
position = 0.0
last_mid_price = None

def mark_to_market():
    if last_mid_price is None:
        return cash

    return cash + position * last_mid_price

def handle_snapshot(snapshot):
    global last_mid_price
    last_mid_price = float(snapshot["mid_price"])

def handle_trade(trade):
    global cash, position

    price = float(trade["price"])
    qty = float(trade["quantity"])

    if trade["buyer_bot_id"] == BOT_ID:
        position += qty
        cash -= price * qty

    if trade["seller_bot_id"] == BOT_ID:
        position -= qty
        cash += price * qty

    equity = mark_to_market()

    print(
        f"[pnl-tracker] bot={BOT_ID} "
        f"cash={cash:.2f} position={position:.2f} "
        f"last_mid={last_mid_price} equity={equity:.2f}"
    )

def main():
    connection, channel = setup_channel()

    queue = f"{BOT_ID}.pnl.queue"
    channel.queue_declare(queue=queue, durable=True)

    channel.queue_bind(exchange="metaml.events", queue=queue, routing_key="market.snapshot")
    channel.queue_bind(exchange="metaml.events", queue=queue, routing_key="trade.executed")

    print(f"[pnl-tracker] Tracking PnL for {BOT_ID}")

    def callback(ch, method, properties, body):
        msg = decode_json(body)

        if method.routing_key == "market.snapshot":
            handle_snapshot(msg)
        elif method.routing_key == "trade.executed":
            handle_trade(msg)

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("[pnl-tracker] Stopping...")
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == "__main__":
    main()
