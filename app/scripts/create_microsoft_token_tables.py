"""
Create Microsoft OAuth Token Tables

This script creates the Microsoft OAuth token tables directly using SQLAlchemy.
Run this if Alembic migrations are not being used.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import Base, engine
from app.models.integration.microsoft_token import MicrosoftOAuthToken, BetaMicrosoftOAuthToken
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create Microsoft OAuth token tables."""
    try:
        logger.info("Creating Microsoft OAuth token tables...")
        
        # Create tables
        MicrosoftOAuthToken.__table__.create(engine, checkfirst=True)
        BetaMicrosoftOAuthToken.__table__.create(engine, checkfirst=True)
        
        logger.info("✅ Successfully created microsoft_oauth_tokens table")
        logger.info("✅ Successfully created beta_microsoft_oauth_tokens table")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'microsoft_oauth_tokens' in tables:
            logger.info("✅ Verified: microsoft_oauth_tokens table exists")
        else:
            logger.error("❌ microsoft_oauth_tokens table not found")
            
        if 'beta_microsoft_oauth_tokens' in tables:
            logger.info("✅ Verified: beta_microsoft_oauth_tokens table exists")
        else:
            logger.error("❌ beta_microsoft_oauth_tokens table not found")
            
        logger.info("Microsoft OAuth token tables created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)

