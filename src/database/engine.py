"""
Database Engine Module - AI Stock Agent

Configures SQLAlchemy database connection for SQLite.
Database file is stored in the data/ directory.

Author: AI Stock Agent Team
Version: 1.0
Last Updated: 2026-07-08
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database path: data/market.db (relative to project root)
DATABASE_URL = "sqlite:///./data/market.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
