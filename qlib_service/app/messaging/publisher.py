"""
RabbitMQ publisher for sending prediction results.
"""
import json
import aio_pika
from aio_pika import Message, DeliveryMode, ExchangeType
from typing import Optional
from datetime import datetime
from loguru import logger

from app.config.settings import settings
from app.models.schemas import QlibPredictionsReadyMessage


class RabbitMQPublisher:
    """Publisher for sending messages to RabbitMQ."""

    def __init__(self):
        """Initialize the publisher."""
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self.connected = False
        logger.info("RabbitMQPublisher initialized")

    async def connect(self) -> bool:
        """
        Establish connection to RabbitMQ.

        Returns:
            True if connection successful
        """
        try:
            logger.info(f"Connecting to RabbitMQ at {settings.rabbitmq_host}:{settings.rabbitmq_port}")

            # Create connection
            self.connection = await aio_pika.connect_robust(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                login=settings.rabbitmq_username,
                password=settings.rabbitmq_password,
                virtualhost=settings.rabbitmq_vhost,
                heartbeat=settings.rabbitmq_heartbeat,
            )

            # Create channel
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=settings.consumer_prefetch_count)

            # Declare exchange
            self.exchange = await self.channel.declare_exchange(
                name=settings.exchange_name,
                type=ExchangeType.DIRECT,
                durable=True,
            )

            # Declare output queue
            queue = await self.channel.declare_queue(
                name=settings.queue_qlib_predictions_ready,
                durable=True,
            )

            # Bind queue to exchange
            await queue.bind(
                exchange=self.exchange,
                routing_key=settings.queue_qlib_predictions_ready,
            )

            # Declare DLQ
            dlq = await self.channel.declare_queue(
                name=settings.queue_dlq,
                durable=True,
            )

            await dlq.bind(
                exchange=self.exchange,
                routing_key=settings.queue_dlq,
            )

            self.connected = True
            logger.info("Successfully connected to RabbitMQ and declared queues/exchanges")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self.connected = False
            return False

    async def publish_predictions(
        self,
        message: QlibPredictionsReadyMessage,
        routing_key: Optional[str] = None
    ) -> bool:
        """
        Publish prediction results to RabbitMQ.

        Args:
            message: Prediction results message
            routing_key: Optional routing key (defaults to predictions queue)

        Returns:
            True if published successfully
        """
        if not self.connected or not self.exchange:
            logger.error("Cannot publish: Not connected to RabbitMQ")
            return False

        try:
            routing_key = routing_key or settings.queue_qlib_predictions_ready

            # Serialize message
            message_body = message.model_dump_json()

            # Create message
            aio_message = Message(
                body=message_body.encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json",
                headers={
                    "request_id": message.request_id,
                    "report_id": message.report_id,
                    "prediction_status": message.prediction_status,
                }
            )

            # Publish to exchange
            await self.exchange.publish(
                message=aio_message,
                routing_key=routing_key,
            )

            logger.info(
                f"Published predictions for request {message.request_id} "
                f"to queue {routing_key}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return False

    async def publish_to_dlq(
        self,
        original_message: dict,
        error_message: str
    ) -> bool:
        """
        Publish failed message to Dead Letter Queue.

        Args:
            original_message: Original message that failed
            error_message: Error description

        Returns:
            True if published successfully
        """
        if not self.connected or not self.exchange:
            logger.error("Cannot publish to DLQ: Not connected to RabbitMQ")
            return False

        try:
            dlq_payload = {
                "original_message": original_message,
                "error": error_message,
                "timestamp": json.dumps({"$date": {"$numberLong": str(int(datetime.now().timestamp() * 1000))}})
            }

            aio_message = Message(
                body=json.dumps(dlq_payload).encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json",
            )

            await self.exchange.publish(
                message=aio_message,
                routing_key=settings.queue_dlq,
            )

            logger.warning(f"Published failed message to DLQ: {error_message}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish to DLQ: {e}")
            return False

    async def disconnect(self):
        """Close RabbitMQ connection."""
        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logger.info("Disconnected from RabbitMQ")
            self.connected = False
        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ: {e}")


# Global publisher instance
publisher = RabbitMQPublisher()
