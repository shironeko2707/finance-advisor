#!/usr/bin/env python3
"""
Main entrypoint for the KL Report Agent microservices.

This orchestrates the startup and shutdown of all microservices including:
- RabbitMQ Consumer for document indexing and report generation
- Publisher for sending messages
- Document processing pipeline
"""

import asyncio
import signal
import sys
from typing import List, Optional

from loguru import logger
from auto_report.messaging.consumer import Consumer
from auto_report.messaging.publisher import Publisher
from auto_report.messaging.client import RabbitMQClient


class ServiceOrchestrator:
    """Orchestrates the startup and shutdown of all microservices."""

    def __init__(self):
        self.consumer: Optional[Consumer] = None
        self.publisher: Optional[Publisher] = None
        self.running = False
        self._tasks: List[asyncio.Task] = []

    async def setup_services(self):
        """Initialize and setup all services."""
        logger.info("Setting up services...")

        # Initialize consumer and publisher
        self.consumer = Consumer()
        self.publisher = Publisher()

        # Connect and setup RabbitMQ infrastructure
        await self.consumer.client.connect()
        await self.publisher.client.connect()

        # Setup exchanges, queues, and bindings
        await self.consumer.setup()
        await self.publisher.setup()

        logger.info("All services setup completed successfully.")

    async def start_services(self):
        """Start all microservices."""
        logger.info("Starting all microservices...")
        self.running = True

        # Start consumer in background task
        if self.consumer:
            consumer_task = asyncio.create_task(self._run_consumer())
            self._tasks.append(consumer_task)
            logger.info("Consumer service started")

        logger.info("All microservices started successfully")

    async def _run_consumer(self):
        """Run the consumer service."""
        try:
            await self.consumer.start_consuming()
        except Exception as e:
            logger.error(f"Consumer service error: {e}")
            self.running = False

    async def stop_services(self):
        """Stop all microservices gracefully."""
        logger.info("Stopping all microservices...")
        self.running = False

        # Cancel all running tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        self._tasks.clear()

        # Close connections
        if self.consumer and self.consumer.client:
            await self.consumer.client.close()
        if self.publisher and self.publisher.client:
            await self.publisher.client.close()

        logger.info("All microservices stopped successfully")

    async def run(self):
        """Main run loop for all services."""
        try:
            await self.setup_services()
            await self.start_services()

            # Keep running until interrupted
            while self.running:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            await self.stop_services()


async def main():
    """Main function to run the service orchestrator."""
    orchestrator = ServiceOrchestrator()

    # Setup signal handlers for graceful shutdown
    def signal_handler():
        logger.info("Received shutdown signal")
        orchestrator.running = False

    # Register signal handlers
    if sys.platform != "win32":
        for sig in (signal.SIGTERM, signal.SIGINT):
            asyncio.get_event_loop().add_signal_handler(sig, signal_handler)

    await orchestrator.run()


if __name__ == "__main__":
    logger.info("Starting KL Report Agent microservices...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)
    finally:
        logger.info("Application shutdown complete")