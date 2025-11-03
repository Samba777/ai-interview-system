"""
Setup Cloud Database Tables
Run this once to create tables in Supabase
"""

from config.database import DatabaseConfig, Base, engine

def setup_database():
    """Create all tables in cloud database"""
    try:
        # Import all models
        from models.database_models import User, Interview, Question, Response, Feedback
        
        print("Creating tables in cloud database...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    setup_database()