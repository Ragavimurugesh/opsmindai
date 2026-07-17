"""
OpsMind AI - FastAPI Backend
============================
Central API server exposing inventory, predictions, decisions, and forecast endpoints.
"""

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

from database import engine, Base, get_db
import models as orm_models

# Create tables if they don't exist (safe idempotent call)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="OpsMind AI Backend", version="0.2.0")

# CORS – allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Response Schemas
# ─────────────────────────────────────────────────────────────────────────────

class InventoryOut(BaseModel):
    """Combined product + inventory data for the dashboard."""
    id: str
    sku: str
    product_name: str
    category: str
    unit_price: float
    reorder_level: int
    stock_on_hand: int
    allocated_stock: int
    reserved_stock: int

    class Config:
        from_attributes = True


class PredictionOut(BaseModel):
    id: int
    product_name: str
    predicted_stock: float
    risk_level: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class DecisionOut(BaseModel):
    id: int
    recommendation: str
    status: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class ForecastOut(BaseModel):
    date: str
    forecast: float
    confidence_lower: float
    confidence_upper: float
    model_engine: str
    historical: Optional[float] = None

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Quick health check verifying DB connectivity."""
    try:
        db.execute(orm_models.Product.__table__.select().limit(1))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}


@app.get("/inventory", response_model=List[InventoryOut])
@app.get("/api/inventory", response_model=List[InventoryOut])
def get_inventory(db: Session = Depends(get_db)):
    """Return all products joined with their inventory levels."""
    try:
        rows = (
            db.query(orm_models.Product, orm_models.Inventory)
            .outerjoin(orm_models.Inventory, orm_models.Product.id == orm_models.Inventory.product_id)
            .order_by(orm_models.Product.sku)
            .all()
        )
        results = []
        for product, inv in rows:
            results.append(InventoryOut(
                id=str(product.id),
                sku=product.sku,
                product_name=product.name,
                category=product.category,
                unit_price=float(product.unit_price),
                reorder_level=product.reorder_level,
                stock_on_hand=inv.stock_on_hand if inv else 0,
                allocated_stock=inv.allocated_stock if inv else 0,
                reserved_stock=inv.reserved_stock if inv else 0,
            ))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predict", response_model=List[PredictionOut])
def get_predictions(db: Session = Depends(get_db)):
    """Return all prediction records."""
    try:
        preds = (
            db.query(orm_models.Prediction)
            .order_by(orm_models.Prediction.created_at.desc())
            .all()
        )
        return [
            PredictionOut(
                id=p.id,
                product_name=p.product_name,
                predicted_stock=p.predicted_stock,
                risk_level=p.risk_level,
                created_at=str(p.created_at) if p.created_at else None,
            )
            for p in preds
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/decision", response_model=List[DecisionOut])
def get_decisions(db: Session = Depends(get_db)):
    """Return all decision log entries."""
    try:
        decisions = (
            db.query(orm_models.DecisionLog)
            .order_by(orm_models.DecisionLog.created_at.desc())
            .all()
        )
        return [
            DecisionOut(
                id=d.id,
                recommendation=d.recommendation,
                status=d.status or "pending",
                created_at=str(d.created_at) if d.created_at else None,
            )
            for d in decisions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decision", response_model=List[DecisionOut])
def generate_decisions(db: Session = Depends(get_db)):
    """Generate new decision entries from the latest predictions."""
    try:
        latest = (
            db.query(orm_models.Prediction)
            .order_by(orm_models.Prediction.created_at.desc())
            .all()
        )
        if not latest:
            raise HTTPException(status_code=404, detail="No predictions available")

        decisions = []
        for pred in latest:
            if pred.risk_level == "Low Stock Risk":
                recommendation = (
                    f"Stock of {pred.product_name} is critically low. "
                    f"Immediately reorder to avoid stockout."
                )
                status = "critical"
            else:
                recommendation = (
                    f"Stock of {pred.product_name} is sufficient. No action needed."
                )
                status = "healthy"

            decision = orm_models.DecisionLog(
                recommendation=recommendation, status=status
            )
            db.add(decision)
            decisions.append(decision)

        db.commit()
        for d in decisions:
            db.refresh(d)

        return [
            DecisionOut(
                id=d.id,
                recommendation=d.recommendation,
                status=d.status,
                created_at=str(d.created_at) if d.created_at else None,
            )
            for d in decisions
        ]
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/forecast", response_model=List[ForecastOut])
def get_forecasts(sku: str = "SKU-001", horizon: int = 30, db: Session = Depends(get_db)):
    """Return forecast data for a given product SKU and time horizon."""
    try:
        product = (
            db.query(orm_models.Product)
            .filter(orm_models.Product.sku == sku)
            .first()
        )
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {sku} not found")

        forecasts = (
            db.query(orm_models.Forecast)
            .filter(orm_models.Forecast.product_id == product.id)
            .order_by(orm_models.Forecast.forecast_date)
            .limit(horizon)
            .all()
        )

        return [
            ForecastOut(
                date=str(f.forecast_date),
                forecast=float(f.forecast_quantity),
                confidence_lower=float(f.confidence_lower),
                confidence_upper=float(f.confidence_upper),
                model_engine=f.model_engine,
                historical=None,
            )
            for f in forecasts
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
@app.get("/api/config")
def get_config():
    """Expose Supabase credentials and connection info to UI Profile page."""
    return {
        "supabase_url": os.getenv("SUPABASE_URL", "https://wvbuqgfghbeyiifpgqxh.supabase.co"),
        "supabase_anon_key": os.getenv("SUPABASE_ANON_KEY", ""),
        "supabase_service_role_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
        "database_url": os.getenv("DATABASE_URL", ""),
        "project_ref": "wvbuqgfghbeyiifpgqxh",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

