#!/usr/bin/env python3
"""Initialize the database schema"""

import sys
sys.path.insert(0, '/home/ubuntu/Desktop/Assignment')

from src.database import init_db
from src.logger import get_logger

logger = get_logger(__name__)


if __name__ == "__main__":
    try:
        init_db()
        logger.info("Database initialization completed successfully")
        print("✓ Database initialized successfully")
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        print(f"✗ Database initialization failed: {e}")
        sys.exit(1)
