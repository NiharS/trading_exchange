import os
import sys
import time
from venv import create
import pika

QUEUE_HOST = os.environ.get("QUEUE_HOST", "rabbitmq")
RETRIES = 10
TIME_BETWEEN_RETRIES = 5

def create_connection():
    for _ in range(RETRIES):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=QUEUE_HOST))
        except Exception:
            print("queue isn't ready yet, waiting and retrying...", file=sys.stderr)
            time.sleep(TIME_BETWEEN_RETRIES)
    if not connection:
        sys.exit(1)
    return connection

def create_channel(connection):
    channel = connection.channel()
    return channel

def create_trading_channel(connection, queue="trades"):
    channel = create_channel(connection)
    channel.queue_declare(queue=queue)
    return channel

def create_trading_consumer(connection, handler, queue="trades"):
    channel = create_trading_channel(connection)
    channel.basic_consume(queue=queue, auto_ack=True, on_message_callback=handler)
    channel.start_consuming()

def send_on_channel(msg, channel, queue="trades"):
    channel.basic_publish(exchange="", routing_key=queue, body=msg)

