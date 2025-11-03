"""
Database Configuration and Connection Management
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConfig:
    """
    Manages database connection
    """

    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConfig, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize database connection"""
        database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:@localhost:5432/interview_db')

        # Create engine
        self._engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )

        # Create session factory
        self._session_factory = scoped_session(
            sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False
            )
        )

        print("✅ Database connection established!")

    @property
    def engine(self):
        return self._engine

    @property
    def session_factory(self):
        return self._session_factory

    def get_session(self):
        """Get a new database session"""
        return self._session_factory()

    def close_session(self, session):
        """Close a database session"""
        session.close()

    def create_all_tables(self):
        """Create all tables"""
        from models.database_models import Base
        Base.metadata.create_all(self._engine)
        print("✅ All tables created successfully!")


class DatabaseSession:
    """
    Context manager for database sessions
    """

    def __init__(self):
        self.db = DatabaseConfig()
        self.session = None

    def __enter__(self):
        self.session = self.db.get_session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                self.session.rollback()
                print(f"❌ Transaction rolled back: {exc_val}")
            else:
                self.session.commit()
        finally:
            self.session.close()
        return False


def test_connection():
    """Test database connection"""
    try:
        db = DatabaseConfig()
        session = db.get_session()
        result = session.execute(text("SELECT 1"))
        session.close()
        print("✅ Database connection test successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing database connection...")
    test_connection()

    print("\nCreating tables...")
    db = DatabaseConfig()
    db.create_all_tables()


# Export Base and engine for external use
from models.database_models import Base

# Get singleton instance to ensure initialization
_db_instance = DatabaseConfig()
engine = _db_instance.engine
