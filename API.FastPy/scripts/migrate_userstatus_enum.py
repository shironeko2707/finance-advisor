#!/usr/bin/env python3
"""
Migration script to update userstatus enum from DEACTIVE to INACTIVE
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env.local
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(dotenv_path=env_path)

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_userstatus_enum():
    """
    Migrate the userstatus enum from DEACTIVE to INACTIVE
    """
    try:
        logger.info("Starting userstatus enum migration...")

        # Check if we're using PostgreSQL
        if 'postgresql' in str(engine.url):
            logger.info("PostgreSQL detected, updating enum values...")

            # First transaction: Add the new INACTIVE value to the enum
            logger.info("Adding INACTIVE value to userstatus enum...")
            try:
                with engine.begin() as conn:
                    conn.execute(text("""
                        ALTER TYPE userstatus ADD VALUE 'INACTIVE'
                    """))
                    logger.info("Successfully added INACTIVE value to enum")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("INACTIVE value already exists in enum")
                else:
                    logger.warning(f"Could not add INACTIVE to enum: {str(e)}")

            # Second transaction: Update existing records
            logger.info("Updating existing DEACTIVE values to INACTIVE...")
            with engine.begin() as conn:
                result = conn.execute(text("""
                    UPDATE users 
                    SET status = 'INACTIVE' 
                    WHERE status = 'DEACTIVE'
                """))
                logger.info(f"Updated {result.rowcount} rows")

            # Note: PostgreSQL doesn't support removing enum values directly
            # We would need to recreate the enum type to remove DEACTIVE
            # For now, we'll leave both values in the enum but update all data to use INACTIVE

            logger.info("Migration completed successfully!")

        else:
            # SQLite handling
            logger.info("SQLite detected, no enum migration needed")
            logger.info("SQLite uses CHECK constraints, updating any DEACTIVE values...")

            with engine.begin() as conn:
                result = conn.execute(text("""
                    UPDATE users 
                    SET status = 'INACTIVE' 
                    WHERE status = 'DEACTIVE'
                """))
                logger.info(f"Updated {result.rowcount} rows")

    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise

def recreate_userstatus_enum():
    """
    Recreate the userstatus enum with only ACTIVE and INACTIVE values (PostgreSQL only)
    This is a more complete solution but requires careful handling
    """
    try:
        with engine.begin() as conn:
            if 'postgresql' not in str(engine.url):
                logger.info("This function is only for PostgreSQL")
                return

            logger.info("Recreating userstatus enum with clean values...")

            # Create a temporary enum
            conn.execute(text("""
                CREATE TYPE userstatus_new AS ENUM ('Active', 'Inactive')
            """))

            # Update the column to use the new enum
            conn.execute(text("""
                ALTER TABLE users 
                ALTER COLUMN status TYPE userstatus_new 
                USING status::text::userstatus_new
            """))

            # Drop the old enum and rename the new one
            conn.execute(text("""
                DROP TYPE userstatus
            """))

            conn.execute(text("""
                ALTER TYPE userstatus_new RENAME TO userstatus
            """))

            logger.info("Successfully recreated userstatus enum!")

    except Exception as e:
        logger.error(f"Error recreating enum: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting userstatus enum migration...")

    try:
        # First, try the simple migration
        migrate_userstatus_enum()

        # Ask user if they want to clean up the enum completely
        response = input("\nDo you want to recreate the enum to remove DEACTIVE completely? (y/n): ")
        if response.lower() == 'y':
            recreate_userstatus_enum()

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)

    logger.info("Migration completed successfully!")
