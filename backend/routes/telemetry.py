'''Telemetry endpoint for OpsMind AI production.
Provides a quick health snapshot of the running service.
'''
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
import os
import glob

router = APIRouter(prefix="/api/v1/telemetry", tags=["Telemetry"])

@router.get("/status", status_code=status.HTTP_200_OK)
def health_status(db: Session = Depends(get_db)):
    # Database connectivity check
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "error"

    # Model artifacts presence check
    model_dir = os.getenv("MODEL_DIR", "ml/saved_models")
    model_files = glob.glob(f"{model_dir}/*.joblib")
    ml_status = "loaded" if model_files else "missing"

    # Fixed dataset source identifier (Kaggle edition)
    dataset_source = "Kaggle_Store_Demand"

    return {
        "environment": os.getenv("ENVIRONMENT", "production"),
        "database": db_status,
        "ml_artifacts": ml_status,
        "dataset_source": dataset_source,
    }
