"""
Database Connection Tests
Verifies PostgreSQL connection and basic health
"""

import sys
import os

# ✅ FIX: Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.database import engine


def test_database_connection():
    """Test basic database connectivity"""
    try:
        with engine.connect() as connection:
            # Test basic query
            result = connection.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
            
            # Get PostgreSQL version
            version_result = connection.execute(text("SELECT version()"))
            version = version_result.fetchone()[0]
            
        print("✅ Database connection successful!")
        print(f"PostgreSQL version: {version.split(',')[0]}")
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        raise


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Running Database Connection Tests")
    print("="*70 + "\n")
    
    test_database_connection()
    
    print("\n" + "="*70)
    print("✅ Database tests passed!")
    print("="*70)
