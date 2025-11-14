"""
RabbitMQ configuration and service
"""
import pika
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.username = os.getenv('RABBITMQ_DEFAULT_USER', 'rabbitmq')
        self.password = os.getenv('RABBITMQ_DEFAULT_PASS', 'rabbitmq')
        self.virtual_host = os.getenv('RABBITMQ_VHOST', '/lengkeng')
        
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare the exchanges and queues
            self._setup_queues()
            
            logger.info("Successfully connected to RabbitMQ")
            return True
            
        except pika.exceptions.ProbableAuthenticationError as e:
            logger.error(f"RabbitMQ authentication failed - invalid credentials: {str(e)}")
            logger.error("Check RABBITMQ_USERNAME and RABBITMQ_PASSWORD environment variables")
            return False
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ server: {str(e)}")
            logger.error(f"Check if RabbitMQ is running on {self.host}:{self.port}")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            return False
    
    def _setup_queues(self):
        """Setup exchanges and queues"""
        # Declare exchange for file upload events
        self.channel.exchange_declare(
            exchange='file_upload_events',
            exchange_type='topic',
            durable=True
        )
        
        # Declare queue for file upload notifications
        self.channel.queue_declare(
            queue='file_upload_notifications',
            durable=True
        )
        
        # Bind queue to exchange
        self.channel.queue_bind(
            exchange='file_upload_events',
            queue='file_upload_notifications',
            routing_key='file.uploaded'
        )
    
    def publish_file_upload_message(self, upload_paths: list, template_path: str, user_id: Optional[int] = None):
        """
        Publish file upload completion message to RabbitMQ
        
        Args:
            upload_paths: List of uploaded file paths
            template_path: Path to the template file
            user_id: ID of the user who uploaded the files
        """
        if not self.connection or self.connection.is_closed:
            if not self.connect():
                logger.error("Cannot publish message: RabbitMQ connection failed")
                return False
        
        try:
            message = {
                "event_type": "file_uploaded",
                "upload_path_files": upload_paths,
                "template_path_file": template_path,
                "user_id": user_id,
                "timestamp": str(datetime.now().isoformat())
            }
            
            self.channel.basic_publish(
                exchange='file_upload_events',
                routing_key='file.uploaded',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published file upload message: {len(upload_paths)} files, template: {template_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish message to RabbitMQ: {str(e)}")
            return False
    
    def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {str(e)}")

# Global RabbitMQ service instance
rabbitmq_service = RabbitMQService()

def get_rabbitmq_service() -> RabbitMQService:
    """Get RabbitMQ service instance"""
    return rabbitmq_service
