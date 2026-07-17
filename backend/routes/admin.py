import os
import sys
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Setup project root pathing to allow dataset module imports
router_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(router_dir)
project_root = os.path.dirname(backend_dir)

if project_root not in sys.path:
    sys.path.append(project_root)

# Resolve local module imports
from dataset.generate_mock_data import generate_mock_data
from utils.preprocess import clean_data
from services.ingestion import ingest_dataframe_to_db
from database import get_db

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Administration / Ingestion Data Pipelines"]
)

@router.post("/ingest-data", status_code=status.HTTP_201_CREATED)
def trigger_bulk_data_ingestion(db: Session = Depends(get_db)):
    """
    Administrative endpoint to programmatically invoke warehouse simulation:
    1. Triggers mock historical generator for 2 years of logs.
    2. Cleans statistical outliers & null items.
    3. Batches transactions & registers master product SKUs into PostgreSQL.
    """
    try:
        # Resolve target raw file location
        raw_csv_path = os.path.join(project_root, "dataset", "raw", "warehouse_sales_raw.csv")
        
        # 1. Run simulation generator
        raw_df = generate_mock_data(raw_csv_path)
        
        # 2. Preprocess and clean dataset (clamp outliers & handle missing indexes)
        cleaned_df = clean_data(
            raw_df, 
            numeric_cols=["quantity", "unit_price", "reorder_level"]
        )
        
        # 3. Run transactional ingestion sequences
        telemetry = ingest_dataframe_to_db(db, cleaned_df)
        
        return {
            "status": "success",
            "total_products_loaded": telemetry["total_products_loaded"],
            "total_transactions_recorded": telemetry["total_transactions_recorded"],
            "message": "Data pipeline executed, cleansed, and committed successfully."
        }
        
    except Exception as pipeline_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion pipeline flow failed: {str(pipeline_error)}"
        )
