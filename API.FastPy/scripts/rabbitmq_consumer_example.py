"""
Example RabbitMQ message consumer for file upload notifications
"""
import pika
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileUploadMessageConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.username = os.getenv('RABBITMQ_DEFAULT_USERNAME', 'guest')
        self.password = os.getenv('RABBITMQ_DEFAULT_PASSWORD', 'guest')
        self.virtual_host = os.getenv('RABBITMQ_VHOST', '/')
        
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
            
            # Ensure the queue exists
            self.channel.queue_declare(
                queue='file_upload_notifications',
                durable=True
            )
            
            logger.info("Connected to RabbitMQ successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            return False
    
    def process_file_upload_message(self, ch, method, properties, body):
        """
        Process file upload notification message
        """
        try:
            # Parse message
            message = json.loads(body)
            
            logger.info("Received file upload notification:")
            logger.info(f"  Event Type: {message.get('event_type')}")
            logger.info(f"  User ID: {message.get('user_id')}")
            logger.info(f"  Timestamp: {message.get('timestamp')}")
            logger.info(f"  Uploaded Files: {len(message.get('upload_path_files', []))}")
            
            for i, file_path in enumerate(message.get('upload_path_files', []), 1):
                logger.info(f"    {i}. {file_path}")
            
            template_path = message.get('template_path_file', '')
            if template_path:
                logger.info(f"  Template File: {template_path}")
            else:
                logger.info("  Template File: None")
            
            # Here you can add your business logic to process the files
            # For example:
            # - Start document processing workflow
            # - Send notification to user
            # - Update processing status in database
            # - Trigger ML/AI processing pipeline
            
            # Example processing logic
            self.process_uploaded_files(
                upload_paths=message.get('upload_path_files', []),
                template_path=template_path,
                user_id=message.get('user_id')
            )
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("Message processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Reject message and requeue for retry
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def process_uploaded_files(self, upload_paths, template_path, user_id):
        """
        Business logic to process uploaded files
        """
        logger.info(f"Processing {len(upload_paths)} files for user {user_id}")
        
        # Example processing steps:
        if template_path:
            logger.info("Template-based processing:")
            logger.info(f"  Loading template: {template_path}")
            # Load and parse template file
            # Apply template to each uploaded file
            # Generate processed output
        else:
            logger.info("Standard file processing:")
            # Process files individually
            # Extract data, analyze, etc.
        
        for file_path in upload_paths:
            logger.info(f"  Processing file: {file_path}")
            # Your file processing logic here
            # Example: extract text, analyze data, generate reports, etc.
        
        logger.info("File processing completed")
    
    def start_consuming(self):
        """
        Start consuming messages from the queue
        """
        if not self.connect():
            logger.error("Cannot start consuming: connection failed")
            return
        
        # Set up message consumption
        self.channel.basic_qos(prefetch_count=1)  # Process one message at a time
        self.channel.basic_consume(
            queue='file_upload_notifications',
            on_message_callback=self.process_file_upload_message
        )
        
        logger.info("Starting message consumption. Press CTRL+C to stop...")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping message consumption...")
            self.channel.stop_consuming()
            self.connection.close()
            logger.info("Consumer stopped")

def main():
    """
    Main function to run the consumer
    """
    consumer = FileUploadMessageConsumer()
    consumer.start_consuming()

if __name__ == "__main__":
    main()
