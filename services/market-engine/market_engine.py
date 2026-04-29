import uuid
from datetime import datetime, timezone

from shared.libs.mq import setup_channel, publish_json, decode_json

latest_snapshot = {}

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def handle_market_snapshot(snapshot):
    global latest_snapshot
    latest_snapshot = snapshot
    print(
        f"[market-engine] Updated market snapshot: "
        f"{snapshot['symbol']} mid={snapshot['mid_price']} regime={snapshot['regime']}"
    )

def execute_order(channel, order):
    if not latest_snapshot:
        print("[market-engine] No market snapshot yet. Ignoring order.")
        return

    side = order["side"]
    quantity = float(order["quantity"])

    if side == "BUY":
        execution_price = latest_snapshot["best_ask"]
        buyer = order["bot_id"]
        seller = "simulated-liquidity-provider"
    else:
        execution_price = latest_snapshot["best_bid"]
        buyer = "simulated-liquidity-provider"
        seller = order["bot_id"]

    trade = {
        "trade_id": str(uuid.uuid4()),
        "symbol": order["symbol"],
        "price": execution_price,
        "quantity": quantity,
        "buyer_bot_id": buyer,
        "seller_bot_id": seller,
        "source_order_id": order["order_id"],
        "timestamp": utc_now()
    }

    publish_json(channel, "trade.executed", trade)

    print(
        f"[market-engine] Executed {side} order from {order['bot_id']} "
        f"qty={quantity} price={execution_price}"
    )

def main():
    connection, channel = setup_channel()

    queue = "market_engine.queue"
    channel.queue_declare(queue=queue, durable=True)

    channel.queue_bind(
        exchange="metaml.events",
        queue=queue,
        routing_key="market.snapshot"
    )

    channel.queue_bind(
        exchange="metaml.events",
        queue=queue,
        routing_key="orders.new"
    )

    print("[market-engine] Waiting for market snapshots and orders...")

    def callback(ch, method, properties, body):
        message = decode_json(body)

        if method.routing_key == "market.snapshot":
            handle_market_snapshot(message)

        elif method.routing_key == "orders.new":
            execute_order(channel, message)

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("[market-engine] Stopping...")
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == "__main__":
    main()
