"""
Application configuration settings.
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service Configuration
    service_host: str = Field(default="0.0.0.0", alias="QLIB_SERVICE_HOST")
    service_port: int = Field(default=8081, alias="QLIB_SERVICE_PORT")
    service_name: str = Field(default="qlib-advisor-predictor", alias="SERVICE_NAME")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Database Configuration
    database_url: str = Field(..., alias="DATABASE_URL")

    # RabbitMQ Configuration
    rabbitmq_host: str = Field(default="rabbitmq", alias="RABBITMQ_HOST")
    rabbitmq_port: int = Field(default=5672, alias="RABBITMQ_PORT")
    rabbitmq_username: str = Field(default="guest", alias="RABBITMQ_USERNAME")
    rabbitmq_password: str = Field(default="guest", alias="RABBITMQ_PASSWORD")
    rabbitmq_vhost: str = Field(default="/", alias="RABBITMQ_VHOST")
    rabbitmq_heartbeat: int = Field(default=60, alias="RABBITMQ_HEARTBEAT")

    # Queue Names
    queue_ai_extraction_complete: str = Field(
        default="ai_extraction_complete",
        alias="QUEUE_AI_EXTRACTION_COMPLETE"
    )
    queue_qlib_predictions_ready: str = Field(
        default="qlib_predictions_ready",
        alias="QUEUE_QLIB_PREDICTIONS_READY"
    )
    queue_dlq: str = Field(default="qlib_predictions_dlq", alias="QUEUE_DLQ")

    # Exchange Names
    exchange_name: str = Field(default="khengleong.direct", alias="EXCHANGE_NAME")
    exchange_type: str = Field(default="direct", alias="EXCHANGE_TYPE")

    # Qlib Configuration
    qlib_region: str = Field(default="cn", alias="QLIB_REGION")
    qlib_provider_uri: str = Field(
        default="/app/qlib_data/cn_data",
        alias="QLIB_PROVIDER_URI"
    )
    qlib_data_dir: str = Field(default="/app/qlib_data", alias="QLIB_DATA_DIR")
    qlib_models_dir: str = Field(default="/app/models_storage", alias="QLIB_MODELS_DIR")

    # Qlib Model Settings
    qlib_default_model: str = Field(default="lightgbm", alias="QLIB_DEFAULT_MODEL")
    qlib_forecast_horizons: str = Field(default="1,5,30", alias="QLIB_FORECAST_HORIZONS")
    qlib_cache_models: bool = Field(default=True, alias="QLIB_CACHE_MODELS")
    qlib_feature_set: str = Field(default="alpha158", alias="QLIB_FEATURE_SET")

    # Performance Tuning
    qlib_max_workers: int = Field(default=4, alias="QLIB_MAX_WORKERS")
    qlib_batch_size: int = Field(default=10, alias="QLIB_BATCH_SIZE")
    qlib_prediction_timeout: int = Field(default=300, alias="QLIB_PREDICTION_TIMEOUT")
    consumer_prefetch_count: int = Field(default=1, alias="CONSUMER_PREFETCH_COUNT")

    # Feature Flags
    enable_forecasting: bool = Field(default=True, alias="ENABLE_FORECASTING")
    enable_portfolio_analysis: bool = Field(default=True, alias="ENABLE_PORTFOLIO_ANALYSIS")
    enable_recommendations: bool = Field(default=True, alias="ENABLE_RECOMMENDATIONS")
    enable_backtesting: bool = Field(default=False, alias="ENABLE_BACKTESTING")

    # Monitoring
    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, alias="METRICS_PORT")

    # Security
    api_key_enabled: bool = Field(default=False, alias="API_KEY_ENABLED")
    api_key: str = Field(default="", alias="API_KEY")

    # Development Settings
    debug: bool = Field(default=False, alias="DEBUG")
    reload: bool = Field(default=False, alias="RELOAD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def rabbitmq_url(self) -> str:
        """Generate RabbitMQ connection URL."""
        return (
            f"amqp://{self.rabbitmq_username}:{self.rabbitmq_password}@"
            f"{self.rabbitmq_host}:{self.rabbitmq_port}{self.rabbitmq_vhost}"
        )

    @property
    def forecast_horizons_list(self) -> List[int]:
        """Parse forecast horizons from comma-separated string."""
        return [int(h.strip()) for h in self.qlib_forecast_horizons.split(",")]

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v


# Global settings instance
settings = Settings()
