"""
Investment recommendation engine.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from loguru import logger

from app.models.schemas import (
    Recommendation,
    RecommendationFactors,
    MarketRegime,
    StockData,
    StockPrediction,
    PortfolioAnalysis
)
from app.config.settings import settings


class RecommendationEngine:
    """Engine for generating investment recommendations."""

    def __init__(self):
        """Initialize the recommendation engine."""
        logger.info("Initialized RecommendationEngine")

    async def generate_recommendations(
        self,
        stocks_data: List[StockData],
        stock_predictions: List[StockPrediction],
        risk_tolerance: str = "moderate",
        investment_horizon: int = 30
    ) -> Tuple[List[Recommendation], MarketRegime]:
        """
        Generate investment recommendations for stocks.

        Args:
            stocks_data: Historical stock data
            stock_predictions: Price predictions
            risk_tolerance: User risk tolerance (low/moderate/high)
            investment_horizon: Investment horizon in days

        Returns:
            Tuple of (recommendations list, market regime)
        """
        try:
            logger.info(f"Generating recommendations for {len(stocks_data)} stocks")

            # Detect market regime
            market_regime = self._detect_market_regime(stocks_data, stock_predictions)

            # Generate recommendations for each stock
            recommendations = []
            for stock_data in stocks_data:
                # Find corresponding prediction
                prediction = next(
                    (p for p in stock_predictions if p.ticker == stock_data.ticker),
                    None
                )

                if prediction:
                    recommendation = await self._generate_stock_recommendation(
                        stock_data,
                        prediction,
                        market_regime,
                        risk_tolerance,
                        investment_horizon
                    )
                    recommendations.append(recommendation)

            # Sort by confidence (highest first)
            recommendations.sort(key=lambda r: r.confidence, reverse=True)

            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations, market_regime

        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            raise

    async def _generate_stock_recommendation(
        self,
        stock_data: StockData,
        prediction: StockPrediction,
        market_regime: MarketRegime,
        risk_tolerance: str,
        investment_horizon: int
    ) -> Recommendation:
        """
        Generate recommendation for a single stock.

        Args:
            stock_data: Historical stock data
            prediction: Price prediction
            market_regime: Current market regime
            risk_tolerance: Risk tolerance
            investment_horizon: Investment horizon

        Returns:
            Recommendation
        """
        try:
            ticker = stock_data.ticker

            # Calculate factor scores
            factors = self._calculate_recommendation_factors(
                stock_data, prediction, market_regime
            )

            # Determine action and strength
            action, strength = self._determine_action(
                factors, prediction, risk_tolerance, investment_horizon
            )

            # Calculate confidence
            confidence = self._calculate_recommendation_confidence(
                factors, prediction, market_regime
            )

            # Calculate target price and stop loss
            target_price, stop_loss = self._calculate_price_targets(
                stock_data, prediction, action, investment_horizon
            )

            # Generate rationale
            rationale = self._generate_rationale(
                action, strength, factors, prediction, market_regime
            )

            recommendation = Recommendation(
                ticker=ticker,
                action=action,
                strength=strength,
                confidence=round(confidence, 4),
                target_price=target_price,
                stop_loss=stop_loss,
                rationale=rationale,
                factors=factors
            )

            logger.debug(f"{ticker}: {action.upper()} ({strength}) confidence={confidence:.2f}")
            return recommendation

        except Exception as e:
            logger.error(f"Failed to generate recommendation for {stock_data.ticker}: {e}")
            raise

    def _calculate_recommendation_factors(
        self,
        stock_data: StockData,
        prediction: StockPrediction,
        market_regime: MarketRegime
    ) -> RecommendationFactors:
        """
        Calculate multi-factor scores for recommendation.

        Args:
            stock_data: Stock data
            prediction: Price prediction
            market_regime: Market regime

        Returns:
            RecommendationFactors
        """
        # Technical score
        technical_score = self._calculate_technical_score(stock_data, prediction)

        # Fundamental score
        fundamental_score = self._calculate_fundamental_score(stock_data)

        # Sentiment score (based on market regime and trend)
        sentiment_score = self._calculate_sentiment_score(prediction, market_regime)

        return RecommendationFactors(
            technical_score=round(technical_score, 4),
            fundamental_score=round(fundamental_score, 4),
            sentiment_score=round(sentiment_score, 4)
        )

    def _calculate_technical_score(
        self,
        stock_data: StockData,
        prediction: StockPrediction
    ) -> float:
        """Calculate technical analysis score (0 to 1)."""
        score = 0.5  # neutral baseline

        # Trend component
        if prediction.trend == "bullish":
            score += 0.3
        elif prediction.trend == "bearish":
            score -= 0.3

        # Predicted return component (30-day forecast)
        forecast_30d = next((f for f in prediction.forecasts if f.horizon_days == 30), None)
        if forecast_30d:
            expected_return = forecast_30d.predicted_return
            if expected_return > 0.10:  # > 10% gain
                score += 0.2
            elif expected_return > 0.05:  # > 5% gain
                score += 0.1
            elif expected_return < -0.10:  # > 10% loss
                score -= 0.2
            elif expected_return < -0.05:  # > 5% loss
                score -= 0.1

        # Volatility component (lower is better for stability)
        if prediction.volatility_forecast < 0.15:  # < 15% volatility
            score += 0.1
        elif prediction.volatility_forecast > 0.30:  # > 30% volatility
            score -= 0.1

        # Clamp to [0, 1]
        score = np.clip(score, 0, 1)
        return float(score)

    def _calculate_fundamental_score(self, stock_data: StockData) -> float:
        """Calculate fundamental analysis score (0 to 1)."""
        score = 0.5  # neutral baseline

        if stock_data.financial_metrics:
            metrics = stock_data.financial_metrics

            # P/E ratio evaluation
            if metrics.pe_ratio:
                if 10 <= metrics.pe_ratio <= 25:  # Reasonable P/E
                    score += 0.15
                elif metrics.pe_ratio > 40:  # Overvalued
                    score -= 0.15

            # Dividend yield (positive signal)
            if metrics.dividend_yield and metrics.dividend_yield > 0.02:
                score += 0.1

            # Beta (stability)
            if metrics.beta:
                if 0.8 <= metrics.beta <= 1.2:  # Moderate beta
                    score += 0.1
                elif metrics.beta > 1.5:  # High beta (risky)
                    score -= 0.1

        if stock_data.fundamentals:
            fundamentals = stock_data.fundamentals

            # Profitability
            if fundamentals.net_income and fundamentals.revenue:
                profit_margin = fundamentals.net_income / fundamentals.revenue
                if profit_margin > 0.15:  # > 15% margin
                    score += 0.15
                elif profit_margin < 0:  # Negative margin
                    score -= 0.15

        # Clamp to [0, 1]
        score = np.clip(score, 0, 1)
        return float(score)

    def _calculate_sentiment_score(
        self,
        prediction: StockPrediction,
        market_regime: MarketRegime
    ) -> float:
        """Calculate sentiment score based on market regime and trend (0 to 1)."""
        score = 0.5  # neutral baseline

        # Market regime impact
        if market_regime.regime == "trending_up":
            score += 0.2
        elif market_regime.regime == "trending_down":
            score -= 0.2
        elif market_regime.regime == "volatile":
            score -= 0.1  # Caution in volatile markets

        # Stock trend alignment with market
        if prediction.trend == "bullish" and market_regime.regime == "trending_up":
            score += 0.2  # Strong positive signal
        elif prediction.trend == "bearish" and market_regime.regime == "trending_down":
            score -= 0.2  # Strong negative signal

        # Confidence in market regime
        regime_confidence_factor = (market_regime.confidence - 0.5) * 0.2
        score += regime_confidence_factor

        # Clamp to [0, 1]
        score = np.clip(score, 0, 1)
        return float(score)

    def _determine_action(
        self,
        factors: RecommendationFactors,
        prediction: StockPrediction,
        risk_tolerance: str,
        investment_horizon: int
    ) -> Tuple[str, str]:
        """
        Determine buy/sell/hold action and strength.

        Args:
            factors: Recommendation factors
            prediction: Price prediction
            risk_tolerance: Risk tolerance
            investment_horizon: Investment horizon

        Returns:
            Tuple of (action, strength)
        """
        # Calculate composite score
        composite_score = (
            0.4 * factors.technical_score +
            0.35 * factors.fundamental_score +
            0.25 * factors.sentiment_score
        )

        # Find forecast for investment horizon
        forecast = next(
            (f for f in prediction.forecasts if f.horizon_days >= investment_horizon),
            prediction.forecasts[-1]  # Use longest horizon if not found
        )

        expected_return = forecast.predicted_return

        # Adjust thresholds based on risk tolerance
        if risk_tolerance == "low":
            buy_threshold = 0.65
            strong_buy_threshold = 0.80
            sell_threshold = 0.35
            strong_sell_threshold = 0.20
        elif risk_tolerance == "high":
            buy_threshold = 0.55
            strong_buy_threshold = 0.70
            sell_threshold = 0.45
            strong_sell_threshold = 0.30
        else:  # moderate
            buy_threshold = 0.60
            strong_buy_threshold = 0.75
            sell_threshold = 0.40
            strong_sell_threshold = 0.25

        # Determine action
        if composite_score >= strong_buy_threshold and expected_return > 0.10:
            return "buy", "strong"
        elif composite_score >= buy_threshold and expected_return > 0.05:
            return "buy", "moderate"
        elif composite_score >= buy_threshold and expected_return > 0:
            return "buy", "weak"
        elif composite_score <= strong_sell_threshold or expected_return < -0.10:
            return "sell", "strong"
        elif composite_score <= sell_threshold and expected_return < -0.05:
            return "sell", "moderate"
        elif composite_score <= sell_threshold and expected_return < 0:
            return "sell", "weak"
        else:
            return "hold", "moderate"

    def _calculate_recommendation_confidence(
        self,
        factors: RecommendationFactors,
        prediction: StockPrediction,
        market_regime: MarketRegime
    ) -> float:
        """Calculate confidence in the recommendation (0 to 1)."""
        # Base confidence from prediction
        forecast_30d = next((f for f in prediction.forecasts if f.horizon_days == 30), prediction.forecasts[-1])
        prediction_confidence = forecast_30d.confidence_score

        # Factor agreement (how aligned are the factors?)
        factor_scores = [
            factors.technical_score,
            factors.fundamental_score,
            factors.sentiment_score
        ]
        factor_std = np.std(factor_scores)
        factor_agreement = 1.0 - min(factor_std * 2, 1.0)  # Lower std = higher agreement

        # Market regime confidence
        regime_confidence = market_regime.confidence

        # Composite confidence
        confidence = (
            0.4 * prediction_confidence +
            0.3 * factor_agreement +
            0.3 * regime_confidence
        )

        # Clamp to [0.3, 1.0]
        confidence = np.clip(confidence, 0.3, 1.0)
        return float(confidence)

    def _calculate_price_targets(
        self,
        stock_data: StockData,
        prediction: StockPrediction,
        action: str,
        investment_horizon: int
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Calculate target price and stop loss.

        Args:
            stock_data: Stock data
            prediction: Price prediction
            action: Recommended action
            investment_horizon: Investment horizon

        Returns:
            Tuple of (target_price, stop_loss)
        """
        current_price = prediction.current_price

        if action == "hold":
            return None, None

        # Find appropriate forecast
        forecast = next(
            (f for f in prediction.forecasts if f.horizon_days >= investment_horizon),
            prediction.forecasts[-1]
        )

        if action == "buy":
            # Target price: predicted price upper bound
            target_price = forecast.prediction_interval.upper

            # Stop loss: 10-15% below current price (based on volatility)
            stop_loss_pct = 0.10 + (prediction.volatility_forecast * 0.2)
            stop_loss_pct = min(stop_loss_pct, 0.20)  # Cap at 20%
            stop_loss = current_price * (1 - stop_loss_pct)

        else:  # sell
            # Target price: predicted price lower bound
            target_price = forecast.prediction_interval.lower

            # Stop loss: 10% above current price (for short positions)
            stop_loss = current_price * 1.10

        return round(float(target_price), 2), round(float(stop_loss), 2)

    def _generate_rationale(
        self,
        action: str,
        strength: str,
        factors: RecommendationFactors,
        prediction: StockPrediction,
        market_regime: MarketRegime
    ) -> str:
        """Generate human-readable rationale for recommendation."""
        # Find 30-day forecast
        forecast_30d = next(
            (f for f in prediction.forecasts if f.horizon_days == 30),
            prediction.forecasts[-1]
        )

        expected_return_pct = forecast_30d.predicted_return * 100

        # Build rationale
        rationale_parts = []

        # Action description
        action_desc = {
            ("buy", "strong"): "Strong buy recommendation",
            ("buy", "moderate"): "Moderate buy recommendation",
            ("buy", "weak"): "Weak buy recommendation",
            ("sell", "strong"): "Strong sell recommendation",
            ("sell", "moderate"): "Moderate sell recommendation",
            ("sell", "weak"): "Weak sell recommendation",
            ("hold", "moderate"): "Hold recommendation"
        }
        rationale_parts.append(action_desc.get((action, strength), "Recommendation"))

        # Expected return
        if expected_return_pct > 0:
            rationale_parts.append(f"with forecasted {expected_return_pct:.1f}% gain over 30 days.")
        elif expected_return_pct < 0:
            rationale_parts.append(f"with forecasted {abs(expected_return_pct):.1f}% loss over 30 days.")
        else:
            rationale_parts.append("with neutral price forecast.")

        # Trend
        if prediction.trend == "bullish":
            rationale_parts.append("Strong upward trend detected.")
        elif prediction.trend == "bearish":
            rationale_parts.append("Downward trend detected.")

        # Factor highlights
        if factors.technical_score > 0.7:
            rationale_parts.append("Technical indicators are favorable.")
        elif factors.technical_score < 0.3:
            rationale_parts.append("Technical indicators show weakness.")

        if factors.fundamental_score > 0.7:
            rationale_parts.append("Strong fundamentals.")
        elif factors.fundamental_score < 0.3:
            rationale_parts.append("Weak fundamentals.")

        # Market context
        if market_regime.regime == "trending_up":
            rationale_parts.append("Market is in an uptrend.")
        elif market_regime.regime == "trending_down":
            rationale_parts.append("Market is in a downtrend.")
        elif market_regime.regime == "volatile":
            rationale_parts.append("Market volatility elevated.")

        return " ".join(rationale_parts)

    def _detect_market_regime(
        self,
        stocks_data: List[StockData],
        stock_predictions: List[StockPrediction]
    ) -> MarketRegime:
        """
        Detect overall market regime.

        Args:
            stocks_data: All stocks data
            stock_predictions: All predictions

        Returns:
            MarketRegime
        """
        try:
            # Analyze trends across all stocks
            bullish_count = sum(1 for p in stock_predictions if p.trend == "bullish")
            bearish_count = sum(1 for p in stock_predictions if p.trend == "bearish")
            total = len(stock_predictions)

            if total == 0:
                return MarketRegime(
                    regime="sideways",
                    confidence=0.5,
                    description="Insufficient data to determine market regime"
                )

            bullish_pct = bullish_count / total
            bearish_pct = bearish_count / total

            # Average volatility
            avg_volatility = np.mean([p.volatility_forecast for p in stock_predictions])

            # Determine regime
            if bullish_pct > 0.6:
                regime = "trending_up"
                confidence = bullish_pct
                description = f"Market showing bullish momentum with {bullish_pct*100:.0f}% of stocks in uptrend"
            elif bearish_pct > 0.6:
                regime = "trending_down"
                confidence = bearish_pct
                description = f"Market in downtrend with {bearish_pct*100:.0f}% of stocks declining"
            elif avg_volatility > 0.30:
                regime = "volatile"
                confidence = min(avg_volatility / 0.30, 1.0)
                description = f"High market volatility detected ({avg_volatility*100:.0f}% average)"
            else:
                regime = "sideways"
                confidence = 1.0 - max(bullish_pct, bearish_pct)
                description = "Market trading in sideways range with no clear trend"

            return MarketRegime(
                regime=regime,
                confidence=round(float(confidence), 4),
                description=description
            )

        except Exception as e:
            logger.error(f"Failed to detect market regime: {e}")
            return MarketRegime(
                regime="sideways",
                confidence=0.5,
                description="Unable to determine market regime"
            )
