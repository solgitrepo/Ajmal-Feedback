from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables from .env file if it exists
load_dotenv()
print("Loaded DB_HOST:", os.getenv('DB_HOST'))

def get_database_credentials():
    """Get database credentials from .env file"""
    try:
            return {
                'username': os.getenv('DB_USERNAME'),
                'password': os.getenv('DB_PASSWORD'),
                'host': os.getenv('DB_HOST'),
                'port': os.getenv('DB_PORT'),
                'database': os.getenv('DB_NAME')
        }
    except Exception as e:
        print(f"Error getting database credentials: {str(e)}")
        return None

def init_connection():
    """Initialize database connection"""
    try:
        # Get database credentials
        credentials = get_database_credentials()
        if not credentials:
            raise Exception("Could not get database credentials")
        
        # PostgreSQL connection string
        DATABASE_URL = f"postgresql+psycopg2://{credentials['username']}:{credentials['password']}@{credentials['host']}:{credentials['port']}/{credentials['database']}"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        try:
            conn = engine.connect()
            print("✅ Successfully connected to DB!")
            conn.close()
        except Exception as e:
            print("❌ Connection test failed:", e)

        
        return engine
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return None

def get_db_session():
    """Get a database session"""
    engine = init_connection()
    if engine:
        Session = sessionmaker(bind=engine)
        return Session()
    return None

def init_database_tables():
    """Create tables if they don't exist"""

    engine = init_connection()
    
    if not engine:
        print("Cannot initialize tables: No database connection")
        return False
    
    try:
        Base.metadata.create_all(engine)
        print("Database tables initialized successfully")
        return True
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        return False
