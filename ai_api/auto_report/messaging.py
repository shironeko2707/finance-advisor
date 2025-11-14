"""
RabbitMQ messaging module for auto report system.
"""
import os
import json
import asyncio
import tempfile
import base64
from datetime import datetime
from typing import List, Optional, Dict, Any, Callable
from pathlib import Path

import aiofiles
from aio_pika import connect_robust, Message, DeliveryMode
from aio_pika.abc import AbstractRobustConnection, AbstractChannel, AbstractQueue
from loguru import logger
from pydantic import BaseModel, Field

from .main import main as process_report


class FileData(BaseModel):
    """Represents a file with its content and metadata."""
    filename: str
    content: str = Field(..., description="Base64 encoded file content")
    content_type: str = Field(default="application/octet-stream")


class ReportRequest(BaseModel):
    """Request message for report generation."""
    request_id: str = Field(..., description="Unique identifier for the request")
    template_file: FileData = Field(..., description="Excel template file")
    pdf_files: List[FileData] = Field(..., description="List of PDF files to process")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    
class ReportResponse(BaseModel):
    """Response message for report generation."""
    request_id: str = Field(..., description="Original request identifier")
    success: bool = Field(..., description="Whether processing was successful")
    result_file: Optional[FileData] = Field(None, description="Generated Excel file")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    processing_time_seconds: Optional[float] = Field(None, description="Time taken to process")
    timestamp: datetime = Field(default_factory=datetime.now)


class RabbitMQConfig(BaseModel):
    """RabbitMQ connection configuration."""
    host: str = Field(default="localhost")
    port: int = Field(default=5672)
    username: str = Field(default="guest")
    password: str = Field(default="guest")
    virtual_host: str = Field(default="/")
    request_queue: str = Field(default="report_requests")
    response_queue: str = Field(default="report_responses")
    exchange: str = Field(default="")
    
    @classmethod
    def from_env(cls) -> "RabbitMQConfig":
        """Create config from environment variables."""
        return cls(
            host=os.getenv("RABBITMQ_HOST", "localhost"),
            port=int(os.getenv("RABBITMQ_PORT", "5672")),
            username=os.getenv("RABBITMQ_USERNAME", "guest"),
            password=os.getenv("RABBITMQ_PASSWORD", "guest"),
            virtual_host=os.getenv("RABBITMQ_VIRTUAL_HOST", "/"),
            request_queue=os.getenv("RABBITMQ_REQUEST_QUEUE", "report_requests"),
            response_queue=os.getenv("RABBITMQ_RESPONSE_QUEUE", "report_responses"),
            exchange=os.getenv("RABBITMQ_EXCHANGE", "")
        )
    
    @property
    def connection_url(self) -> str:
        """Generate RabbitMQ connection URL."""
        return f"amqp://{self.username}:{self.password}@{self.host}:{self.port}{self.virtual_host}"


class RabbitMQManager:
    """Manages RabbitMQ connections and messaging."""
    
    def __init__(self, config: RabbitMQConfig):
        self.config = config
        self.connection: Optional[AbstractRobustConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.request_queue: Optional[AbstractQueue] = None
        self.response_queue: Optional[AbstractQueue] = None
        
    async def connect(self) -> None:
        """Establish connection to RabbitMQ."""
        try:
            self.connection = await connect_robust(self.config.connection_url)
            self.channel = await self.connection.channel()
            
            # Declare queues
            self.request_queue = await self.channel.declare_queue(
                self.config.request_queue, durable=True
            )
            self.response_queue = await self.channel.declare_queue(
                self.config.response_queue, durable=True
            )
            
            logger.info(f"Connected to RabbitMQ at {self.config.host}:{self.config.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")
    
    async def publish_response(self, response: ReportResponse) -> None:
        """Publish response message to response queue."""
        if not self.channel or not self.response_queue:
            raise RuntimeError("RabbitMQ not connected")
        
        message_body = response.model_dump_json().encode()
        message = Message(
            message_body,
            delivery_mode=DeliveryMode.PERSISTENT
        )
        
        await self.channel.default_exchange.publish(
            message, routing_key=self.config.response_queue
        )
        
        logger.info(f"Published response for request {response.request_id}")
    
    async def start_consumer(self, message_handler: Callable[[ReportRequest], None]) -> None:
        """Start consuming messages from request queue."""
        if not self.request_queue:
            raise RuntimeError("RabbitMQ not connected")
        
        async def process_message(message) -> None:
            async with message.process():
                try:
                    # Parse message
                    request_data = json.loads(message.body.decode())
                    request = ReportRequest(**request_data)
                    
                    logger.info(f"Received request {request.request_id}")
                    
                    # Process request
                    await message_handler(request)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        
        # Start consuming
        await self.request_queue.consume(process_message)
        logger.info("Started consuming messages from request queue")


class ReportService:
    """Service for processing report requests via RabbitMQ."""
    
    def __init__(self, config: Optional[RabbitMQConfig] = None):
        self.config = config or RabbitMQConfig.from_env()
        self.rabbitmq = RabbitMQManager(self.config)
        
    async def start(self) -> None:
        """Start the service."""
        await self.rabbitmq.connect()
        await self.rabbitmq.start_consumer(self._handle_request)
        
        logger.info("Report service started")
        
        # Keep the service running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Shutting down service...")
        finally:
            await self.rabbitmq.disconnect()
    
    async def _handle_request(self, request: ReportRequest) -> None:
        """Handle incoming report request."""
        start_time = datetime.now()
        
        try:
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Save template file
                template_path = await self._save_file(
                    request.template_file, temp_path / request.template_file.filename
                )
                
                # Save PDF files
                pdf_paths = []
                for pdf_file in request.pdf_files:
                    pdf_path = await self._save_file(
                        pdf_file, temp_path / pdf_file.filename
                    )
                    pdf_paths.append(str(pdf_path))
                
                # Process report
                logger.info(f"Processing request {request.request_id}")
                output_path = await process_report(
                    template_path=str(template_path),
                    document_path=pdf_paths
                )
                
                # Read result file
                result_file = await self._read_file_as_base64(output_path)
                
                # Calculate processing time
                processing_time = (datetime.now() - start_time).total_seconds()
                
                # Create response
                response = ReportResponse(
                    request_id=request.request_id,
                    success=True,
                    result_file=FileData(
                        filename=os.path.basename(output_path),
                        content=result_file,
                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    ),
                    processing_time_seconds=processing_time
                )
                
                logger.info(f"Successfully processed request {request.request_id} in {processing_time:.2f}s")
                
        except Exception as e:
            logger.error(f"Failed to process request {request.request_id}: {e}")
            
            # Create error response
            processing_time = (datetime.now() - start_time).total_seconds()
            response = ReportResponse(
                request_id=request.request_id,
                success=False,
                error_message=str(e),
                processing_time_seconds=processing_time
            )
        
        # Send response
        await self.rabbitmq.publish_response(response)
    
    async def _save_file(self, file_data: FileData, file_path: Path) -> Path:
        """Save base64 encoded file to disk."""
        content = base64.b64decode(file_data.content)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        return file_path
    
    async def _read_file_as_base64(self, file_path: str) -> str:
        """Read file and encode as base64."""
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        
        return base64.b64encode(content).decode('utf-8')


# CLI entry point
async def run_service():
    """Run the report service."""
    service = ReportService()
    await service.start()


if __name__ == "__main__":
    asyncio.run(run_service())