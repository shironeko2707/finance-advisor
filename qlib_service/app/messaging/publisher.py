"""
RabbitMQ publisher for sending Qlib predictions to downstream services.
"""
import json
import aio_pika
from typing import Dict, Any
from loguru import logger

from app.config.settings import settings


class QlibPublisher:
    """Publisher for Qlib prediction results."""

    def __init__(self):
        """Initialize the publisher."""
        self.connection = None
        self.channel = None
        self.exchange = None
        logger.info("QlibPublisher initialized")

    async def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            logger.info(f"Connecting to RabbitMQ at {settings.rabbitmq_host}:{settings.rabbitmq_port}")

            self.connection = await aio_pika.connect_robust(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                login=settings.rabbitmq_username,
                password=settings.rabbitmq_password,
                virtualhost=settings.rabbitmq_vhost,
                heartbeat=settings.rabbitmq_heartbeat,
            )

            self.channel = await self.connection.channel()

            # Declare exchange
            self.exchange = await self.channel.declare_exchange(
                name=settings.exchange_name,
                type=aio_pika.ExchangeType.DIRECT,
                durable=True,
            )

            # Declare output queue
            await self.channel.declare_queue(
                name=settings.queue_qlib_predictions_ready,
                durable=True,
            )

            logger.info("✓ Publisher connected to RabbitMQ")
            return True

        except Exception as e:
            logger.error(f"Failed to connect publisher to RabbitMQ: {str(e)}")
            return False

    async def publish_predictions(self, predictions: Dict[str, Any]):
        """
        Publish Qlib predictions to output queue.

        Args:
            predictions: Prediction results to publish

        Returns:
            bool: True if published successfully
        """
        try:
            if not self.channel or self.channel.is_closed:
                logger.warning("Publisher channel closed, reconnecting...")
                await self.connect()

            # Convert to JSON
            message_body = json.dumps(predictions, default=str)

            # Create message
            message = aio_pika.Message(
                body=message_body.encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )

            # Publish to queue
            await self.exchange.publish(
                message,
                routing_key=settings.queue_qlib_predictions_ready,
            )

            logger.info(
                f"Published predictions for request_id={predictions.get('request_id')} "
                f"to queue={settings.queue_qlib_predictions_ready}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to publish predictions: {str(e)}")
            return False

    async def publish_error(self, request_id: str, error_message: str, original_data: Dict[str, Any] = None):
        """
        Publish error message to Dead Letter Queue.

        Args:
            request_id: Original request ID
            error_message: Error description
            original_data: Original request data (optional)

        Returns:
            bool: True if published successfully
        """
        try:
            if not self.channel or self.channel.is_closed:
                await self.connect()

            error_payload = {
                "request_id": request_id,
                "error": error_message,
                "status": "failed",
                "original_data": original_data,
            }

            message_body = json.dumps(error_payload, default=str)

            message = aio_pika.Message(
                body=message_body.encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )

            # Declare DLQ if not exists
            await self.channel.declare_queue(
                name=settings.queue_dlq,
                durable=True,
            )

            await self.exchange.publish(
                message,
                routing_key=settings.queue_dlq,
            )

            logger.warning(f"Published error for request_id={request_id} to DLQ")
            return True

        except Exception as e:
            logger.error(f"Failed to publish error: {str(e)}")
            return False

    async def close(self):
        """Close RabbitMQ connection."""
        try:
            if self.channel and not self.channel.is_closed:
                await self.channel.close()

            if self.connection and not self.connection.is_closed:
                await self.connection.close()

            logger.info("Publisher connection closed")

        except Exception as e:
            logger.error(f"Error closing publisher connection: {str(e)}")
