"""
Database utilities
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import structlog

logger = structlog.get_logger()

# Database engine (se inicializa en init_db)
engine = None
SessionLocal = None
Base = declarative_base()


async def init_db(database_url: str):
    """
    Initialize database connection
    """
    global engine, SessionLocal
    
    try:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        logger.info("database_connected", url=database_url.split("@")[-1])
        
    except Exception as e:
        logger.error("database_connection_failed", error=str(e))
        # No lanzar excepción, permitir que la app arranque sin DB
        # (útil para testing con datos en memoria)


async def close_db():
    """
    Close database connection
    """
    global engine
    
    if engine:
        engine.dispose()
        logger.info("database_disconnected")


def get_db():
    """
    Get database session
    """
    if SessionLocal is None:
        return None
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
