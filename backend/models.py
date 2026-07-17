"""
OpsMind AI - SQLAlchemy ORM Models
===================================
These models match the actual Supabase PostgreSQL schema defined in database/schema.sql.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime,
    Numeric, Text, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from database import Base


class Product(Base):
    """Master product catalog (products table)."""
    __tablename__ = "products"

    id            = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku           = Column(String(100), unique=True, nullable=False)
    name          = Column(String(255), nullable=False)
    category      = Column(String(100), nullable=False)
    unit_price    = Column(Numeric(10, 2), nullable=False)
    reorder_level = Column(Integer, nullable=False, default=10)
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inventory     = relationship("Inventory", back_populates="product", uselist=False)
    transactions  = relationship("Transaction", back_populates="product")
    forecasts     = relationship("Forecast", back_populates="product")

    def __repr__(self):
        return f"<Product sku={self.sku} name={self.name}>"


class Inventory(Base):
    """Real-time stock quantities (inventory table)."""
    __tablename__ = "inventory"

    id              = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id      = Column(PG_UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False)
    stock_on_hand   = Column(Integer, nullable=False, default=0)
    allocated_stock = Column(Integer, nullable=False, default=0)
    reserved_stock  = Column(Integer, nullable=False, default=0)
    updated_at      = Column(DateTime, default=datetime.utcnow)

    # Relationship
    product         = relationship("Product", back_populates="inventory")

    def __repr__(self):
        return f"<Inventory product_id={self.product_id} stock={self.stock_on_hand}>"


class Transaction(Base):
    """Immutable stock movement ledger (transactions table)."""
    __tablename__ = "transactions"

    id               = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id       = Column(PG_UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity         = Column(Integer, nullable=False)
    transaction_type = Column(String(20), nullable=False)
    reference_note   = Column(Text, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    # Relationship
    product          = relationship("Product", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction type={self.transaction_type} qty={self.quantity}>"


class Forecast(Base):
    """ML forecast results (forecasts table)."""
    __tablename__ = "forecasts"

    id                = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id        = Column(PG_UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    forecast_date     = Column(Date, nullable=False)
    forecast_quantity = Column(Numeric(12, 2), nullable=False)
    confidence_lower  = Column(Numeric(12, 2), nullable=False)
    confidence_upper  = Column(Numeric(12, 2), nullable=False)
    model_engine      = Column(String(50), nullable=False)
    created_at        = Column(DateTime, default=datetime.utcnow)

    # Relationship
    product           = relationship("Product", back_populates="forecasts")

    def __repr__(self):
        return f"<Forecast product_id={self.product_id} date={self.forecast_date}>"


class Prediction(Base):
    """Flat ML prediction cache (prediction table)."""
    __tablename__ = "prediction"

    id              = Column(Integer, primary_key=True, index=True)
    product_name    = Column(String, nullable=False)
    predicted_stock = Column(Float, nullable=False)
    risk_level      = Column(String, nullable=False)  # "Safe Stock" or "Low Stock Risk"
    created_at      = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Prediction product={self.product_name} risk={self.risk_level}>"


class DecisionLog(Base):
    """AI decision recommendations (decision_log table)."""
    __tablename__ = "decision_log"

    id             = Column(Integer, primary_key=True, index=True)
    recommendation = Column(String, nullable=False)
    status         = Column(String, default="pending")
    created_at     = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DecisionLog id={self.id} status={self.status}>"
