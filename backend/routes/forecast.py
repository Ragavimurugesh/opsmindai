'''Forecasting API routes.
Provides endpoints to train a model for a specific product and retrieve the 90‑day horizon forecast.
'''

import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from services.ml_engine import train_and_select
from models.inventory import Product, Forecast

router = APIRouter(prefix="/api/v1/predict", tags=["Forecasting"])

@router.post("/train/{product_id}", status_code=status.HTTP_202_ACCEPTED)
def train_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    result = train_and_select(db, product.sku)
    return result

@router.get("/horizon/{product_id}")
def get_forecast(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    forecasts = (
        db.query(Forecast)
        .filter(Forecast.product_id == product.id)
        .order_by(Forecast.forecast_date)
        .all()
    )
    return [
        {
            "date": f.forecast_date.isoformat(),
            "quantity": float(f.forecast_quantity),
            "lower": float(f.confidence_lower) if f.confidence_lower is not None else None,
            "upper": float(f.confidence_upper) if f.confidence_upper is not None else None,
            "model": f.model_engine,
        }
        for f in forecasts
    ]
