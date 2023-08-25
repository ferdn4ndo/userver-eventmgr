import json
import os

import pika
from django.core.serializers.json import DjangoJSONEncoder


class MessageBrokerService:

    def __init__(self):
        self.channel = None
        self.connection = None
        self.exchange_name = os.getenv('EVENT_EXCHANGE_NAME', 'userver-filemgr')

    def prepare_connection(self):
        if self.channel is not None and self.connection is not None:
            return

        connection_params = pika.ConnectionParameters(
            host=os.getenv('RABBITMQ_HOST', 'userver-rabbitmq'),
            port=int(os.getenv('RABBITMQ_PORT', '5672')),
            credentials=pika.credentials.PlainCredentials(
                username=os.getenv('RABBITMQ_USERNAME', 'guest'),
                password=os.getenv('RABBITMQ_PASSWORD', 'guest'),
            ),
        )
        self.connection = pika.BlockingConnection(connection_params)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type='topic')

    def send_message(self, topic: str, payload: dict):
        self.prepare_connection()

        encoded_message = json.dumps(payload, cls=DjangoJSONEncoder)

        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=f"{self.exchange_name}.{topic}",
            body=encoded_message,
        )

        self.connection.close()
