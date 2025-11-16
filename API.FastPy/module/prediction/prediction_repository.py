"""
Repository for Prediction database operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from .PredictionModel import (
    PredictionRequest,
    StockPrediction,
    PortfolioAnalysis,
    Recommendation,
    MarketRegime
)


class PredictionRepository:
    """Repository for managing prediction data."""

    def __init__(self, db: Session):
        self.db = db

    # ===========================
    # Prediction Request Methods
    # ===========================

    def create_prediction_request(
        self,
        request_id: str,
        report_id: Optional[int] = None
    ) -> PredictionRequest:
        """Create a new prediction request."""
        prediction_request = PredictionRequest(
            request_id=request_id,
            report_id=report_id,
            status="pending",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(prediction_request)
        self.db.commit()
        self.db.refresh(prediction_request)
        return prediction_request

    def get_prediction_request_by_id(self, request_id: int) -> Optional[PredictionRequest]:
        """Get prediction request by ID."""
        return self.db.query(PredictionRequest).filter(PredictionRequest.id == request_id).first()

    def get_prediction_request_by_request_id(self, request_id: str) -> Optional[PredictionRequest]:
        """Get prediction request by request_id string."""
        return self.db.query(PredictionRequest).filter(PredictionRequest.request_id == request_id).first()

    def get_prediction_request_by_report_id(self, report_id: int) -> Optional[PredictionRequest]:
        """Get prediction request by report_id."""
        return self.db.query(PredictionRequest).filter(PredictionRequest.report_id == report_id).first()

    def get_all_prediction_requests(self, skip: int = 0, limit: int = 100) -> List[PredictionRequest]:
        """Get all prediction requests with pagination."""
        return self.db.query(PredictionRequest)\
            .order_by(desc(PredictionRequest.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()

    def update_prediction_request_status(
        self,
        request_id: str,
        status: str,
        prediction_status: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Optional[PredictionRequest]:
        """Update prediction request status."""
        prediction_request = self.get_prediction_request_by_request_id(request_id)
        if prediction_request:
            prediction_request.status = status
            prediction_request.updated_at = datetime.utcnow()

            if prediction_status:
                prediction_request.prediction_status = prediction_status

            if error_message:
                prediction_request.error_message = error_message

            if status == "processing" and not prediction_request.processing_started_at:
                prediction_request.processing_started_at = datetime.utcnow()

            if status in ["success", "failed"] and not prediction_request.processing_completed_at:
                prediction_request.processing_completed_at = datetime.utcnow()
                if prediction_request.processing_started_at:
                    delta = prediction_request.processing_completed_at - prediction_request.processing_started_at
                    prediction_request.processing_time_seconds = delta.total_seconds()

            self.db.commit()
            self.db.refresh(prediction_request)
        return prediction_request

    def update_prediction_metadata(
        self,
        request_id: str,
        model_name: str,
        model_version: str,
        feature_set: str
    ) -> Optional[PredictionRequest]:
        """Update prediction metadata."""
        prediction_request = self.get_prediction_request_by_request_id(request_id)
        if prediction_request:
            prediction_request.model_name = model_name
            prediction_request.model_version = model_version
            prediction_request.feature_set = feature_set
            prediction_request.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(prediction_request)
        return prediction_request

    # ===========================
    # Stock Prediction Methods
    # ===========================

    def create_stock_prediction(
        self,
        prediction_request_id: int,
        ticker: str,
        current_price: float,
        trend: str,
        volatility_forecast: float,
        forecasts: list
    ) -> StockPrediction:
        """Create a stock prediction."""
        stock_prediction = StockPrediction(
            prediction_request_id=prediction_request_id,
            ticker=ticker,
            current_price=current_price,
            trend=trend,
            volatility_forecast=volatility_forecast,
            forecasts=forecasts,
            created_at=datetime.utcnow()
        )
        self.db.add(stock_prediction)
        self.db.commit()
        self.db.refresh(stock_prediction)
        return stock_prediction

    def get_stock_predictions_by_request(self, prediction_request_id: int) -> List[StockPrediction]:
        """Get all stock predictions for a request."""
        return self.db.query(StockPrediction)\
            .filter(StockPrediction.prediction_request_id == prediction_request_id)\
            .all()

    def get_stock_prediction_by_ticker(self, prediction_request_id: int, ticker: str) -> Optional[StockPrediction]:
        """Get stock prediction for a specific ticker."""
        return self.db.query(StockPrediction)\
            .filter(
                StockPrediction.prediction_request_id == prediction_request_id,
                StockPrediction.ticker == ticker
            )\
            .first()

    # ===========================
    # Portfolio Analysis Methods
    # ===========================

    def create_portfolio_analysis(
        self,
        prediction_request_id: int,
        sharpe_ratio: float,
        max_drawdown: float,
        volatility: float,
        value_at_risk_95: float,
        beta: float,
        alpha: float,
        expected_return_1d: float,
        expected_return_5d: float,
        expected_return_30d: float,
        diversification_score: float,
        risk_level: str
    ) -> PortfolioAnalysis:
        """Create a portfolio analysis."""
        portfolio_analysis = PortfolioAnalysis(
            prediction_request_id=prediction_request_id,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            volatility=volatility,
            value_at_risk_95=value_at_risk_95,
            beta=beta,
            alpha=alpha,
            expected_return_1d=expected_return_1d,
            expected_return_5d=expected_return_5d,
            expected_return_30d=expected_return_30d,
            diversification_score=diversification_score,
            risk_level=risk_level,
            created_at=datetime.utcnow()
        )
        self.db.add(portfolio_analysis)
        self.db.commit()
        self.db.refresh(portfolio_analysis)
        return portfolio_analysis

    def get_portfolio_analysis_by_request(self, prediction_request_id: int) -> Optional[PortfolioAnalysis]:
        """Get portfolio analysis for a request."""
        return self.db.query(PortfolioAnalysis)\
            .filter(PortfolioAnalysis.prediction_request_id == prediction_request_id)\
            .first()

    # ===========================
    # Recommendation Methods
    # ===========================

    def create_recommendation(
        self,
        prediction_request_id: int,
        ticker: str,
        action: str,
        strength: str,
        confidence: float,
        target_price: Optional[float],
        stop_loss: Optional[float],
        rationale: str,
        technical_score: float,
        fundamental_score: float,
        sentiment_score: float
    ) -> Recommendation:
        """Create a recommendation."""
        recommendation = Recommendation(
            prediction_request_id=prediction_request_id,
            ticker=ticker,
            action=action,
            strength=strength,
            confidence=confidence,
            target_price=target_price,
            stop_loss=stop_loss,
            rationale=rationale,
            technical_score=technical_score,
            fundamental_score=fundamental_score,
            sentiment_score=sentiment_score,
            created_at=datetime.utcnow()
        )
        self.db.add(recommendation)
        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation

    def get_recommendations_by_request(self, prediction_request_id: int) -> List[Recommendation]:
        """Get all recommendations for a request."""
        return self.db.query(Recommendation)\
            .filter(Recommendation.prediction_request_id == prediction_request_id)\
            .all()

    def get_recommendation_by_ticker(self, prediction_request_id: int, ticker: str) -> Optional[Recommendation]:
        """Get recommendation for a specific ticker."""
        return self.db.query(Recommendation)\
            .filter(
                Recommendation.prediction_request_id == prediction_request_id,
                Recommendation.ticker == ticker
            )\
            .first()

    # ===========================
    # Market Regime Methods
    # ===========================

    def create_market_regime(
        self,
        prediction_request_id: int,
        regime: str,
        confidence: float,
        description: str
    ) -> MarketRegime:
        """Create a market regime."""
        market_regime = MarketRegime(
            prediction_request_id=prediction_request_id,
            regime=regime,
            confidence=confidence,
            description=description,
            created_at=datetime.utcnow()
        )
        self.db.add(market_regime)
        self.db.commit()
        self.db.refresh(market_regime)
        return market_regime

    def get_market_regime_by_request(self, prediction_request_id: int) -> Optional[MarketRegime]:
        """Get market regime for a request."""
        return self.db.query(MarketRegime)\
            .filter(MarketRegime.prediction_request_id == prediction_request_id)\
            .first()

    # ===========================
    # Utility Methods
    # ===========================

    def delete_prediction_request(self, request_id: str) -> bool:
        """Delete a prediction request and all related data (cascade)."""
        prediction_request = self.get_prediction_request_by_request_id(request_id)
        if prediction_request:
            self.db.delete(prediction_request)
            self.db.commit()
            return True
        return False

    def count_all_predictions(self) -> int:
        """Count total number of prediction requests."""
        return self.db.query(PredictionRequest).count()
