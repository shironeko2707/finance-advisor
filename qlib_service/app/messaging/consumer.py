"""
RabbitMQ consumer for processing AI extraction messages.
"""
import json
import asyncio
import aio_pika
from typing import Dict, Any
from loguru import logger
from datetime import datetime

from app.config.settings import settings
from app.models import schemas
from app.services.qlib_manager import QlibManager
from app.services.forecasting import ForecastingService
from app.services.portfolio_analysis import PortfolioAnalysisService
from app.services.recommendation import RecommendationService
from app.messaging.publisher import QlibPublisher


class QlibConsumer:
    """Consumer for AI extraction complete messages."""

    def __init__(self, qlib_manager: QlibManager):
        """
        Initialize the consumer.

        Args:
            qlib_manager: QlibManager instance
        """
        self.qlib_manager = qlib_manager
        self.publisher = QlibPublisher()
        self.connection = None
        self.channel = None
        self.queue = None
        self.running = False
        logger.info("QlibConsumer initialized")

    async def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            logger.info(f"Connecting consumer to RabbitMQ at {settings.rabbitmq_host}:{settings.rabbitmq_port}")

            self.connection = await aio_pika.connect_robust(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                login=settings.rabbitmq_username,
                password=settings.rabbitmq_password,
                virtualhost=settings.rabbitmq_vhost,
                heartbeat=settings.rabbitmq_heartbeat,
            )

            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=settings.consumer_prefetch_count)

            # Declare exchange
            exchange = await self.channel.declare_exchange(
                name=settings.exchange_name,
                type=aio_pika.ExchangeType.DIRECT,
                durable=True,
            )

            # Declare queue
            self.queue = await self.channel.declare_queue(
                name=settings.queue_ai_extraction_complete,
                durable=True,
            )

            # Bind queue to exchange
            await self.queue.bind(exchange, routing_key=settings.queue_ai_extraction_complete)

            logger.info("✓ Consumer connected to RabbitMQ")
            return True

        except Exception as e:
            logger.error(f"Failed to connect consumer to RabbitMQ: {str(e)}")
            return False

    async def process_message(self, message: aio_pika.IncomingMessage):
        """
        Process a single message from the queue.

        Args:
            message: Incoming RabbitMQ message
        """
        async with message.process():
            try:
                # Parse message
                message_data = json.loads(message.body.decode())
                logger.info(f"Received message: request_id={message_data.get('request_id')}")

                # Validate message structure
                ai_message = schemas.AIExtractionCompleteMessage(**message_data)

                # Check extraction status
                if ai_message.extraction_status == "failed":
                    logger.warning(f"Skipping failed extraction: {ai_message.request_id}")
                    await self.publisher.publish_error(
                        request_id=ai_message.request_id,
                        error_message="AI extraction failed",
                        original_data=message_data
                    )
                    return

                # Process predictions
                predictions = await self.generate_predictions(ai_message)

                # Publish results
                if predictions:
                    await self.publisher.publish_predictions(predictions)
                    logger.info(f"✓ Completed processing for request_id={ai_message.request_id}")
                else:
                    logger.error(f"Prediction generation failed for request_id={ai_message.request_id}")
                    await self.publisher.publish_error(
                        request_id=ai_message.request_id,
                        error_message="Prediction generation failed"
                    )

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in message: {str(e)}")
                await message.reject(requeue=False)

            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await self.publisher.publish_error(
                    request_id=message_data.get('request_id', 'unknown'),
                    error_message=str(e),
                    original_data=message_data
                )

    async def generate_predictions(self, ai_message: schemas.AIExtractionCompleteMessage) -> Dict[str, Any]:
        """
        Generate all predictions from extracted data.

        Args:
            ai_message: AI extraction complete message

        Returns:
            Dict with predictions or None if failed
        """
        try:
            logger.info(f"Generating predictions for request_id={ai_message.request_id}")

            extracted_data = ai_message.extracted_data
            stock_forecasts = []
            portfolio_analysis = None
            recommendations_list = []

            # 1. Generate stock forecasts
            if settings.enable_forecasting and extracted_data.stocks:
                logger.info(f"Forecasting {len(extracted_data.stocks)} stocks...")
                forecasting_service = ForecastingService(self.qlib_manager)

                for stock in extracted_data.stocks:
                    try:
                        # Create prediction request
                        pred_request = schemas.StockPredictionRequest(
                            ticker=stock.ticker,
                            historical_data=stock.prices,
                            market_context=extracted_data.market_context
                        )

                        # Generate forecast
                        forecast = await forecasting_service.forecast_stock(pred_request)
                        stock_forecasts.append(forecast.dict())

                    except Exception as e:
                        logger.warning(f"Failed to forecast {stock.ticker}: {str(e)}")

            # 2. Portfolio analysis
            if settings.enable_portfolio_analysis and extracted_data.portfolio:
                logger.info("Analyzing portfolio...")
                portfolio_service = PortfolioAnalysisService(self.qlib_manager)

                try:
                    analysis_request = schemas.PortfolioAnalysisRequest(
                        portfolio=extracted_data.portfolio,
                        market_context=extracted_data.market_context,
                        stocks_data=extracted_data.stocks
                    )

                    analysis = await portfolio_service.analyze_portfolio(analysis_request)
                    portfolio_analysis = analysis.dict()

                except Exception as e:
                    logger.warning(f"Portfolio analysis failed: {str(e)}")

            # 3. Generate recommendations
            if settings.enable_recommendations and extracted_data.stocks:
                logger.info("Generating recommendations...")
                recommendation_service = RecommendationService(self.qlib_manager)

                try:
                    rec_request = schemas.RecommendationRequest(
                        stocks=extracted_data.stocks,
                        portfolio=extracted_data.portfolio,
                        market_context=extracted_data.market_context,
                        forecasts=[schemas.StockForecast(**f) for f in stock_forecasts]
                    )

                    recommendations = await recommendation_service.generate_recommendations(rec_request)
                    recommendations_list = [r.dict() for r in recommendations.recommendations]

                except Exception as e:
                    logger.warning(f"Recommendation generation failed: {str(e)}")

            # Build response
            predictions_payload = {
                "request_id": ai_message.request_id,
                "report_id": ai_message.report_id,
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "predictions": {
                    "stock_forecasts": stock_forecasts,
                    "portfolio_analysis": portfolio_analysis,
                    "recommendations": recommendations_list,
                },
                "model_metadata": {
                    "qlib_version": "0.9.6",
                    "model_type": settings.qlib_default_model,
                    "feature_set": settings.qlib_feature_set,
                    "forecast_horizons": settings.forecast_horizons_list,
                },
                "processing_metadata": {
                    "stocks_processed": len(stock_forecasts),
                    "recommendations_generated": len(recommendations_list),
                    "portfolio_analyzed": portfolio_analysis is not None,
                }
            }

            return predictions_payload

        except Exception as e:
            logger.error(f"Prediction generation failed: {str(e)}")
            return None

    async def start(self):
        """Start consuming messages."""
        try:
            self.running = True

            # Connect to RabbitMQ
            await self.connect()

            # Connect publisher
            await self.publisher.connect()

            # Start consuming
            logger.info(f"Starting to consume from queue: {settings.queue_ai_extraction_complete}")
            await self.queue.consume(self.process_message)

            logger.info("✓ Consumer started successfully")

            # Keep running
            while self.running:
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Consumer error: {str(e)}")
            self.running = False

    async def stop(self):
        """Stop consuming messages."""
        try:
            logger.info("Stopping consumer...")
            self.running = False

            if self.channel and not self.channel.is_closed:
                await self.channel.close()

            if self.connection and not self.connection.is_closed:
                await self.connection.close()

            await self.publisher.close()

            logger.info("✓ Consumer stopped")

        except Exception as e:
            logger.error(f"Error stopping consumer: {str(e)}")
