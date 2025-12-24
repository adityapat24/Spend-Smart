"""Database models and connection management."""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from config import settings

Base = declarative_base()


class Transaction(Base):
    """Transaction model for storing bank transactions."""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)  # Plaid transaction ID
    account_id = Column(String, index=True)
    amount = Column(Float)
    date = Column(DateTime)
    name = Column(String)
    merchant_name = Column(String, nullable=True)
    category = Column(String, index=True)  # AI-categorized category
    category_confidence = Column(Float, nullable=True)  # Confidence score from AI
    primary_category = Column(String, index=True)  # Main category (e.g., Food, Transport)
    subcategory = Column(String, nullable=True)  # Subcategory (e.g., Groceries, Restaurants)
    description = Column(Text, nullable=True)
    is_pending = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    synced_to_sheets = Column(Boolean, default=False)


class Category(Base):
    """Category model for storing spending categories."""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic models for API validation
class TransactionCreate(BaseModel):
    """Pydantic model for creating transactions."""
    transaction_id: str
    account_id: str
    amount: float
    date: datetime
    name: str
    merchant_name: Optional[str] = None
    description: Optional[str] = None
    is_pending: bool = False


class TransactionResponse(BaseModel):
    """Pydantic model for transaction responses."""
    id: int
    transaction_id: str
    account_id: str
    amount: float
    date: datetime
    name: str
    merchant_name: Optional[str]
    category: Optional[str]
    category_confidence: Optional[float]
    primary_category: Optional[str]
    subcategory: Optional[str]
    description: Optional[str]
    is_pending: bool
    synced_to_sheets: bool
    
    class Config:
        from_attributes = True


# Database connection
engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

