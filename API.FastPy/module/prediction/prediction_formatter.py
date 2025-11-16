"""
Prediction formatter utilities for Excel report generation.

This module provides utilities to format Qlib prediction data
for inclusion in Excel reports.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PredictionFormatter:
    """Formatter for converting prediction data to Excel-friendly format."""

    @staticmethod
    def format_stock_predictions_for_excel(stock_predictions: List[Any]) -> List[Dict[str, Any]]:
        """
        Format stock predictions for Excel table.

        Args:
            stock_predictions: List of StockPrediction objects

        Returns:
            List of dictionaries with formatted prediction data
        """
        formatted = []

        for stock_pred in stock_predictions:
            # Format each forecast horizon
            for forecast in stock_pred.forecasts:
                formatted.append({
                    "Ticker": stock_pred.ticker,
                    "Current Price": f"${stock_pred.current_price:.2f}",
                    "Trend": stock_pred.trend.upper(),
                    "Forecast Horizon": f"{forecast['horizon_days']} Day(s)",
                    "Predicted Price": f"${forecast['predicted_price']:.2f}",
                    "Predicted Return": f"{forecast['predicted_return']:.2%}",
                    "Confidence": f"{forecast['confidence_score']:.1%}",
                    "Price Range (Low)": f"${forecast['prediction_interval']['lower']:.2f}",
                    "Price Range (High)": f"${forecast['prediction_interval']['upper']:.2f}",
                    "Volatility": f"{stock_pred.volatility_forecast:.2%}",
                })

        return formatted

    @staticmethod
    def format_stock_predictions_summary(stock_predictions: List[Any]) -> List[Dict[str, Any]]:
        """
        Format stock predictions summary (one row per stock).

        Args:
            stock_predictions: List of StockPrediction objects

        Returns:
            List of dictionaries with summary data
        """
        formatted = []

        for stock_pred in stock_predictions:
            # Get forecasts
            forecast_1d = next((f for f in stock_pred.forecasts if f['horizon_days'] == 1), None)
            forecast_5d = next((f for f in stock_pred.forecasts if f['horizon_days'] == 5), None)
            forecast_30d = next((f for f in stock_pred.forecasts if f['horizon_days'] == 30), None)

            formatted.append({
                "Ticker": stock_pred.ticker,
                "Current Price": f"${stock_pred.current_price:.2f}",
                "Trend": stock_pred.trend.upper(),
                "1-Day Forecast": f"${forecast_1d['predicted_price']:.2f}" if forecast_1d else "N/A",
                "1-Day Return": f"{forecast_1d['predicted_return']:.2%}" if forecast_1d else "N/A",
                "5-Day Forecast": f"${forecast_5d['predicted_price']:.2f}" if forecast_5d else "N/A",
                "5-Day Return": f"{forecast_5d['predicted_return']:.2%}" if forecast_5d else "N/A",
                "30-Day Forecast": f"${forecast_30d['predicted_price']:.2f}" if forecast_30d else "N/A",
                "30-Day Return": f"{forecast_30d['predicted_return']:.2%}" if forecast_30d else "N/A",
                "Volatility": f"{stock_pred.volatility_forecast:.2%}",
            })

        return formatted

    @staticmethod
    def format_portfolio_analysis_for_excel(portfolio_analysis: Optional[Any]) -> Dict[str, Any]:
        """
        Format portfolio analysis for Excel.

        Args:
            portfolio_analysis: PortfolioAnalysis object

        Returns:
            Dictionary with formatted portfolio data
        """
        if not portfolio_analysis:
            return {}

        return {
            # Risk Metrics
            "Risk Level": portfolio_analysis.risk_level.upper(),
            "Sharpe Ratio": f"{portfolio_analysis.sharpe_ratio:.2f}",
            "Max Drawdown": f"{portfolio_analysis.max_drawdown:.2%}",
            "Volatility": f"{portfolio_analysis.volatility:.2%}",
            "Value at Risk (95%)": f"{portfolio_analysis.value_at_risk_95:.2%}",
            "Beta": f"{portfolio_analysis.beta:.2f}",
            "Alpha": f"{portfolio_analysis.alpha:.2%}",
            "Diversification Score": f"{portfolio_analysis.diversification_score:.1%}",

            # Performance Forecasts
            "Expected Return (1-Day)": f"{portfolio_analysis.expected_return_1d:.2%}",
            "Expected Return (5-Day)": f"{portfolio_analysis.expected_return_5d:.2%}",
            "Expected Return (30-Day)": f"{portfolio_analysis.expected_return_30d:.2%}",
        }

    @staticmethod
    def format_recommendations_for_excel(recommendations: List[Any]) -> List[Dict[str, Any]]:
        """
        Format recommendations for Excel table.

        Args:
            recommendations: List of Recommendation objects

        Returns:
            List of dictionaries with formatted recommendation data
        """
        formatted = []

        for rec in recommendations:
            formatted.append({
                "Ticker": rec.ticker,
                "Recommendation": rec.action.upper(),
                "Strength": rec.strength.capitalize(),
                "Confidence": f"{rec.confidence:.1%}",
                "Target Price": f"${rec.target_price:.2f}" if rec.target_price else "N/A",
                "Stop Loss": f"${rec.stop_loss:.2f}" if rec.stop_loss else "N/A",
                "Technical Score": f"{rec.technical_score:.1%}",
                "Fundamental Score": f"{rec.fundamental_score:.1%}",
                "Sentiment Score": f"{rec.sentiment_score:.1%}",
                "Rationale": rec.rationale,
            })

        return formatted

    @staticmethod
    def format_market_regime_for_excel(market_regime: Optional[Any]) -> Dict[str, Any]:
        """
        Format market regime for Excel.

        Args:
            market_regime: MarketRegime object

        Returns:
            Dictionary with formatted market regime data
        """
        if not market_regime:
            return {}

        return {
            "Market Regime": market_regime.regime.replace("_", " ").title(),
            "Confidence": f"{market_regime.confidence:.1%}",
            "Description": market_regime.description,
        }

    @staticmethod
    def create_prediction_summary(prediction_results: Any) -> Dict[str, Any]:
        """
        Create a comprehensive prediction summary.

        Args:
            prediction_results: PredictionRequest object with all relationships

        Returns:
            Dictionary with complete prediction summary
        """
        summary = {
            "metadata": {
                "request_id": prediction_results.request_id,
                "model_name": prediction_results.model_name or "Unknown",
                "model_version": prediction_results.model_version or "Unknown",
                "feature_set": prediction_results.feature_set or "Unknown",
                "processing_time": f"{prediction_results.processing_time_seconds:.2f}s" if prediction_results.processing_time_seconds else "N/A",
                "generated_at": prediction_results.created_at.strftime("%Y-%m-%d %H:%M:%S") if prediction_results.created_at else "N/A",
                "status": prediction_results.prediction_status or "Unknown",
            },
            "stock_count": len(prediction_results.stock_predictions) if prediction_results.stock_predictions else 0,
            "has_portfolio_analysis": prediction_results.portfolio_analysis is not None,
            "recommendations_count": len(prediction_results.recommendations) if prediction_results.recommendations else 0,
            "has_market_regime": prediction_results.market_regime is not None,
        }

        return summary

    @staticmethod
    def format_predictions_for_json(prediction_results: Any) -> Dict[str, Any]:
        """
        Format complete prediction results for JSON API response.

        Args:
            prediction_results: PredictionRequest object with all relationships

        Returns:
            Dictionary with all formatted prediction data
        """
        result = {
            "summary": PredictionFormatter.create_prediction_summary(prediction_results),
            "market_regime": None,
            "portfolio_analysis": None,
            "stock_predictions": [],
            "recommendations": [],
        }

        # Market regime
        if prediction_results.market_regime:
            result["market_regime"] = PredictionFormatter.format_market_regime_for_excel(
                prediction_results.market_regime
            )

        # Portfolio analysis
        if prediction_results.portfolio_analysis:
            result["portfolio_analysis"] = PredictionFormatter.format_portfolio_analysis_for_excel(
                prediction_results.portfolio_analysis
            )

        # Stock predictions
        if prediction_results.stock_predictions:
            result["stock_predictions"] = PredictionFormatter.format_stock_predictions_summary(
                prediction_results.stock_predictions
            )

        # Recommendations
        if prediction_results.recommendations:
            result["recommendations"] = PredictionFormatter.format_recommendations_for_excel(
                prediction_results.recommendations
            )

        return result


# Convenience functions
def format_predictions_for_report(prediction_results: Any) -> Dict[str, Any]:
    """
    Main function to format all prediction data for report inclusion.

    Args:
        prediction_results: PredictionRequest object with all relationships

    Returns:
        Dictionary with all formatted prediction data ready for Excel/PDF
    """
    return PredictionFormatter.format_predictions_for_json(prediction_results)
