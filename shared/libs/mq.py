import json
import os
import pika
from dotenv import load_dotenv

load_dotenv()

EXCHANGE = "metaml.events"

def get_connection():
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    user = os.getenv("RABBITMQ_USER", "metaml")
    password = os.getenv("RABBITMQ_PASSWORD", "metaml")

    credentials = pika.PlainCredentials(user, password)
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
    )

def setup_channel():
    connection = get_connection()
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    return connection, channel

def publish_json(channel, routing_key, payload):
    channel.basic_publish(
        exchange=EXCHANGE,
        routing_key=routing_key,
        body=json.dumps(payload),
        properties=pika.BasicProperties(content_type="application/json")
    )

def decode_json(body):
    return json.loads(body.decode("utf-8"))
