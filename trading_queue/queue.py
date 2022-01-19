import os
import sys
import time
import pika

QUEUE_HOST = os.environ.get("QUEUE_HOST", "rabbitmq")
RETRIES = 10
TIME_BETWEEN_RETRIES = 5


class QueueClient(object):
    def __init__(self):
        self.connection = self.create_connection()

    def create_connection(self):
        for _ in range(RETRIES):
            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=QUEUE_HOST)
                )
            except Exception:
                print("queue isn't ready yet, waiting and retrying...", file=sys.stderr)
                time.sleep(TIME_BETWEEN_RETRIES)
        if not connection:
            sys.exit(1)
        return connection

    def create_channel(self):
        channel = self.connection.channel()
        return channel

    def create_trading_channel(self, queue="trades"):
        try:
            channel = self.create_channel(self.connection)
        except Exception:
            # try recreating the connection
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=QUEUE_HOST)
            )
            channel = self.create_channel()
            # if it fails to even create it, then the queue might be down, don't keep trying
        channel.queue_declare(queue=queue)
        return channel

    def create_trading_consumer(self, handler, queue="trades"):
        channel = self.create_trading_channel()
        channel.basic_consume(queue=queue, auto_ack=True, on_message_callback=handler)
        channel.start_consuming()

    def send_on_channel(self, msg, channel, queue="trades"):
        channel.basic_publish(exchange="", routing_key=queue, body=msg)
