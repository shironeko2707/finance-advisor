"""
Command line interface for the auto report system.
"""
import asyncio
import sys
from pathlib import Path

import click
from loguru import logger

from .messaging import ReportService, RabbitMQConfig
from .client import ReportClient


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose: bool):
    """Auto Report System CLI."""
    if verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")


@cli.command()
@click.option('--host', default='localhost', help='RabbitMQ host')
@click.option('--port', default=5672, help='RabbitMQ port')
@click.option('--username', default='guest', help='RabbitMQ username')
@click.option('--password', default='guest', help='RabbitMQ password')
@click.option('--request-queue', default='report_requests', help='Request queue name')
@click.option('--response-queue', default='report_responses', help='Response queue name')
def serve(host: str, port: int, username: str, password: str, request_queue: str, response_queue: str):
    """Start the report service."""
    config = RabbitMQConfig(
        host=host,
        port=port,
        username=username,
        password=password,
        request_queue=request_queue,
        response_queue=response_queue
    )
    
    service = ReportService(config)
    
    logger.info(f"Starting report service with RabbitMQ at {host}:{port}")
    logger.info(f"Request queue: {request_queue}")
    logger.info(f"Response queue: {response_queue}")
    
    try:
        asyncio.run(service.start())
    except KeyboardInterrupt:
        logger.info("Service stopped by user")


@cli.command()
@click.argument('template_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('pdf_paths', nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.option('--output', '-o', help='Output file path')
@click.option('--host', default='localhost', help='RabbitMQ host')
@click.option('--port', default=5672, help='RabbitMQ port')
@click.option('--username', default='guest', help='RabbitMQ username')
@click.option('--password', default='guest', help='RabbitMQ password')
@click.option('--request-queue', default='report_requests', help='Request queue name')
@click.option('--response-queue', default='report_responses', help='Response queue name')
@click.option('--timeout', default=300, help='Timeout in seconds')
def process(
    template_path: str, 
    pdf_paths: tuple, 
    output: str,
    host: str, 
    port: int, 
    username: str, 
    password: str,
    request_queue: str,
    response_queue: str,
    timeout: int
):
    """Process a report via RabbitMQ."""
    if not pdf_paths:
        click.echo("Error: At least one PDF file is required", err=True)
        sys.exit(1)
    
    config = RabbitMQConfig(
        host=host,
        port=port,
        username=username,
        password=password,
        request_queue=request_queue,
        response_queue=response_queue
    )
    
    async def run_client():
        client = ReportClient(config)
        
        try:
            await client.connect()
            
            if not output:
                output_path = f"result_{Path(template_path).stem}.xlsx"
            else:
                output_path = output
            
            logger.info(f"Processing report with template: {template_path}")
            logger.info(f"PDF files: {', '.join(pdf_paths)}")
            logger.info(f"Output: {output_path}")
            
            success = await client.process_request(
                template_path=template_path,
                pdf_paths=list(pdf_paths),
                output_path=output_path,
                timeout_seconds=float(timeout)
            )
            
            if success:
                click.echo(f"Report generated successfully: {output_path}")
                sys.exit(0)
            else:
                click.echo("Report generation failed", err=True)
                sys.exit(1)
                
        finally:
            await client.disconnect()
    
    asyncio.run(run_client())


@cli.command()
@click.argument('template_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('pdf_paths', nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.option('--output', '-o', help='Output file path')
@click.option('--max-workers', default=4, help='Maximum concurrent workers')
def direct(template_path: str, pdf_paths: tuple, output: str, max_workers: int):
    """Process a report directly (bypass RabbitMQ)."""
    if not pdf_paths:
        click.echo("Error: At least one PDF file is required", err=True)
        sys.exit(1)
    
    from .main import main as process_main
    
    async def run_direct():
        try:
            if not output:
                output_path = await process_main(
                    template_path=template_path,
                    document_path=list(pdf_paths),
                    max_workers=max_workers
                )
            else:
                # Update output directory temporarily
                import os
                from .main import OUTPUT_TEMPLATE_DIRS
                
                old_output_dir = OUTPUT_TEMPLATE_DIRS
                os.environ["OUTPUT_TEMPLATE_DIRS"] = str(Path(output).parent)
                
                try:
                    output_path = await process_main(
                        template_path=template_path,
                        document_path=list(pdf_paths),
                        max_workers=max_workers
                    )
                finally:
                    os.environ["OUTPUT_TEMPLATE_DIRS"] = old_output_dir
            
            click.echo(f"Report generated successfully: {output_path}")
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(run_direct())


if __name__ == "__main__":
    cli()