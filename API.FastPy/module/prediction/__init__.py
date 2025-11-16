"""
Prediction module for handling Qlib prediction results.
"""
from .PredictionModel import (
    PredictionRequest,
    StockPrediction,
    PortfolioAnalysis,
    Recommendation,
    MarketRegime
)
from .PredictionDTO import (
    PredictionRequestDTO,
    PredictionResultsDTO,
    StockPredictionDTO,
    PortfolioAnalysisDTO,
    RecommendationDTO,
    MarketRegimeDTO,
    PredictionRequestListDTO,
    PredictionStatusDTO
)
from .prediction_consumer import start_prediction_consumer_background, get_prediction_consumer

__all__ = [
    # Models
    "PredictionRequest",
    "StockPrediction",
    "PortfolioAnalysis",
    "Recommendation",
    "MarketRegime",
    # DTOs
    "PredictionRequestDTO",
    "PredictionResultsDTO",
    "StockPredictionDTO",
    "PortfolioAnalysisDTO",
    "RecommendationDTO",
    "MarketRegimeDTO",
    "PredictionRequestListDTO",
    "PredictionStatusDTO",
    # Consumer
    "start_prediction_consumer_background",
    "get_prediction_consumer",
]
