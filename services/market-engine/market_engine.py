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
        f"[market-engine] Snapshot "
        f"{snapshot['symbol']} mid={snapshot['mid_price']} "
        f"bid={snapshot['best_bid']} ask={snapshot['best_ask']} "
        f"regime={snapshot['regime']}"
    )

def should_execute_limit(order, snapshot):
    side = order["side"]
    limit_price = order.get("price")

    if limit_price is None:
        return False

    limit_price = float(limit_price)

    if side == "BUY":
        return limit_price >= float(snapshot["best_ask"])
    else:
        return limit_price <= float(snapshot["best_bid"])

def get_execution_price(order, snapshot):
    side = order["side"]
    order_type = order["order_type"]

    if order_type == "MARKET":
        return snapshot["best_ask"] if side == "BUY" else snapshot["best_bid"]

    if order_type == "LIMIT":
        if should_execute_limit(order, snapshot):
            return snapshot["best_ask"] if side == "BUY" else snapshot["best_bid"]
        return None

    return None

def execute_order(channel, order):
    if not latest_snapshot:
        print("[market-engine] No market snapshot yet. Ignoring order.")
        return

    symbol = order["symbol"]

    if symbol != latest_snapshot["symbol"]:
        print(f"[market-engine] Symbol mismatch. order={symbol}, market={latest_snapshot['symbol']}")
        return

    execution_price = get_execution_price(order, latest_snapshot)

    if execution_price is None:
        print(
            f"[market-engine] LIMIT order not filled: "
            f"{order['side']} limit={order.get('price')} "
            f"bid={latest_snapshot['best_bid']} ask={latest_snapshot['best_ask']}"
        )
        return

    side = order["side"]
    quantity = float(order["quantity"])

    if side == "BUY":
        buyer = order["bot_id"]
        seller = "simulated-liquidity-provider"
    else:
        buyer = "simulated-liquidity-provider"
        seller = order["bot_id"]

    trade = {
        "trade_id": str(uuid.uuid4()),
        "symbol": symbol,
        "price": float(execution_price),
        "quantity": quantity,
        "buyer_bot_id": buyer,
        "seller_bot_id": seller,
        "source_order_id": order["order_id"],
        "order_type": order["order_type"],
        "market_regime": latest_snapshot["regime"],
        "mid_price": latest_snapshot["mid_price"],
        "spread": latest_snapshot["spread"],
        "timestamp": utc_now()
    }

    publish_json(channel, "trade.executed", trade)

    print(
        f"[market-engine] EXECUTED {side} "
        f"bot={order['bot_id']} qty={quantity} "
        f"price={execution_price} type={order['order_type']}"
    )

def main():
    connection, channel = setup_channel()

    queue = "market_engine.queue"
    channel.queue_declare(queue=queue, durable=True)

    channel.queue_bind(exchange="metaml.events", queue=queue, routing_key="market.snapshot")
    channel.queue_bind(exchange="metaml.events", queue=queue, routing_key="orders.new")

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
