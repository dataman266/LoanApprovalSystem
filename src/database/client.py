from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.config import get_settings
from src.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Create engine
connect_args = {}
if "sqlite" in settings.database_url:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args=connect_args,
    pool_pre_ping=True if "mysql" in settings.database_url else False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from src.models.database import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")
