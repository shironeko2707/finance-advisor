"""
RabbitMQ consumer for Qlib prediction results.
"""
import pika
import json
import os
import logging
import threading
from typing import Optional

from config.database import SessionLocal
from .prediction_service import PredictionService

logger = logging.getLogger(__name__)


class QlibPredictionConsumer:
    """
    Consumer for listening to Qlib prediction ready messages.
    """

    def __init__(self):
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self.consumer_thread: Optional[threading.Thread] = None
        self.is_consuming = False

        # RabbitMQ configuration
        self.host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.username = os.getenv('RABBITMQ_DEFAULT_USER', 'rabbitmq')
        self.password = os.getenv('RABBITMQ_DEFAULT_PASS', 'rabbitmq')
        self.virtual_host = os.getenv('RABBITMQ_VHOST', '/lengkeng')

        # Queue configuration
        self.queue_name = os.getenv('QUEUE_QLIB_PREDICTIONS_READY', 'qlib_predictions_ready')
        self.exchange_name = os.getenv('EXCHANGE_NAME', 'khengleong.direct')

    def connect(self) -> bool:
        """Establish connection to RabbitMQ."""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )

            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # Declare exchange (idempotent)
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='direct',
                durable=True
            )

            # Declare queue (idempotent)
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )

            # Bind queue to exchange
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key=self.queue_name
            )

            # Set QoS - process one message at a time
            self.channel.basic_qos(prefetch_count=1)

            logger.info(
                f"Successfully connected to RabbitMQ at {self.host}:{self.port}, "
                f"queue: {self.queue_name}"
            )
            return True

        except pika.exceptions.ProbableAuthenticationError as e:
            logger.error(f"RabbitMQ authentication failed: {e}")
            return False
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to RabbitMQ: {e}")
            return False

    def callback(self, ch, method, properties, body):
        """
        Callback function for processing messages.

        Args:
            ch: Channel
            method: Delivery method
            properties: Message properties
            body: Message body
        """
        try:
            logger.info(f"Received prediction message: {body[:200]}...")

            # Parse message
            message_data = json.loads(body.decode())
            request_id = message_data.get("request_id", "unknown")

            logger.info(f"Processing prediction for request_id={request_id}")

            # Create database session
            db = SessionLocal()

            try:
                # Process message
                service = PredictionService(db)
                success = service.process_qlib_prediction_message(message_data)

                if success:
                    # Acknowledge message
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"Successfully processed and stored predictions for request_id={request_id}")
                else:
                    # Reject and requeue (will go to DLQ if configured)
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    logger.error(f"Failed to process prediction for request_id={request_id}")

            finally:
                db.close()

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message: {e}")
            # Reject invalid messages without requeue
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            logger.error(f"Error processing prediction message: {e}", exc_info=True)
            # Reject and don't requeue (send to DLQ)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start_consuming(self):
        """Start consuming messages."""
        if not self.connection or self.connection.is_closed:
            if not self.connect():
                logger.error("Cannot start consuming: Connection failed")
                return False

        try:
            logger.info(f"Starting to consume from queue: {self.queue_name}")

            # Start consuming
            self.is_consuming = True
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback,
                auto_ack=False  # Manual acknowledgment
            )

            logger.info("Qlib Prediction Consumer is ready and waiting for messages...")
            self.channel.start_consuming()

        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"Error in consumer: {e}", exc_info=True)
            self.is_consuming = False
            return False

        return True

    def start_consuming_async(self):
        """Start consuming in a background thread."""
        if self.consumer_thread and self.consumer_thread.is_alive():
            logger.warning("Consumer thread is already running")
            return False

        def run_consumer():
            try:
                self.start_consuming()
            except Exception as e:
                logger.error(f"Consumer thread error: {e}", exc_info=True)

        self.consumer_thread = threading.Thread(target=run_consumer, daemon=True)
        self.consumer_thread.start()
        logger.info("Started Qlib prediction consumer in background thread")
        return True

    def stop_consuming(self):
        """Stop consuming messages."""
        try:
            self.is_consuming = False

            if self.channel and not self.channel.is_closed:
                self.channel.stop_consuming()
                logger.info("Stopped consuming messages")

            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Closed RabbitMQ connection")

        except Exception as e:
            logger.error(f"Error stopping consumer: {e}")


# Global consumer instance
prediction_consumer = QlibPredictionConsumer()


def get_prediction_consumer() -> QlibPredictionConsumer:
    """Get the global prediction consumer instance."""
    return prediction_consumer


def start_prediction_consumer_background():
    """
    Start the prediction consumer in the background.
    This should be called during application startup.
    """
    try:
        consumer = get_prediction_consumer()
        consumer.start_consuming_async()
        logger.info("Qlib prediction consumer started successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to start prediction consumer: {e}")
        return False
