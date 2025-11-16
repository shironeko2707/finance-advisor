"""
Service layer for processing and storing Qlib predictions.
"""
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging

from .prediction_repository import PredictionRepository
from .PredictionModel import PredictionRequest

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for processing Qlib prediction messages."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = PredictionRepository(db)

    def process_qlib_prediction_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Process a Qlib prediction ready message and store results in database.

        Args:
            message_data: Dictionary containing the prediction message

        Returns:
            True if processed successfully, False otherwise
        """
        try:
            request_id = message_data.get("request_id")
            report_id = message_data.get("report_id")
            prediction_status = message_data.get("prediction_status")
            predictions = message_data.get("predictions")
            model_metadata = message_data.get("model_metadata", {})
            error_message = message_data.get("error_message")

            logger.info(f"Processing prediction message for request_id={request_id}")

            # Get or create prediction request
            prediction_request = self.repository.get_prediction_request_by_request_id(request_id)

            if not prediction_request:
                logger.info(f"Creating new prediction request for request_id={request_id}")
                prediction_request = self.repository.create_prediction_request(
                    request_id=request_id,
                    report_id=report_id
                )

            # Update status to processing
            self.repository.update_prediction_request_status(
                request_id=request_id,
                status="processing",
                prediction_status=prediction_status
            )

            # Update model metadata
            if model_metadata:
                self.repository.update_prediction_metadata(
                    request_id=request_id,
                    model_name=model_metadata.get("primary_model", "unknown"),
                    model_version=model_metadata.get("model_version", "unknown"),
                    feature_set=model_metadata.get("feature_set", "unknown")
                )

            # Check if predictions exist
            if not predictions:
                logger.warning(f"No predictions data for request_id={request_id}")
                self.repository.update_prediction_request_status(
                    request_id=request_id,
                    status="failed",
                    error_message=error_message or "No predictions data received"
                )
                return False

            # Process stock forecasts
            stock_forecasts = predictions.get("stock_forecasts", [])
            if stock_forecasts:
                self._process_stock_forecasts(prediction_request.id, stock_forecasts)

            # Process portfolio analysis
            portfolio_analysis = predictions.get("portfolio_analysis")
            if portfolio_analysis:
                self._process_portfolio_analysis(prediction_request.id, portfolio_analysis)

            # Process recommendations
            recommendations = predictions.get("recommendations", [])
            if recommendations:
                self._process_recommendations(prediction_request.id, recommendations)

            # Process market regime
            market_regime = predictions.get("market_regime")
            if market_regime:
                self._process_market_regime(prediction_request.id, market_regime)

            # Update final status
            final_status = "success" if prediction_status == "success" else "completed_with_warnings"
            self.repository.update_prediction_request_status(
                request_id=request_id,
                status=final_status,
                prediction_status=prediction_status,
                error_message=error_message
            )

            logger.info(f"Successfully processed predictions for request_id={request_id}")
            return True

        except Exception as e:
            logger.error(f"Error processing prediction message: {e}", exc_info=True)
            if request_id:
                try:
                    self.repository.update_prediction_request_status(
                        request_id=request_id,
                        status="failed",
                        error_message=str(e)
                    )
                except Exception as update_error:
                    logger.error(f"Failed to update error status: {update_error}")
            return False

    def _process_stock_forecasts(self, prediction_request_id: int, stock_forecasts: list):
        """Process and store stock forecasts."""
        try:
            for forecast in stock_forecasts:
                # Extract forecast data
                ticker = forecast.get("ticker")
                current_price = forecast.get("current_price")
                trend = forecast.get("trend")
                volatility_forecast = forecast.get("volatility_forecast")
                forecasts_data = forecast.get("forecasts", [])

                # Convert forecast objects to JSON-serializable format
                forecasts_json = [
                    {
                        "horizon_days": f.get("horizon_days"),
                        "predicted_price": f.get("predicted_price"),
                        "predicted_return": f.get("predicted_return"),
                        "confidence_score": f.get("confidence_score"),
                        "prediction_interval": {
                            "lower": f.get("prediction_interval", {}).get("lower"),
                            "upper": f.get("prediction_interval", {}).get("upper")
                        }
                    }
                    for f in forecasts_data
                ]

                self.repository.create_stock_prediction(
                    prediction_request_id=prediction_request_id,
                    ticker=ticker,
                    current_price=current_price,
                    trend=trend,
                    volatility_forecast=volatility_forecast,
                    forecasts=forecasts_json
                )

            logger.info(f"Stored {len(stock_forecasts)} stock forecasts")

        except Exception as e:
            logger.error(f"Error processing stock forecasts: {e}", exc_info=True)
            raise

    def _process_portfolio_analysis(self, prediction_request_id: int, portfolio_analysis: dict):
        """Process and store portfolio analysis."""
        try:
            risk_metrics = portfolio_analysis.get("risk_metrics", {})
            performance_forecast = portfolio_analysis.get("performance_forecast", {})

            self.repository.create_portfolio_analysis(
                prediction_request_id=prediction_request_id,
                sharpe_ratio=risk_metrics.get("sharpe_ratio"),
                max_drawdown=risk_metrics.get("max_drawdown"),
                volatility=risk_metrics.get("volatility"),
                value_at_risk_95=risk_metrics.get("value_at_risk_95"),
                beta=risk_metrics.get("beta"),
                alpha=risk_metrics.get("alpha"),
                expected_return_1d=performance_forecast.get("expected_return_1d"),
                expected_return_5d=performance_forecast.get("expected_return_5d"),
                expected_return_30d=performance_forecast.get("expected_return_30d"),
                diversification_score=portfolio_analysis.get("diversification_score"),
                risk_level=portfolio_analysis.get("risk_level")
            )

            logger.info("Stored portfolio analysis")

        except Exception as e:
            logger.error(f"Error processing portfolio analysis: {e}", exc_info=True)
            raise

    def _process_recommendations(self, prediction_request_id: int, recommendations: list):
        """Process and store recommendations."""
        try:
            for recommendation in recommendations:
                factors = recommendation.get("factors", {})

                self.repository.create_recommendation(
                    prediction_request_id=prediction_request_id,
                    ticker=recommendation.get("ticker"),
                    action=recommendation.get("action"),
                    strength=recommendation.get("strength"),
                    confidence=recommendation.get("confidence"),
                    target_price=recommendation.get("target_price"),
                    stop_loss=recommendation.get("stop_loss"),
                    rationale=recommendation.get("rationale"),
                    technical_score=factors.get("technical_score"),
                    fundamental_score=factors.get("fundamental_score"),
                    sentiment_score=factors.get("sentiment_score")
                )

            logger.info(f"Stored {len(recommendations)} recommendations")

        except Exception as e:
            logger.error(f"Error processing recommendations: {e}", exc_info=True)
            raise

    def _process_market_regime(self, prediction_request_id: int, market_regime: dict):
        """Process and store market regime."""
        try:
            self.repository.create_market_regime(
                prediction_request_id=prediction_request_id,
                regime=market_regime.get("regime"),
                confidence=market_regime.get("confidence"),
                description=market_regime.get("description")
            )

            logger.info("Stored market regime")

        except Exception as e:
            logger.error(f"Error processing market regime: {e}", exc_info=True)
            raise

    def get_prediction_results(self, request_id: str) -> Optional[PredictionRequest]:
        """
        Get complete prediction results for a request.

        Args:
            request_id: Request ID

        Returns:
            PredictionRequest with all relationships loaded, or None if not found
        """
        return self.repository.get_prediction_request_by_request_id(request_id)

    def get_prediction_results_by_report(self, report_id: int) -> Optional[PredictionRequest]:
        """
        Get prediction results for a report.

        Args:
            report_id: Report ID

        Returns:
            PredictionRequest with all relationships loaded, or None if not found
        """
        return self.repository.get_prediction_request_by_report_id(report_id)
