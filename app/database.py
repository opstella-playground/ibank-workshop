"""Database configuration and session management."""

from collections.abc import Generator
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

settings = get_settings()

# Ensure data directory exists for SQLite
if settings.database_url.startswith("sqlite"):
    db_path = settings.database_url.replace("sqlite:///", "")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

# SQLite requires check_same_thread=False for FastAPI
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.debug,
)


def create_db_and_tables() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session dependency."""
    with Session(engine) as session:
        yield session


# Type alias for session dependency injection
SessionDep = Annotated[Session, Depends(get_session)]
