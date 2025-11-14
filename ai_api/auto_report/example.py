"""
Example usage of the auto report system with RabbitMQ.
"""
import asyncio
import os
from pathlib import Path

from .messaging import ReportService, RabbitMQConfig
from .client import ReportClient


async def example_service():
    """Example of running the report service."""
    # Configure RabbitMQ (use environment variables in production)
    config = RabbitMQConfig(
        host="localhost",
        port=5672,
        username="guest",
        password="guest",
        request_queue="report_requests",
        response_queue="report_responses"
    )
    
    # Start the service
    service = ReportService(config)
    await service.start()


async def example_client():
    """Example of using the report client."""
    # Configure RabbitMQ connection
    config = RabbitMQConfig(
        host="localhost",
        port=5672,
        username="guest",
        password="guest",
        request_queue="report_requests",
        response_queue="report_responses"
    )
    
    client = ReportClient(config)
    
    try:
        # Connect to RabbitMQ
        await client.connect()
        
        # Example file paths (update these to your actual files)
        template_path = "data/template/your-template.xlsx"
        pdf_paths = [
            "data/input/document1.pdf",
            "data/input/document2.pdf"
        ]
        
        # Check if files exist before processing
        if not os.path.exists(template_path):
            print(f"Template file not found: {template_path}")
            return
        
        missing_pdfs = [p for p in pdf_paths if not os.path.exists(p)]
        if missing_pdfs:
            print(f"PDF files not found: {missing_pdfs}")
            return
        
        # Process the report
        print("Sending report request...")
        success = await client.process_request(
            template_path=template_path,
            pdf_paths=pdf_paths,
            output_path="generated_report.xlsx",
            timeout_seconds=300  # 5 minutes
        )
        
        if success:
            print("Report generated successfully!")
        else:
            print("Report generation failed.")
            
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        await client.disconnect()


async def example_direct_processing():
    """Example of direct processing (without RabbitMQ)."""
    from .main import main
    
    # Example file paths
    template_path = "data/template/your-template.xlsx"
    pdf_paths = [
        "data/input/document1.pdf",
        "data/input/document2.pdf"
    ]
    
    try:
        # Process directly
        output_path = await main(
            template_path=template_path,
            document_path=pdf_paths,
            max_workers=4
        )
        
        print(f"Report generated directly: {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")


def environment_setup_example():
    """Example of setting up environment variables."""
    print("Set these environment variables for RabbitMQ:")
    print("export RABBITMQ_HOST=localhost")
    print("export RABBITMQ_PORT=5672")
    print("export RABBITMQ_USERNAME=guest")
    print("export RABBITMQ_PASSWORD=guest")
    print("export RABBITMQ_REQUEST_QUEUE=report_requests")
    print("export RABBITMQ_RESPONSE_QUEUE=report_responses")
    print()
    print("Set these environment variables for Azure:")
    print("export AZURE_SEARCH_API_KEY=your_api_key")
    print("export AZURE_SEARCH_ENDPOINT=https://your-service.search.windows.net")
    print()
    print("Optional configuration:")
    print("export MAX_WORKERS=4")
    print("export OUTPUT_TEMPLATE_DIRS=./output")


if __name__ == "__main__":
    print("Auto Report System Examples")
    print("=" * 40)
    print()
    
    print("1. Environment Setup:")
    environment_setup_example()
    print()
    
    print("2. To run the service:")
    print("python -m auto_report.example service")
    print("or")
    print("auto-report serve")
    print()
    
    print("3. To process a report via RabbitMQ:")
    print("python -m auto_report.example client")
    print("or")
    print("auto-report process template.xlsx file1.pdf file2.pdf")
    print()
    
    print("4. To process directly (no RabbitMQ):")
    print("python -m auto_report.example direct")
    print("or")
    print("auto-report direct template.xlsx file1.pdf file2.pdf")
    
    # Run based on command line argument
    import sys
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "service":
            asyncio.run(example_service())
        elif mode == "client":
            asyncio.run(example_client())
        elif mode == "direct":
            asyncio.run(example_direct_processing())
        else:
            print(f"Unknown mode: {mode}")