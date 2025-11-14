"""
Client utilities for testing RabbitMQ integration.
"""
import os
import json
import asyncio
import base64
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from aio_pika import connect_robust, Message, DeliveryMode
from aio_pika.abc import AbstractRobustConnection, AbstractChannel, AbstractQueue
from loguru import logger

from .messaging import ReportRequest, ReportResponse, FileData, RabbitMQConfig


class ReportClient:
    """Client for sending report requests and receiving responses."""
    
    def __init__(self, config: Optional[RabbitMQConfig] = None):
        self.config = config or RabbitMQConfig.from_env()
        self.connection: Optional[AbstractRobustConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.request_queue: Optional[AbstractQueue] = None
        self.response_queue: Optional[AbstractQueue] = None
        
    async def connect(self) -> None:
        """Connect to RabbitMQ."""
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
            
            logger.info(f"Client connected to RabbitMQ at {self.config.host}:{self.config.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Client disconnected from RabbitMQ")
    
    async def send_request(
        self, 
        template_path: str, 
        pdf_paths: List[str],
        request_id: Optional[str] = None
    ) -> str:
        """
        Send a report generation request.
        
        Args:
            template_path: Path to Excel template file
            pdf_paths: List of paths to PDF files
            request_id: Optional custom request ID
            
        Returns:
            Request ID for tracking
        """
        if not self.channel or not self.request_queue:
            raise RuntimeError("Client not connected to RabbitMQ")
        
        # Generate request ID if not provided
        if request_id is None:
            request_id = str(uuid.uuid4())
        
        # Read template file
        template_file = await self._read_file_as_file_data(template_path)
        
        # Read PDF files
        pdf_files = []
        for pdf_path in pdf_paths:
            pdf_file = await self._read_file_as_file_data(pdf_path)
            pdf_files.append(pdf_file)
        
        # Create request
        request = ReportRequest(
            request_id=request_id,
            template_file=template_file,
            pdf_files=pdf_files
        )
        
        # Send message
        message_body = request.model_dump_json().encode()
        message = Message(
            message_body,
            delivery_mode=DeliveryMode.PERSISTENT
        )
        
        await self.channel.default_exchange.publish(
            message, routing_key=self.config.request_queue
        )
        
        logger.info(f"Sent request {request_id} with {len(pdf_files)} PDF files")
        return request_id
    
    async def wait_for_response(
        self, 
        request_id: str, 
        timeout_seconds: float = 300.0
    ) -> Optional[ReportResponse]:
        """
        Wait for a response to a specific request.
        
        Args:
            request_id: The request ID to wait for
            timeout_seconds: Maximum time to wait
            
        Returns:
            ReportResponse if received, None if timeout
        """
        if not self.response_queue:
            raise RuntimeError("Client not connected to RabbitMQ")
        
        logger.info(f"Waiting for response to request {request_id} (timeout: {timeout_seconds}s)")
        
        async def check_message(message) -> Optional[ReportResponse]:
            async with message.process():
                try:
                    response_data = json.loads(message.body.decode())
                    response = ReportResponse(**response_data)
                    
                    if response.request_id == request_id:
                        return response
                    else:
                        # Requeue message for other consumers
                        await message.reject(requeue=True)
                        return None
                        
                except Exception as e:
                    logger.error(f"Error parsing response message: {e}")
                    return None
        
        # Consume messages with timeout
        start_time = datetime.now()
        async for message in self.response_queue:
            response = await check_message(message)
            if response:
                logger.info(f"Received response for request {request_id}")
                return response
            
            # Check timeout
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout_seconds:
                logger.warning(f"Timeout waiting for response to request {request_id}")
                break
        
        return None
    
    async def process_request(
        self,
        template_path: str,
        pdf_paths: List[str],
        output_path: Optional[str] = None,
        timeout_seconds: float = 300.0
    ) -> bool:
        """
        Send request and wait for response, saving result to file.
        
        Args:
            template_path: Path to Excel template file
            pdf_paths: List of paths to PDF files
            output_path: Path to save result (optional)
            timeout_seconds: Maximum time to wait
            
        Returns:
            True if successful, False otherwise
        """
        # Send request
        request_id = await self.send_request(template_path, pdf_paths)
        
        # Wait for response
        response = await self.wait_for_response(request_id, timeout_seconds)
        
        if not response:
            logger.error(f"No response received for request {request_id}")
            return False
        
        if not response.success:
            logger.error(f"Request {request_id} failed: {response.error_message}")
            return False
        
        if not response.result_file:
            logger.error(f"No result file in response for request {request_id}")
            return False
        
        # Save result file
        if output_path is None:
            output_path = f"result_{request_id}.xlsx"
        
        await self._save_file_data(response.result_file, output_path)
        
        logger.info(
            f"Request {request_id} completed successfully in "
            f"{response.processing_time_seconds:.2f}s. Result saved to {output_path}"
        )
        
        return True
    
    async def _read_file_as_file_data(self, file_path: str) -> FileData:
        """Read file and convert to FileData."""
        path = Path(file_path)
        
        with open(path, 'rb') as f:
            content = f.read()
        
        # Determine content type
        if path.suffix.lower() == '.xlsx':
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif path.suffix.lower() == '.pdf':
            content_type = "application/pdf"
        else:
            content_type = "application/octet-stream"
        
        return FileData(
            filename=path.name,
            content=base64.b64encode(content).decode('utf-8'),
            content_type=content_type
        )
    
    async def _save_file_data(self, file_data: FileData, output_path: str) -> None:
        """Save FileData to disk."""
        content = base64.b64decode(file_data.content)
        
        with open(output_path, 'wb') as f:
            f.write(content)


async def test_client():
    """Test the RabbitMQ client."""
    client = ReportClient()
    
    try:
        await client.connect()
        
        # Example usage (update paths as needed)
        template_path = "data/template/240826-UOB Financial Review-Input.xlsx"
        pdf_paths = ["data/input/UOB - condensed-financial-statement-4q-2024-results 1.pdf"]
        
        if os.path.exists(template_path) and all(os.path.exists(p) for p in pdf_paths):
            success = await client.process_request(
                template_path=template_path,
                pdf_paths=pdf_paths,
                output_path="test_output.xlsx"
            )
            
            print(f"Test {'passed' if success else 'failed'}")
        else:
            print("Test files not found, skipping test")
            
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_client())