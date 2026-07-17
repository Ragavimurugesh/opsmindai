import uuid
import pandas as pd
from sqlalchemy.orm import Session
from models import Product, Transaction

def ingest_dataframe_to_db(db: Session, df: pd.DataFrame) -> dict:
    """
    Ingests mock transaction dataframe objects directly into Supabase.
    First registers unique product profiles, maps transaction SKU entries,
    and maps batch transactional data utilizing a thread-safe rollback structure.
    """
    try:
        # Extract unique products based on SKU to insert metadata
        unique_products = df[
            ["sku", "product_name", "category", "unit_price", "reorder_level"]
        ].drop_duplicates(subset=["sku"])
        
        sku_to_id = {}
        products_inserted = 0
        
        # 1. Product mapping phase
        for _, row in unique_products.iterrows():
            # Check if product profile already exists in Supabase
            existing_product = db.query(Product).filter(Product.sku == row["sku"]).first()
            
            if existing_product:
                sku_to_id[row["sku"]] = existing_product.id
            else:
                # Create a new product entry
                new_product = Product(
                    id=uuid.uuid4(),
                    sku=row["sku"],
                    name=row["product_name"],
                    category=row["category"],
                    unit_price=row["unit_price"],
                    reorder_level=row["reorder_level"]
                )
                db.add(new_product)
                db.flush()  # Flush to generate ID within the active transaction
                sku_to_id[row["sku"]] = new_product.id
                products_inserted += 1
        
        # 2. Transaction mapping phase
        transaction_mappings = []
        for _, row in df.iterrows():
            prod_id = sku_to_id[row["sku"]]
            
            # Map transaction record columns
            transaction_mappings.append({
                "id": uuid.uuid4(),
                "product_id": prod_id,
                "quantity": int(row["quantity"]),
                "transaction_type": row["transaction_type"],
                "reference_note": f"Bulk data upload pipeline. Promotional tag: {row.get('is_promotion', 0)}",
                # Convert dates to UTC-aware datetime timestamps
                "created_at": pd.to_datetime(row["date"]).to_pydatetime()
            })
            
        # 3. Bulk insert executions
        db.bulk_insert_mappings(Transaction, transaction_mappings)
        
        # Multi-stage commit
        db.commit()
        
        return {
            "status": "success",
            "total_products_loaded": products_inserted,
            "total_transactions_recorded": len(transaction_mappings),
            "message": "Bulk data ingestion successfully committed."
        }
        
    except Exception as error:
        # Enforce secure rollback to maintain transactional boundary
        db.rollback()
        raise RuntimeError(f"Database bulk transaction ingestion aborted: {str(error)}")
