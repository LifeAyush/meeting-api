import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.base import Base


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./meetings.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Yield a SQLAlchemy session for dependency injection in FastAPI routes."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all database tables based on the SQLAlchemy models."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")
