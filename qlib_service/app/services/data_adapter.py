"""
Data adapter to convert AI extracted data to Qlib format.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, date
from loguru import logger

from app.models.schemas import (
    ExtractedData,
    StockData,
    PriceData,
    Portfolio,
    MarketContext
)


class QlibDataAdapter:
    """Adapter to convert extracted data to Qlib-compatible format."""

    def __init__(self):
        """Initialize the data adapter."""
        logger.info("Initializing Qlib Data Adapter")

    def convert_to_qlib_dataframe(
        self,
        stock_data: StockData
    ) -> pd.DataFrame:
        """
        Convert stock price data to Qlib DataFrame format.

        Args:
            stock_data: Stock data from AI extraction

        Returns:
            DataFrame in Qlib format with columns: date, open, high, low, close, volume
        """
        try:
            # Extract price records
            records = []
            for price in stock_data.prices:
                records.append({
                    'date': price.date,
                    'open': price.open,
                    'high': price.high,
                    'low': price.low,
                    'close': price.close,
                    'volume': price.volume,
                    'adj_close': price.adj_close if price.adj_close else price.close
                })

            # Create DataFrame
            df = pd.DataFrame(records)

            # Set date as index
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

            # Sort by date
            df.sort_index(inplace=True)

            # Add ticker column
            df['ticker'] = stock_data.ticker

            logger.debug(f"Converted {len(df)} price records for {stock_data.ticker}")
            return df

        except Exception as e:
            logger.error(f"Failed to convert stock data for {stock_data.ticker}: {e}")
            raise

    def prepare_stock_features(
        self,
        stock_data: StockData
    ) -> Dict[str, Any]:
        """
        Prepare stock features for Qlib model input.

        Args:
            stock_data: Stock data from AI extraction

        Returns:
            Dictionary of features including prices, metrics, and fundamentals
        """
        features = {
            'ticker': stock_data.ticker,
            'name': stock_data.name,
            'price_df': self.convert_to_qlib_dataframe(stock_data)
        }

        # Add financial metrics if available
        if stock_data.financial_metrics:
            features['metrics'] = {
                'pe_ratio': stock_data.financial_metrics.pe_ratio,
                'market_cap': stock_data.financial_metrics.market_cap,
                'eps': stock_data.financial_metrics.eps,
                'dividend_yield': stock_data.financial_metrics.dividend_yield,
                'beta': stock_data.financial_metrics.beta
            }

        # Add fundamentals if available
        if stock_data.fundamentals:
            features['fundamentals'] = {
                'revenue': stock_data.fundamentals.revenue,
                'net_income': stock_data.fundamentals.net_income,
                'total_assets': stock_data.fundamentals.total_assets,
                'total_liabilities': stock_data.fundamentals.total_liabilities,
                'cash_flow': stock_data.fundamentals.cash_flow
            }

            # Calculate derived ratios
            if stock_data.fundamentals.total_assets and stock_data.fundamentals.total_liabilities:
                features['fundamentals']['debt_to_asset_ratio'] = (
                    stock_data.fundamentals.total_liabilities /
                    stock_data.fundamentals.total_assets
                )

        return features

    def convert_extracted_data(
        self,
        extracted_data: ExtractedData
    ) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Any]]:
        """
        Convert complete extracted data to Qlib format.

        Args:
            extracted_data: All extracted data from AI service

        Returns:
            Tuple of (stock_dataframes, metadata)
        """
        try:
            stock_dfs = {}
            metadata = {
                'tickers': [],
                'market_context': {
                    'region': extracted_data.market_context.region,
                    'sector': extracted_data.market_context.sector,
                    'benchmark': extracted_data.market_context.benchmark_index,
                    'risk_free_rate': extracted_data.market_context.risk_free_rate
                }
            }

            # Convert each stock
            for stock_data in extracted_data.stocks:
                ticker = stock_data.ticker
                metadata['tickers'].append(ticker)

                # Convert to DataFrame
                df = self.convert_to_qlib_dataframe(stock_data)
                stock_dfs[ticker] = df

                # Add features
                features = self.prepare_stock_features(stock_data)
                metadata[ticker] = {
                    'name': stock_data.name,
                    'metrics': features.get('metrics', {}),
                    'fundamentals': features.get('fundamentals', {})
                }

            # Add portfolio information if available
            if extracted_data.portfolio:
                metadata['portfolio'] = {
                    'total_value': extracted_data.portfolio.total_value,
                    'positions': [
                        {
                            'ticker': pos.ticker,
                            'shares': pos.shares,
                            'avg_cost': pos.avg_cost,
                            'current_value': pos.current_value,
                            'weight': pos.weight
                        }
                        for pos in extracted_data.portfolio.positions
                    ]
                }

            logger.info(f"Converted data for {len(stock_dfs)} stocks")
            return stock_dfs, metadata

        except Exception as e:
            logger.error(f"Failed to convert extracted data: {e}")
            raise

    def create_qlib_dataset(
        self,
        stock_dfs: Dict[str, pd.DataFrame],
        start_date: str = None,
        end_date: str = None
    ) -> pd.DataFrame:
        """
        Create a combined dataset suitable for Qlib model training/prediction.

        Args:
            stock_dfs: Dictionary of ticker -> DataFrame
            start_date: Start date filter (optional)
            end_date: End date filter (optional)

        Returns:
            Combined DataFrame with all stocks
        """
        try:
            # Combine all stock dataframes
            all_dfs = []

            for ticker, df in stock_dfs.items():
                df_copy = df.copy()
                df_copy['ticker'] = ticker

                # Filter by date if specified
                if start_date:
                    df_copy = df_copy[df_copy.index >= pd.to_datetime(start_date)]
                if end_date:
                    df_copy = df_copy[df_copy.index <= pd.to_datetime(end_date)]

                all_dfs.append(df_copy)

            # Concatenate all dataframes
            combined_df = pd.concat(all_dfs, axis=0)

            # Sort by ticker and date
            combined_df.sort_values(['ticker', combined_df.index], inplace=True)

            logger.info(f"Created combined dataset with {len(combined_df)} records")
            return combined_df

        except Exception as e:
            logger.error(f"Failed to create Qlib dataset: {e}")
            raise

    def calculate_technical_indicators(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate basic technical indicators for Qlib.

        Args:
            df: Price DataFrame

        Returns:
            DataFrame with additional technical indicator columns
        """
        try:
            df = df.copy()

            # Calculate returns
            df['return'] = df['close'].pct_change()
            df['log_return'] = np.log(df['close'] / df['close'].shift(1))

            # Moving averages
            df['ma_5'] = df['close'].rolling(window=5).mean()
            df['ma_10'] = df['close'].rolling(window=10).mean()
            df['ma_20'] = df['close'].rolling(window=20).mean()

            # Volatility (20-day rolling std of returns)
            df['volatility_20'] = df['return'].rolling(window=20).std()

            # Volume indicators
            df['volume_ma_5'] = df['volume'].rolling(window=5).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma_5']

            # Price momentum
            df['momentum_5'] = df['close'] / df['close'].shift(5) - 1
            df['momentum_10'] = df['close'] / df['close'].shift(10) - 1

            # High-Low range
            df['hl_ratio'] = (df['high'] - df['low']) / df['close']

            # RSI (Relative Strength Index) - simplified
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi_14'] = 100 - (100 / (1 + rs))

            logger.debug(f"Calculated technical indicators for {len(df)} records")
            return df

        except Exception as e:
            logger.error(f"Failed to calculate technical indicators: {e}")
            raise

    def validate_data_quality(
        self,
        df: pd.DataFrame,
        ticker: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate data quality for Qlib processing.

        Args:
            df: Price DataFrame
            ticker: Stock ticker

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        # Check for minimum data points
        if len(df) < 30:
            issues.append(f"Insufficient data: only {len(df)} records (minimum 30 required)")

        # Check for missing values
        missing_cols = df.columns[df.isnull().any()].tolist()
        if missing_cols:
            issues.append(f"Missing values in columns: {missing_cols}")

        # Check for price anomalies
        if (df['high'] < df['low']).any():
            issues.append("Invalid prices: high < low detected")

        if (df['close'] < 0).any():
            issues.append("Invalid prices: negative close prices detected")

        # Check for volume anomalies
        if (df['volume'] < 0).any():
            issues.append("Invalid volume: negative volume detected")

        # Check for extreme price changes (> 50% in one day)
        returns = df['close'].pct_change().abs()
        if (returns > 0.5).any():
            issues.append("Extreme price changes detected (>50% in single day)")

        is_valid = len(issues) == 0

        if not is_valid:
            logger.warning(f"Data quality issues for {ticker}: {issues}")
        else:
            logger.debug(f"Data quality validation passed for {ticker}")

        return is_valid, issues
