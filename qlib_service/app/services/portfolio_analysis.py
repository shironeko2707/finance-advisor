"""
Portfolio analysis and risk assessment service.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger
from scipy import stats

from app.models.schemas import (
    Portfolio,
    StockData,
    PortfolioAnalysis,
    RiskMetrics,
    PerformanceForecast,
    MarketContext,
    StockPrediction
)
from app.config.settings import settings


class PortfolioAnalysisService:
    """Service for portfolio risk analysis and performance assessment."""

    def __init__(self):
        """Initialize the portfolio analysis service."""
        logger.info("Initialized PortfolioAnalysisService")

    async def analyze_portfolio(
        self,
        portfolio: Portfolio,
        stocks_data: List[StockData],
        market_context: MarketContext,
        stock_predictions: Optional[List[StockPrediction]] = None
    ) -> PortfolioAnalysis:
        """
        Perform comprehensive portfolio analysis.

        Args:
            portfolio: Portfolio holdings
            stocks_data: Historical data for all stocks in portfolio
            market_context: Market and benchmark context
            stock_predictions: Optional forecasts for portfolio stocks

        Returns:
            PortfolioAnalysis with risk metrics and forecasts
        """
        try:
            logger.info(f"Analyzing portfolio with {len(portfolio.positions)} positions")

            # Calculate risk metrics
            risk_metrics = await self._calculate_risk_metrics(
                portfolio, stocks_data, market_context
            )

            # Calculate performance forecast
            performance_forecast = await self._forecast_performance(
                portfolio, stocks_data, stock_predictions
            )

            # Calculate diversification score
            diversification_score = self._calculate_diversification(
                portfolio, stocks_data
            )

            # Classify risk level
            risk_level = self._classify_risk_level(risk_metrics, diversification_score)

            analysis = PortfolioAnalysis(
                risk_metrics=risk_metrics,
                performance_forecast=performance_forecast,
                diversification_score=round(diversification_score, 4),
                risk_level=risk_level
            )

            logger.info(f"Portfolio analysis complete: risk_level={risk_level}")
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze portfolio: {e}")
            raise

    async def _calculate_risk_metrics(
        self,
        portfolio: Portfolio,
        stocks_data: List[StockData],
        market_context: MarketContext
    ) -> RiskMetrics:
        """
        Calculate portfolio risk metrics.

        Args:
            portfolio: Portfolio holdings
            stocks_data: Historical stock data
            market_context: Market context

        Returns:
            RiskMetrics
        """
        try:
            # Build returns DataFrame
            returns_df = self._build_returns_dataframe(stocks_data)

            # Calculate portfolio returns
            portfolio_returns = self._calculate_portfolio_returns(
                returns_df, portfolio
            )

            # Calculate Sharpe Ratio
            sharpe_ratio = self._calculate_sharpe_ratio(
                portfolio_returns, market_context.risk_free_rate
            )

            # Calculate Maximum Drawdown
            max_drawdown = self._calculate_max_drawdown(portfolio_returns)

            # Calculate Volatility
            volatility = self._calculate_volatility(portfolio_returns)

            # Calculate Value at Risk (95% confidence)
            value_at_risk_95 = self._calculate_var(portfolio_returns, confidence=0.95)

            # Calculate Beta and Alpha (vs benchmark)
            beta, alpha = await self._calculate_beta_alpha(
                portfolio_returns, market_context
            )

            metrics = RiskMetrics(
                sharpe_ratio=round(float(sharpe_ratio), 4),
                max_drawdown=round(float(max_drawdown), 6),
                volatility=round(float(volatility), 6),
                value_at_risk_95=round(float(value_at_risk_95), 6),
                beta=round(float(beta), 6),
                alpha=round(float(alpha), 6)
            )

            logger.debug(f"Risk metrics: Sharpe={sharpe_ratio:.4f}, MaxDD={max_drawdown:.4f}")
            return metrics

        except Exception as e:
            logger.error(f"Failed to calculate risk metrics: {e}")
            raise

    async def _forecast_performance(
        self,
        portfolio: Portfolio,
        stocks_data: List[StockData],
        stock_predictions: Optional[List[StockPrediction]] = None
    ) -> PerformanceForecast:
        """
        Forecast portfolio performance.

        Args:
            portfolio: Portfolio holdings
            stocks_data: Historical stock data
            stock_predictions: Stock predictions (if available)

        Returns:
            PerformanceForecast
        """
        try:
            if stock_predictions:
                # Use predictions if available
                expected_return_1d = self._forecast_from_predictions(
                    portfolio, stock_predictions, horizon=1
                )
                expected_return_5d = self._forecast_from_predictions(
                    portfolio, stock_predictions, horizon=5
                )
                expected_return_30d = self._forecast_from_predictions(
                    portfolio, stock_predictions, horizon=30
                )
            else:
                # Fall back to historical momentum
                returns_df = self._build_returns_dataframe(stocks_data)
                portfolio_returns = self._calculate_portfolio_returns(returns_df, portfolio)

                # Use recent momentum for forecast
                recent_return = portfolio_returns.tail(20).mean()
                expected_return_1d = recent_return
                expected_return_5d = recent_return * 5
                expected_return_30d = recent_return * 30

            forecast = PerformanceForecast(
                expected_return_1d=round(float(expected_return_1d), 6),
                expected_return_5d=round(float(expected_return_5d), 6),
                expected_return_30d=round(float(expected_return_30d), 6)
            )

            logger.debug(f"Performance forecast: 30d={expected_return_30d:.4f}")
            return forecast

        except Exception as e:
            logger.error(f"Failed to forecast performance: {e}")
            raise

    def _build_returns_dataframe(self, stocks_data: List[StockData]) -> pd.DataFrame:
        """
        Build DataFrame of stock returns.

        Args:
            stocks_data: List of stock data

        Returns:
            DataFrame with returns for each stock
        """
        returns_dict = {}

        for stock_data in stocks_data:
            ticker = stock_data.ticker
            prices = pd.Series(
                [p.close for p in stock_data.prices],
                index=[p.date for p in stock_data.prices]
            )
            returns = prices.pct_change().dropna()
            returns_dict[ticker] = returns

        returns_df = pd.DataFrame(returns_dict)
        return returns_df.dropna()

    def _calculate_portfolio_returns(
        self,
        returns_df: pd.DataFrame,
        portfolio: Portfolio
    ) -> pd.Series:
        """
        Calculate portfolio returns based on weights.

        Args:
            returns_df: Returns for each stock
            portfolio: Portfolio with weights

        Returns:
            Series of portfolio returns
        """
        # Get weights
        weights = {}
        for position in portfolio.positions:
            if position.ticker in returns_df.columns:
                weights[position.ticker] = position.weight

        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        else:
            # Equal weight if no weights provided
            n = len(weights)
            weights = {k: 1.0 / n for k in weights.keys()}

        # Calculate weighted returns
        portfolio_returns = pd.Series(0, index=returns_df.index)
        for ticker, weight in weights.items():
            if ticker in returns_df.columns:
                portfolio_returns += returns_df[ticker] * weight

        return portfolio_returns

    def _calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: float
    ) -> float:
        """
        Calculate Sharpe Ratio.

        Args:
            returns: Portfolio returns
            risk_free_rate: Risk-free rate (annual)

        Returns:
            Sharpe ratio
        """
        # Convert annual risk-free rate to daily
        daily_rf_rate = (1 + risk_free_rate) ** (1/252) - 1

        # Calculate excess returns
        excess_returns = returns - daily_rf_rate

        # Sharpe ratio
        if excess_returns.std() > 0:
            sharpe = excess_returns.mean() / excess_returns.std()
            # Annualize (sqrt of 252 trading days)
            sharpe_annualized = sharpe * np.sqrt(252)
        else:
            sharpe_annualized = 0

        return float(sharpe_annualized)

    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """
        Calculate maximum drawdown.

        Args:
            returns: Portfolio returns

        Returns:
            Maximum drawdown (negative value)
        """
        # Calculate cumulative returns
        cumulative = (1 + returns).cumprod()

        # Calculate running maximum
        running_max = cumulative.expanding().max()

        # Calculate drawdown
        drawdown = (cumulative - running_max) / running_max

        # Maximum drawdown
        max_dd = drawdown.min()

        return float(max_dd)

    def _calculate_volatility(self, returns: pd.Series) -> float:
        """
        Calculate annualized volatility.

        Args:
            returns: Portfolio returns

        Returns:
            Annualized volatility
        """
        daily_vol = returns.std()
        annual_vol = daily_vol * np.sqrt(252)
        return float(annual_vol)

    def _calculate_var(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk.

        Args:
            returns: Portfolio returns
            confidence: Confidence level (default 0.95)

        Returns:
            VaR (negative value indicating potential loss)
        """
        # Use historical simulation method
        var = returns.quantile(1 - confidence)
        return float(var)

    async def _calculate_beta_alpha(
        self,
        portfolio_returns: pd.Series,
        market_context: MarketContext
    ) -> Tuple[float, float]:
        """
        Calculate Beta and Alpha vs benchmark.

        Args:
            portfolio_returns: Portfolio returns
            market_context: Market context with benchmark

        Returns:
            Tuple of (beta, alpha)
        """
        # Note: In production, would fetch actual benchmark returns
        # For now, using simplified calculation

        # Assume benchmark returns similar to market (simplified)
        # In reality, would fetch SPY or other benchmark data

        # Calculate beta using correlation and volatility ratio
        # Beta = Cov(portfolio, market) / Var(market)

        # Simplified: assume beta = 1.0 for now
        # Alpha = portfolio excess return - beta * market excess return

        # Placeholder values
        beta = 1.0
        alpha = portfolio_returns.mean() * 252 - market_context.risk_free_rate

        return float(beta), float(alpha)

    def _forecast_from_predictions(
        self,
        portfolio: Portfolio,
        stock_predictions: List[StockPrediction],
        horizon: int
    ) -> float:
        """
        Forecast portfolio return from stock predictions.

        Args:
            portfolio: Portfolio holdings
            stock_predictions: Stock predictions
            horizon: Forecast horizon in days

        Returns:
            Expected portfolio return
        """
        # Build prediction map
        prediction_map = {pred.ticker: pred for pred in stock_predictions}

        # Calculate weighted expected return
        expected_return = 0.0
        total_weight = 0.0

        for position in portfolio.positions:
            ticker = position.ticker
            weight = position.weight

            if ticker in prediction_map:
                prediction = prediction_map[ticker]

                # Find forecast for this horizon
                for forecast in prediction.forecasts:
                    if forecast.horizon_days == horizon:
                        expected_return += forecast.predicted_return * weight
                        total_weight += weight
                        break

        # Normalize if weights don't sum to 1
        if total_weight > 0 and total_weight != 1.0:
            expected_return /= total_weight

        return float(expected_return)

    def _calculate_diversification(
        self,
        portfolio: Portfolio,
        stocks_data: List[StockData]
    ) -> float:
        """
        Calculate diversification score (0 to 1, higher is better).

        Args:
            portfolio: Portfolio holdings
            stocks_data: Stock data

        Returns:
            Diversification score
        """
        try:
            # Build correlation matrix
            returns_df = self._build_returns_dataframe(stocks_data)

            if len(returns_df.columns) < 2:
                # Single stock, no diversification
                return 0.0

            # Calculate correlation matrix
            corr_matrix = returns_df.corr()

            # Average correlation (excluding diagonal)
            n = len(corr_matrix)
            avg_corr = (corr_matrix.sum().sum() - n) / (n * (n - 1))

            # Diversification score = 1 - average correlation
            # Higher score = lower correlation = better diversification
            diversification_score = 1.0 - avg_corr

            # Adjust for concentration (Herfindahl index)
            weights = [pos.weight for pos in portfolio.positions]
            total_weight = sum(weights)
            if total_weight > 0:
                normalized_weights = [w / total_weight for w in weights]
                herfindahl = sum(w ** 2 for w in normalized_weights)
                concentration_penalty = herfindahl
            else:
                concentration_penalty = 0

            # Final score
            final_score = diversification_score * (1 - concentration_penalty)

            # Clamp to [0, 1]
            final_score = np.clip(final_score, 0, 1)

            return float(final_score)

        except Exception as e:
            logger.error(f"Failed to calculate diversification: {e}")
            return 0.5  # default moderate diversification

    def _classify_risk_level(
        self,
        risk_metrics: RiskMetrics,
        diversification_score: float
    ) -> str:
        """
        Classify portfolio risk level.

        Args:
            risk_metrics: Risk metrics
            diversification_score: Diversification score

        Returns:
            Risk level: "low", "moderate", or "high"
        """
        # Risk score calculation
        risk_score = 0

        # Volatility component
        if risk_metrics.volatility > 0.30:
            risk_score += 3
        elif risk_metrics.volatility > 0.20:
            risk_score += 2
        else:
            risk_score += 1

        # Max drawdown component
        if risk_metrics.max_drawdown < -0.20:
            risk_score += 3
        elif risk_metrics.max_drawdown < -0.10:
            risk_score += 2
        else:
            risk_score += 1

        # VaR component
        if risk_metrics.value_at_risk_95 < -0.05:
            risk_score += 3
        elif risk_metrics.value_at_risk_95 < -0.03:
            risk_score += 2
        else:
            risk_score += 1

        # Diversification component (inverse)
        if diversification_score < 0.3:
            risk_score += 2
        elif diversification_score < 0.6:
            risk_score += 1

        # Classify based on total score
        if risk_score >= 9:
            return "high"
        elif risk_score >= 5:
            return "moderate"
        else:
            return "low"
