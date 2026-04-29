import json
import os
from datetime import datetime, timezone

import pika
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("RABBITMQ_HOST", "localhost")
port = int(os.getenv("RABBITMQ_PORT", "5672"))
user = os.getenv("RABBITMQ_USER", "metaml")
password = os.getenv("RABBITMQ_PASSWORD", "metaml")

credentials = pika.PlainCredentials(user, password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=host, port=port, credentials=credentials)
)
channel = connection.channel()

exchange = "metaml.events"
routing_key = "orders.test"

channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)

message = {
    "order_id": "test-order-001",
    "bot_id": "baseline-bot",
    "symbol": "AAPL",
    "side": "BUY",
    "quantity": 10,
    "price": 100.0,
    "order_type": "LIMIT",
    "timestamp": datetime.now(timezone.utc).isoformat()
}

channel.basic_publish(
    exchange=exchange,
    routing_key=routing_key,
    body=json.dumps(message),
)

print("Published test order:")
print(json.dumps(message, indent=2))

connection.close()
