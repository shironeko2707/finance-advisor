"""
Stock price forecasting service using Qlib.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from loguru import logger
from scipy import stats

from app.models.schemas import (
    StockForecast,
    StockPrediction,
    PredictionInterval,
    StockData
)
from app.config.settings import settings


class ForecastingService:
    """Service for stock price forecasting using Qlib."""

    def __init__(self):
        """Initialize the forecasting service."""
        self.model_name = settings.qlib_default_model
        self.horizons = settings.forecast_horizons_list
        self.feature_set = settings.qlib_feature_set
        logger.info(f"Initialized ForecastingService with model={self.model_name}")

    async def predict_stock_price(
        self,
        stock_data: StockData,
        horizons: Optional[List[int]] = None
    ) -> StockPrediction:
        """
        Predict stock price for multiple time horizons.

        Args:
            stock_data: Historical stock data
            horizons: List of forecast horizons in days (default: from settings)

        Returns:
            StockPrediction with forecasts for each horizon
        """
        try:
            horizons = horizons or self.horizons
            ticker = stock_data.ticker

            logger.info(f"Generating predictions for {ticker} with horizons {horizons}")

            # Get current price
            current_price = stock_data.prices[-1].close

            # Convert to DataFrame
            df = self._prepare_dataframe(stock_data)

            # Generate forecasts for each horizon
            forecasts = []
            for horizon in horizons:
                forecast = await self._predict_horizon(df, current_price, horizon, ticker)
                forecasts.append(forecast)

            # Detect trend
            trend = self._detect_trend(df, forecasts)

            # Forecast volatility
            volatility = self._forecast_volatility(df)

            prediction = StockPrediction(
                ticker=ticker,
                current_price=current_price,
                forecasts=forecasts,
                trend=trend,
                volatility_forecast=volatility
            )

            logger.info(f"Generated {len(forecasts)} forecasts for {ticker}")
            return prediction

        except Exception as e:
            logger.error(f"Failed to predict stock price for {stock_data.ticker}: {e}")
            raise

    async def _predict_horizon(
        self,
        df: pd.DataFrame,
        current_price: float,
        horizon: int,
        ticker: str
    ) -> StockForecast:
        """
        Predict price for a specific time horizon.

        Args:
            df: Price DataFrame with features
            current_price: Current stock price
            horizon: Days ahead to forecast
            ticker: Stock ticker

        Returns:
            StockForecast for the specified horizon
        """
        try:
            # Calculate features
            features = self._calculate_features(df)

            # Simple prediction model (will be replaced with Qlib model)
            # Using momentum and trend-based prediction
            predicted_return = await self._predict_return(features, horizon)

            # Calculate predicted price
            predicted_price = current_price * (1 + predicted_return)

            # Calculate confidence score based on data quality and volatility
            confidence_score = self._calculate_confidence(df, horizon)

            # Calculate prediction interval
            prediction_interval = self._calculate_prediction_interval(
                current_price, predicted_return, df, horizon, confidence_score
            )

            forecast = StockForecast(
                horizon_days=horizon,
                predicted_price=round(predicted_price, 2),
                predicted_return=round(predicted_return, 6),
                confidence_score=round(confidence_score, 4),
                prediction_interval=prediction_interval
            )

            logger.debug(f"{ticker} {horizon}d: price=${predicted_price:.2f}, return={predicted_return:.4f}")
            return forecast

        except Exception as e:
            logger.error(f"Failed to predict horizon {horizon} for {ticker}: {e}")
            raise

    async def _predict_return(
        self,
        features: Dict[str, float],
        horizon: int
    ) -> float:
        """
        Predict expected return using features.

        This is a simplified model. In production, this would use
        trained Qlib LightGBM/LSTM models.

        Args:
            features: Calculated features
            horizon: Forecast horizon

        Returns:
            Predicted return (e.g., 0.05 = 5% gain)
        """
        # Weighted combination of momentum and trend indicators
        # This is a placeholder - will be replaced with actual Qlib model inference

        momentum_5d = features.get('momentum_5', 0)
        momentum_10d = features.get('momentum_10', 0)
        ma_trend = features.get('ma_trend', 0)
        rsi = features.get('rsi', 50)

        # Simple weighted model
        # Normalize RSI to -1 to 1 range (RSI 50 = neutral)
        rsi_signal = (rsi - 50) / 50

        # Combine signals
        if horizon == 1:
            # Short term: more weight on momentum
            predicted_return = (
                0.5 * momentum_5d +
                0.3 * ma_trend +
                0.2 * rsi_signal * 0.01
            )
        elif horizon == 5:
            # Medium term: balanced
            predicted_return = (
                0.3 * momentum_5d +
                0.3 * momentum_10d +
                0.3 * ma_trend +
                0.1 * rsi_signal * 0.01
            )
        else:
            # Long term: more weight on trend
            predicted_return = (
                0.2 * momentum_10d +
                0.5 * ma_trend +
                0.3 * rsi_signal * 0.01
            )

        # Scale by horizon (sqrt scaling for mean reversion)
        scaling_factor = np.sqrt(horizon / 5.0)
        predicted_return *= scaling_factor

        # Clamp to reasonable range (-20% to +20%)
        predicted_return = np.clip(predicted_return, -0.20, 0.20)

        return float(predicted_return)

    def _calculate_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate technical features from price data.

        Args:
            df: Price DataFrame

        Returns:
            Dictionary of features
        """
        try:
            latest = df.iloc[-1]
            features = {}

            # Momentum features
            if len(df) >= 5:
                features['momentum_5'] = (latest['close'] / df.iloc[-5]['close']) - 1
            if len(df) >= 10:
                features['momentum_10'] = (latest['close'] / df.iloc[-10]['close']) - 1
            if len(df) >= 20:
                features['momentum_20'] = (latest['close'] / df.iloc[-20]['close']) - 1

            # Moving average features
            if 'ma_5' in df.columns:
                features['ma_5'] = latest['ma_5']
            if 'ma_10' in df.columns:
                features['ma_10'] = latest['ma_10']
            if 'ma_20' in df.columns:
                features['ma_20'] = latest['ma_20']

            # MA trend (price vs MA20)
            if 'ma_20' in df.columns and not pd.isna(latest['ma_20']):
                features['ma_trend'] = (latest['close'] / latest['ma_20']) - 1

            # RSI
            if 'rsi_14' in df.columns and not pd.isna(latest['rsi_14']):
                features['rsi'] = latest['rsi_14']
            else:
                features['rsi'] = 50  # neutral

            # Volatility
            if 'volatility_20' in df.columns and not pd.isna(latest['volatility_20']):
                features['volatility'] = latest['volatility_20']
            else:
                features['volatility'] = df['close'].pct_change().std()

            # Volume trend
            if 'volume_ratio' in df.columns and not pd.isna(latest['volume_ratio']):
                features['volume_ratio'] = latest['volume_ratio']

            return features

        except Exception as e:
            logger.error(f"Failed to calculate features: {e}")
            return {}

    def _calculate_confidence(self, df: pd.DataFrame, horizon: int) -> float:
        """
        Calculate confidence score for prediction.

        Args:
            df: Price DataFrame
            horizon: Forecast horizon

        Returns:
            Confidence score (0 to 1)
        """
        try:
            confidence = 1.0

            # Reduce confidence for longer horizons
            horizon_penalty = 0.1 * (horizon / 10.0)
            confidence -= min(horizon_penalty, 0.3)

            # Reduce confidence for high volatility
            if 'volatility_20' in df.columns:
                volatility = df['volatility_20'].iloc[-1]
                if not pd.isna(volatility):
                    vol_penalty = min(volatility * 5, 0.3)  # Cap at 0.3
                    confidence -= vol_penalty

            # Reduce confidence for insufficient data
            data_points = len(df)
            if data_points < 60:
                data_penalty = (60 - data_points) / 60 * 0.2
                confidence -= data_penalty

            # Ensure confidence is between 0.3 and 1.0
            confidence = np.clip(confidence, 0.3, 1.0)

            return float(confidence)

        except Exception as e:
            logger.error(f"Failed to calculate confidence: {e}")
            return 0.5  # default moderate confidence

    def _calculate_prediction_interval(
        self,
        current_price: float,
        predicted_return: float,
        df: pd.DataFrame,
        horizon: int,
        confidence_score: float
    ) -> PredictionInterval:
        """
        Calculate prediction interval (confidence bounds).

        Args:
            current_price: Current stock price
            predicted_return: Predicted return
            df: Price DataFrame
            horizon: Forecast horizon
            confidence_score: Confidence score

        Returns:
            PredictionInterval with lower and upper bounds
        """
        try:
            # Calculate historical volatility
            returns = df['close'].pct_change().dropna()
            volatility = returns.std()

            # Scale volatility by horizon (sqrt of time)
            scaled_vol = volatility * np.sqrt(horizon)

            # 95% confidence interval (approximately 2 standard deviations)
            z_score = 1.96

            # Adjust interval width based on confidence score
            # Lower confidence = wider interval
            interval_multiplier = (2.0 - confidence_score)

            # Calculate bounds
            predicted_price = current_price * (1 + predicted_return)
            interval_half_width = predicted_price * scaled_vol * z_score * interval_multiplier

            lower_bound = predicted_price - interval_half_width
            upper_bound = predicted_price + interval_half_width

            # Ensure lower bound is not negative
            lower_bound = max(lower_bound, 0.01)

            return PredictionInterval(
                lower=round(float(lower_bound), 2),
                upper=round(float(upper_bound), 2)
            )

        except Exception as e:
            logger.error(f"Failed to calculate prediction interval: {e}")
            # Fallback: +/- 20%
            predicted_price = current_price * (1 + predicted_return)
            return PredictionInterval(
                lower=round(predicted_price * 0.8, 2),
                upper=round(predicted_price * 1.2, 2)
            )

    def _detect_trend(
        self,
        df: pd.DataFrame,
        forecasts: List[StockForecast]
    ) -> str:
        """
        Detect overall trend from forecasts and historical data.

        Args:
            df: Price DataFrame
            forecasts: List of forecasts

        Returns:
            Trend classification: "bullish", "bearish", or "neutral"
        """
        try:
            # Average predicted return across horizons
            avg_return = np.mean([f.predicted_return for f in forecasts])

            # Check recent price momentum
            if len(df) >= 10:
                recent_momentum = (df['close'].iloc[-1] / df['close'].iloc[-10]) - 1
            else:
                recent_momentum = 0

            # Combined signal
            combined_signal = 0.6 * avg_return + 0.4 * recent_momentum

            # Classify trend
            if combined_signal > 0.02:  # > 2% expected gain
                return "bullish"
            elif combined_signal < -0.02:  # > 2% expected loss
                return "bearish"
            else:
                return "neutral"

        except Exception as e:
            logger.error(f"Failed to detect trend: {e}")
            return "neutral"

    def _forecast_volatility(self, df: pd.DataFrame) -> float:
        """
        Forecast future volatility.

        Args:
            df: Price DataFrame

        Returns:
            Forecasted volatility (annualized)
        """
        try:
            # Calculate historical volatility (20-day)
            returns = df['close'].pct_change().dropna()

            if len(returns) < 20:
                # Insufficient data, use all available
                hist_vol = returns.std()
            else:
                # Use last 20 days
                hist_vol = returns.tail(20).std()

            # Annualize (assuming 252 trading days)
            annualized_vol = hist_vol * np.sqrt(252)

            # Apply EWMA for recent volatility changes
            if len(returns) >= 20:
                ewma_vol = returns.ewm(span=20).std().iloc[-1] * np.sqrt(252)
                # Blend historical and EWMA
                forecasted_vol = 0.7 * annualized_vol + 0.3 * ewma_vol
            else:
                forecasted_vol = annualized_vol

            return round(float(forecasted_vol), 4)

        except Exception as e:
            logger.error(f"Failed to forecast volatility: {e}")
            return 0.20  # default 20% annualized volatility

    def _prepare_dataframe(self, stock_data: StockData) -> pd.DataFrame:
        """
        Prepare DataFrame with technical indicators.

        Args:
            stock_data: Stock data

        Returns:
            DataFrame with calculated indicators
        """
        # Convert to DataFrame
        records = []
        for price in stock_data.prices:
            records.append({
                'date': price.date,
                'open': price.open,
                'high': price.high,
                'low': price.low,
                'close': price.close,
                'volume': price.volume
            })

        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)

        # Calculate technical indicators
        df = self._add_technical_indicators(df)

        return df

    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators to DataFrame.

        Args:
            df: Price DataFrame

        Returns:
            DataFrame with indicators
        """
        # Moving averages
        df['ma_5'] = df['close'].rolling(window=5).mean()
        df['ma_10'] = df['close'].rolling(window=10).mean()
        df['ma_20'] = df['close'].rolling(window=20).mean()

        # Volatility
        df['return'] = df['close'].pct_change()
        df['volatility_20'] = df['return'].rolling(window=20).std()

        # Volume indicators
        df['volume_ma_5'] = df['volume'].rolling(window=5).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma_5']

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi_14'] = 100 - (100 / (1 + rs))

        return df

    async def predict_multiple_stocks(
        self,
        stocks_data: List[StockData],
        horizons: Optional[List[int]] = None
    ) -> List[StockPrediction]:
        """
        Predict prices for multiple stocks.

        Args:
            stocks_data: List of stock data
            horizons: Forecast horizons

        Returns:
            List of predictions
        """
        predictions = []

        for stock_data in stocks_data:
            try:
                prediction = await self.predict_stock_price(stock_data, horizons)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Failed to predict {stock_data.ticker}: {e}")
                # Continue with other stocks

        logger.info(f"Generated predictions for {len(predictions)}/{len(stocks_data)} stocks")
        return predictions
