from shared.libs.mq import setup_channel, decode_json

def main():
    connection, channel = setup_channel()

    queue = "trade_monitor.queue"
    channel.queue_declare(queue=queue, durable=True)

    channel.queue_bind(
        exchange="metaml.events",
        queue=queue,
        routing_key="trade.executed"
    )

    print("[trade-monitor] Waiting for executed trades...")

    def callback(ch, method, properties, body):
        trade = decode_json(body)
        print(
            f"[trade-monitor] TRADE "
            f"symbol={trade['symbol']} "
            f"price={trade['price']} "
            f"qty={trade['quantity']} "
            f"buyer={trade['buyer_bot_id']} "
            f"seller={trade['seller_bot_id']}"
        )

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("[trade-monitor] Stopping...")
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == "__main__":
    main()
