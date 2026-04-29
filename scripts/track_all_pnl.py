from collections import defaultdict

from shared.libs.mq import setup_channel, decode_json

INITIAL_CASH = 100000.0

cash = defaultdict(lambda: INITIAL_CASH)
position = defaultdict(float)
last_mid_price = {}

known_bots = set()

def mark_to_market(bot_id, symbol="AAPL"):
    mid = last_mid_price.get(symbol)
    if mid is None:
        return cash[bot_id]
    return cash[bot_id] + position[bot_id] * mid

def handle_snapshot(snapshot):
    symbol = snapshot["symbol"]
    last_mid_price[symbol] = float(snapshot["mid_price"])

def update_bot_for_trade(bot_id, side, price, qty):
    known_bots.add(bot_id)

    if side == "BUY":
        position[bot_id] += qty
        cash[bot_id] -= price * qty
    elif side == "SELL":
        position[bot_id] -= qty
        cash[bot_id] += price * qty

def handle_trade(trade):
    price = float(trade["price"])
    qty = float(trade["quantity"])

    buyer = trade["buyer_bot_id"]
    seller = trade["seller_bot_id"]

    if buyer != "simulated-liquidity-provider":
        update_bot_for_trade(buyer, "BUY", price, qty)

    if seller != "simulated-liquidity-provider":
        update_bot_for_trade(seller, "SELL", price, qty)

    print("\n[pnl-tracker] Current Bot PnL")
    print("-" * 72)

    for bot_id in sorted(known_bots):
        equity = mark_to_market(bot_id, trade["symbol"])
        pnl = equity - INITIAL_CASH

        print(
            f"{bot_id:24s} "
            f"cash={cash[bot_id]:10.2f} "
            f"pos={position[bot_id]:8.2f} "
            f"equity={equity:10.2f} "
            f"pnl={pnl:8.2f}"
        )

    print("-" * 72)

def main():
    connection, channel = setup_channel()

    queue = "all_bots.pnl.queue"
    channel.queue_declare(queue=queue, durable=True)

    channel.queue_bind(exchange="metaml.events", queue=queue, routing_key="market.snapshot")
    channel.queue_bind(exchange="metaml.events", queue=queue, routing_key="trade.executed")

    print("[pnl-tracker] Tracking PnL for all bots...")

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
