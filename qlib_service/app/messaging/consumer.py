"""
RabbitMQ consumer for processing AI extraction complete messages.
"""
import json
import asyncio
import aio_pika
from aio_pika import Message, ExchangeType, IncomingMessage
from typing import Optional
from datetime import datetime
from loguru import logger

from app.config.settings import settings
from app.models.schemas import (
    AIExtractionCompleteMessage,
    QlibPredictionsReadyMessage,
    PredictionData,
    ModelMetadata,
    StockPrediction,
    PortfolioAnalysis,
    Recommendation,
    MarketRegime,
)
from app.services.forecasting import ForecastingService
from app.services.portfolio_analysis import PortfolioAnalysisService
from app.services.recommendation import RecommendationService
from app.messaging.publisher import publisher


class RabbitMQConsumer:
    """Consumer for processing AI extraction complete messages."""

    def __init__(self):
        """Initialize the consumer."""
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.queue: Optional[aio_pika.Queue] = None
        self.running = False

        # Initialize services
        self.forecasting_service = ForecastingService()
        self.portfolio_service = PortfolioAnalysisService()
        self.recommendation_service = RecommendationService()

        logger.info("RabbitMQConsumer initialized")

    async def connect(self) -> bool:
        """
        Establish connection to RabbitMQ and start consuming.

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
            exchange = await self.channel.declare_exchange(
                name=settings.exchange_name,
                type=ExchangeType.DIRECT,
                durable=True,
            )

            # Declare queue
            self.queue = await self.channel.declare_queue(
                name=settings.queue_ai_extraction_complete,
                durable=True,
            )

            # Bind queue to exchange
            await self.queue.bind(
                exchange=exchange,
                routing_key=settings.queue_ai_extraction_complete,
            )

            logger.info(f"Successfully connected and bound to queue: {settings.queue_ai_extraction_complete}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False

    async def start_consuming(self):
        """Start consuming messages from the queue."""
        if not self.queue:
            logger.error("Cannot start consuming: Queue not initialized")
            return

        try:
            self.running = True
            logger.info(f"Started consuming from queue: {settings.queue_ai_extraction_complete}")

            # Start consuming
            await self.queue.consume(self._process_message)

        except Exception as e:
            logger.error(f"Error in consumer: {e}")
            self.running = False

    async def _process_message(self, message: IncomingMessage):
        """
        Process incoming message from queue.

        Args:
            message: Incoming RabbitMQ message
        """
        async with message.process():
            try:
                # Parse message
                body = message.body.decode()
                logger.info(f"Received message: {body[:200]}...")

                message_data = json.loads(body)
                extraction_message = AIExtractionCompleteMessage(**message_data)

                logger.info(
                    f"Processing extraction for request_id={extraction_message.request_id}, "
                    f"report_id={extraction_message.report_id}"
                )

                # Process the extraction
                prediction_message = await self._process_extraction(extraction_message)

                # Publish prediction results
                if prediction_message:
                    success = await publisher.publish_predictions(prediction_message)
                    if success:
                        logger.info(
                            f"Successfully processed and published predictions for "
                            f"request_id={extraction_message.request_id}"
                        )
                    else:
                        logger.error(
                            f"Failed to publish predictions for "
                            f"request_id={extraction_message.request_id}"
                        )
                        # Publish to DLQ
                        await publisher.publish_to_dlq(
                            message_data,
                            "Failed to publish predictions"
                        )

            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                # Try to publish to DLQ
                try:
                    await publisher.publish_to_dlq(
                        json.loads(message.body.decode()),
                        f"Processing error: {str(e)}"
                    )
                except Exception as dlq_error:
                    logger.error(f"Failed to publish to DLQ: {dlq_error}")

    async def _process_extraction(
        self,
        extraction_message: AIExtractionCompleteMessage
    ) -> Optional[QlibPredictionsReadyMessage]:
        """
        Process extraction and generate predictions.

        Args:
            extraction_message: AI extraction complete message

        Returns:
            Prediction results message or None if processing failed
        """
        start_time = datetime.now()

        try:
            extracted_data = extraction_message.extracted_data

            # Check if extraction was successful
            if extraction_message.extraction_status not in ["success", "partial"]:
                logger.warning(
                    f"Extraction failed for request {extraction_message.request_id}, "
                    f"status={extraction_message.extraction_status}"
                )
                return self._create_error_message(
                    extraction_message,
                    "AI extraction failed",
                    start_time
                )

            # Initialize result containers
            stock_forecasts = []
            portfolio_analysis = None
            recommendations = []

            # 1. Generate stock forecasts
            if settings.enable_forecasting and extracted_data.stocks:
                logger.info(f"Generating forecasts for {len(extracted_data.stocks)} stocks")

                for stock_data in extracted_data.stocks:
                    try:
                        forecast = await self.forecasting_service.predict_stock_price(stock_data)
                        stock_forecasts.append(forecast)
                        logger.debug(f"Generated forecast for {stock_data.ticker}")
                    except Exception as e:
                        logger.error(f"Failed to forecast {stock_data.ticker}: {e}")
                        # Continue with other stocks

            # 2. Generate portfolio analysis
            if settings.enable_portfolio_analysis and extracted_data.portfolio:
                logger.info("Generating portfolio analysis")

                try:
                    portfolio_analysis = await self.portfolio_service.analyze_portfolio(
                        portfolio=extracted_data.portfolio,
                        stocks_data=extracted_data.stocks,
                        market_context=extracted_data.market_context
                    )
                    logger.debug("Generated portfolio analysis")
                except Exception as e:
                    logger.error(f"Failed to analyze portfolio: {e}")

            # 3. Generate recommendations
            if settings.enable_recommendations and extracted_data.stocks:
                logger.info(f"Generating recommendations for {len(extracted_data.stocks)} stocks")

                try:
                    recommendations = await self.recommendation_service.generate_recommendations(
                        stocks_data=extracted_data.stocks,
                        portfolio=extracted_data.portfolio,
                        market_context=extracted_data.market_context,
                        stock_forecasts=stock_forecasts
                    )
                    logger.debug(f"Generated {len(recommendations)} recommendations")
                except Exception as e:
                    logger.error(f"Failed to generate recommendations: {e}")

            # 4. Detect market regime
            try:
                market_regime = await self.recommendation_service.detect_market_regime(
                    extracted_data.stocks
                )
            except Exception as e:
                logger.warning(f"Failed to detect market regime: {e}")
                market_regime = MarketRegime(
                    regime="unknown",
                    confidence=0.0,
                    description="Market regime detection failed"
                )

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Create prediction data
            prediction_data = PredictionData(
                stock_forecasts=stock_forecasts,
                portfolio_analysis=portfolio_analysis,
                recommendations=recommendations,
                market_regime=market_regime
            )

            # Create model metadata
            model_metadata = ModelMetadata(
                primary_model=settings.qlib_default_model,
                model_version="1.0.0",
                training_date=datetime.now().date(),
                feature_set=settings.qlib_feature_set,
                processing_time_seconds=processing_time
            )

            # Determine overall status
            if stock_forecasts or portfolio_analysis or recommendations:
                prediction_status = "success"
            elif extracted_data.stocks:
                prediction_status = "partial_success"
            else:
                prediction_status = "failed"

            # Create response message
            response_message = QlibPredictionsReadyMessage(
                request_id=extraction_message.request_id,
                report_id=extraction_message.report_id,
                timestamp=datetime.now(),
                prediction_status=prediction_status,
                predictions=prediction_data,
                model_metadata=model_metadata,
                error_message=None
            )

            logger.info(
                f"Completed predictions for request {extraction_message.request_id} "
                f"in {processing_time:.2f}s with status={prediction_status}"
            )

            return response_message

        except Exception as e:
            logger.error(f"Error processing extraction: {e}", exc_info=True)
            processing_time = (datetime.now() - start_time).total_seconds()
            return self._create_error_message(
                extraction_message,
                f"Processing error: {str(e)}",
                start_time
            )

    def _create_error_message(
        self,
        extraction_message: AIExtractionCompleteMessage,
        error: str,
        start_time: datetime
    ) -> QlibPredictionsReadyMessage:
        """
        Create an error response message.

        Args:
            extraction_message: Original extraction message
            error: Error description
            start_time: Processing start time

        Returns:
            Error response message
        """
        processing_time = (datetime.now() - start_time).total_seconds()

        model_metadata = ModelMetadata(
            primary_model=settings.qlib_default_model,
            model_version="1.0.0",
            training_date=datetime.now().date(),
            feature_set=settings.qlib_feature_set,
            processing_time_seconds=processing_time
        )

        return QlibPredictionsReadyMessage(
            request_id=extraction_message.request_id,
            report_id=extraction_message.report_id,
            timestamp=datetime.now(),
            prediction_status="failed",
            predictions=None,
            model_metadata=model_metadata,
            error_message=error
        )

    async def stop_consuming(self):
        """Stop consuming messages."""
        self.running = False
        logger.info("Consumer stopped")

    async def disconnect(self):
        """Close RabbitMQ connection."""
        try:
            await self.stop_consuming()

            if self.connection and not self.connection.is_closed:
                await self.connection.close()
                logger.info("Disconnected from RabbitMQ")
        except Exception as e:
            logger.error(f"Error disconnecting from RabbitMQ: {e}")


# Global consumer instance
consumer = RabbitMQConsumer()
