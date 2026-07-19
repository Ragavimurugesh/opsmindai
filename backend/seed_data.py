"""
OpsMind AI - Phase 5: Database Seed Script
==========================================
Populates the Supabase PostgreSQL database with realistic mock data:
  - 5 products in the `products` table
  - 5 inventory rows in the `inventory` table (FK to products)
  - 35 transactions (7 days x 5 products) in the `transactions` table
  - 5 forecast records in the `forecasts` table
  - 5 prediction records in the `prediction` table (flat ORM table)
  - 5 decision log entries in the `decision_log` table

Usage (from project root):
    python backend/seed_data.py
"""

import os
import sys
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

# ── 1. Load .env ──────────────────────────────────────────────────────────────
from dotenv import load_dotenv

_env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=_env_path)

_db_url = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")
if not _db_url:
    print("ERROR: Neither SUPABASE_DB_URL nor DATABASE_URL is set.")
    sys.exit(1)

# SQLAlchemy 1.4+ and 2.0+ require postgresql:// instead of postgres://
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

# ── 2. SQLAlchemy setup ──────────────────────────────────────────────────────
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date, DateTime,
    Numeric, Text, CheckConstraint, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

engine = create_engine(_db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── 3. Models matching the REAL Supabase schema ──────────────────────────────

class Product(Base):
    __tablename__ = "products"
    id            = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku           = Column(String(100), unique=True, nullable=False)
    name          = Column(String(255), nullable=False)
    category      = Column(String(100), nullable=False)
    unit_price    = Column(Numeric(10, 2), nullable=False)
    reorder_level = Column(Integer, nullable=False, default=10)
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow)


