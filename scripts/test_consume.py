import os
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
queue = "metaml.test.queue"
routing_key = "orders.*"

channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
channel.queue_declare(queue=queue, durable=True)
channel.queue_bind(exchange=exchange, queue=queue, routing_key=routing_key)

print("Waiting for test messages. Press CTRL+C to stop.")

def callback(ch, method, properties, body):
    print("Received message:")
    print(body.decode())

channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping consumer...")
    channel.stop_consuming()
    connection.close()
