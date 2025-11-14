#!/usr/bin/env python3
"""
Test runner script for Lengkeng API
Sets up test environment and runs all tests
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_test_environment():
    """Set up environment variables for testing"""
    logger.info("Setting up test environment...")

    # Set IS_PRODUCTION to false for testing
    os.environ['IS_PRODUCTION'] = 'false'

    # Set other test-specific environment variables
    os.environ['DATABASE_URL'] = 'sqlite:///./storage/test_lengkeng.db'
    os.environ['JWT_SECRET_KEY'] = 'test-secret-key-for-testing-only'
    os.environ['DEBUG'] = 'true'
    os.environ['LOG_LEVEL'] = 'DEBUG'

    # Ensure test storage directories exist
    test_dirs = [
        'storage',
        'storage/uploads',
        'storage/templates',
        'storage/generated',
        'storage/exports',
        'storage/logs',
        'storage/cache'
    ]

    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    logger.info("Test environment configured successfully")
    logger.info(f"IS_PRODUCTION = {os.getenv('IS_PRODUCTION')}")
    logger.info(f"DATABASE_URL = {os.getenv('DATABASE_URL')}")

def run_tests():
    """Run pytest with appropriate configuration"""
    logger.info("Starting test execution...")

    try:
        # Run pytest with verbose output
        cmd = [
            sys.executable, '-m', 'pytest',
            'tests/',
            '-v',
            '--tb=short',
            '--strict-markers',
            '--disable-warnings'
        ]

        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=False)

        if result.returncode == 0:
            logger.info("All tests passed successfully!")
        else:
            logger.error(f"Tests failed with return code: {result.returncode}")

        return result.returncode

    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
        return 1

def cleanup_test_environment():
    """Clean up test artifacts"""
    logger.info("Cleaning up test environment...")

    # Remove test database if it exists
    test_db_path = Path('storage/test_lengkeng.db')
    if test_db_path.exists():
        test_db_path.unlink()
        logger.info("Test database removed")

    logger.info("Cleanup completed")

def main():
    """Main test runner function"""
    logger.info("=== Lengkeng API Test Runner ===")

    try:
        # Setup test environment
        setup_test_environment()

        # Run tests
        exit_code = run_tests()

        # Cleanup
        cleanup_test_environment()

        # Exit with the same code as pytest
        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.warning("Test execution interrupted by user")
        cleanup_test_environment()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        cleanup_test_environment()
        sys.exit(1)

if __name__ == "__main__":
    main()