class Inventory(Base):
    __tablename__ = "inventory"
    id              = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id      = Column(PG_UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False)
    stock_on_hand   = Column(Integer, nullable=False, default=0)
    allocated_stock = Column(Integer, nullable=False, default=0)
    reserved_stock  = Column(Integer, nullable=False, default=0)
    updated_at      = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"
    id               = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id       = Column(PG_UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity         = Column(Integer, nullable=False)
    transaction_type = Column(String(20), nullable=False)
    reference_note   = Column(Text, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)


class Forecast(Base):
    __tablename__ = "forecasts"
    id                = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id        = Column(PG_UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    forecast_date     = Column(Date, nullable=False)
    forecast_quantity = Column(Numeric(12, 2), nullable=False)
    confidence_lower  = Column(Numeric(12, 2), nullable=False)
    confidence_upper  = Column(Numeric(12, 2), nullable=False)
    model_engine      = Column(String(50), nullable=False)
    created_at        = Column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "prediction"
    id              = Column(Integer, primary_key=True, index=True)
    product_name    = Column(String, nullable=False)
    predicted_stock = Column(Float, nullable=False)
    risk_level      = Column(String, nullable=False)
    created_at      = Column(DateTime, default=datetime.utcnow)


class DecisionLog(Base):
    __tablename__ = "decision_log"
    id             = Column(Integer, primary_key=True, index=True)
    recommendation = Column(String, nullable=False)
    status         = Column(String, default="pending")
    created_at     = Column(DateTime, default=datetime.utcnow)


# ── 4. Seed data definitions ─────────────────────────────────────────────────
TODAY = date.today()

PRODUCTS_DEF = [
    {"sku": "SKU-001", "name": "Rice",        "category": "Grains",      "unit_price": Decimal("2.50"),  "reorder_level": 40, "stock": 200, "daily_sales": 45},
    {"sku": "SKU-002", "name": "Wheat",       "category": "Grains",      "unit_price": Decimal("2.00"),  "reorder_level": 30, "stock": 150, "daily_sales": 38},
    {"sku": "SKU-003", "name": "Cooking Oil", "category": "Oils",        "unit_price": Decimal("5.75"),  "reorder_level": 20, "stock": 50,  "daily_sales": 22},
    {"sku": "SKU-004", "name": "Sugar",       "category": "Sweeteners",  "unit_price": Decimal("1.80"),  "reorder_level": 15, "stock": 30,  "daily_sales": 17},
    {"sku": "SKU-005", "name": "Milk",        "category": "Dairy",       "unit_price": Decimal("3.20"),  "reorder_level": 10, "stock": 18,  "daily_sales": 12},
]

REORDER_THRESHOLD = 25


# ── 5. Build rows ────────────────────────────────────────────────────────────
product_rows = []
inventory_rows = []
transaction_rows = []
forecast_rows = []
prediction_rows = []
decision_rows = []

for pdef in PRODUCTS_DEF:
    pid = uuid.uuid4()

    # products
    product_rows.append(Product(
        id=pid, sku=pdef["sku"], name=pdef["name"],
        category=pdef["category"], unit_price=pdef["unit_price"],
        reorder_level=pdef["reorder_level"],
    ))

    # inventory (current snapshot)
    inventory_rows.append(Inventory(
        product_id=pid,
        stock_on_hand=pdef["stock"],
        allocated_stock=0,
        reserved_stock=0,
    ))

    # transactions (7 days of OUTBOUND sales)
    for day in range(7):
        qty = pdef["daily_sales"] // 7 + (1 if day < pdef["daily_sales"] % 7 else 0)
        transaction_rows.append(Transaction(
            product_id=pid,
            quantity=qty,
            transaction_type="OUTBOUND",
            reference_note=f"Daily sales for {pdef['name']} (Day {day+1})",
            created_at=datetime.combine(TODAY - timedelta(days=6 - day), datetime.min.time()),
        ))

    # forecasts (next 7 days)
    base_demand = pdef["daily_sales"]
    for day in range(1, 8):
        fq = round(base_demand * (1 + 0.03 * day), 2)
        cl = round(fq * 0.85, 2)
        cu = round(fq * 1.15, 2)
        forecast_rows.append(Forecast(
            product_id=pid,
            forecast_date=TODAY + timedelta(days=day),
            forecast_quantity=Decimal(str(fq)),
            confidence_lower=Decimal(str(cl)),
            confidence_upper=Decimal(str(cu)),
            model_engine="XGBoost",
        ))

    # prediction (flat ORM table)
    predicted = round(pdef["stock"] * 0.9, 2)
    risk = "Low Stock Risk" if pdef["stock"] <= REORDER_THRESHOLD else "Safe Stock"
    prediction_rows.append(Prediction(
        product_name=pdef["name"],
        predicted_stock=predicted,
        risk_level=risk,
    ))

    # decision_log
    if pdef["stock"] <= REORDER_THRESHOLD:
        rec = (f"Stock of {pdef['name']} is critically low ({pdef['stock']} units). "
               f"Immediately reorder at least {pdef['daily_sales'] * 2} units to avoid stockout.")
        status = "critical"
    elif pdef["stock"] <= REORDER_THRESHOLD * 2:
        rec = (f"Stock of {pdef['name']} ({pdef['stock']} units) is approaching reorder threshold. "
               f"Consider placing a reorder within the next 3 days.")
        status = "warning"
    else:
        rec = (f"Stock of {pdef['name']} ({pdef['stock']} units) is at a healthy level. "
               f"No immediate action required.")
        status = "healthy"
    decision_rows.append(DecisionLog(recommendation=rec, status=status))


# ── 6. Execute seed ──────────────────────────────────────────────────────────
db = SessionLocal()
try:
    # Clear existing data (order matters for FK constraints)
    print("Clearing existing data...")
    db.query(DecisionLog).delete()
    db.query(Prediction).delete()
    db.query(Forecast).delete()
    db.query(Transaction).delete()
    db.query(Inventory).delete()
    db.query(Product).delete()
    db.commit()
    print("  Cleared all seed tables.\n")

    # Insert in FK order
    db.add_all(product_rows)
    db.flush()  # ensure product IDs are available

    db.add_all(inventory_rows)
    db.add_all(transaction_rows)
    db.add_all(forecast_rows)
    db.add_all(prediction_rows)
    db.add_all(decision_rows)
    db.commit()

    print("=" * 64)
    print("  SEED DATA INSERTED SUCCESSFULLY!")
    print("=" * 64)
    print(f"  products      : {len(product_rows)}")
    print(f"  inventory     : {len(inventory_rows)}")
    print(f"  transactions  : {len(transaction_rows)}")
    print(f"  forecasts     : {len(forecast_rows)}")
    print(f"  predictions   : {len(prediction_rows)}")
    print(f"  decision_log  : {len(decision_rows)}")

    # ── 7. Verification ──────────────────────────────────────────────────────
    print("\n" + "-" * 64)
    print("  PRODUCTS TABLE")
    print("-" * 64)
    print(f"  {'SKU':<10} {'Name':<14} {'Category':<12} {'Price':>8} {'Reorder':>8}")
    print("-" * 64)
    for p in db.query(Product).order_by(Product.sku).all():
        print(f"  {p.sku:<10} {p.name:<14} {p.category:<12} ${float(p.unit_price):>6.2f} {p.reorder_level:>8}")

    print("\n" + "-" * 64)
    print("  INVENTORY TABLE")
    print("-" * 64)
    print(f"  {'Product':<14} {'On Hand':>10} {'Allocated':>10} {'Reserved':>10}")
    print("-" * 64)
    for inv in db.query(Inventory).all():
        prod = db.query(Product).filter(Product.id == inv.product_id).first()
        name = prod.name if prod else "?"
        print(f"  {name:<14} {inv.stock_on_hand:>10} {inv.allocated_stock:>10} {inv.reserved_stock:>10}")

    print("\n" + "-" * 64)
    print("  PREDICTION TABLE")
    print("-" * 64)
    print(f"  {'Product':<14} {'Predicted':>10}  {'Risk Level'}")
    print("-" * 64)
    for r in db.query(Prediction).all():
        print(f"  {r.product_name:<14} {r.predicted_stock:>10.2f}  {r.risk_level}")

    print("\n" + "-" * 64)
    print("  DECISION LOG TABLE")
    print("-" * 64)
    for r in db.query(DecisionLog).all():
        print(f"  [{r.status.upper():<8}] {r.recommendation[:80]}")

    print("\n" + "=" * 64)
    print("  Phase 5 Database Seeding Complete!")
    print("=" * 64 + "\n")

except Exception as exc:
    db.rollback()
    print(f"\nSeeding failed: {exc}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
