import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_mock_data(output_path: str = None) -> pd.DataFrame:
    """
    Generates 2 years of realistic daily warehouse transaction logs for 5 unique SKUs.
    Includes base demand, weekly/annual seasonality, promotions, and replenishment events.
    """
    # 1. Define Product Master Catalog
    products_metadata = {
        "SKU-001": {
            "name": "Organic Apples Bag",
            "category": "Fresh Produce",
            "unit_price": 2.99,
            "reorder_level": 150,
            "base_demand": 80,
            "weekly_season": [0.85, 0.85, 0.90, 0.95, 1.10, 1.20, 1.15], # Mon-Sun
            "yearly_season_peak_months": [9, 10], # Autumn harvest peak
            "yearly_season_peak_factor": 1.30,
            "promo_prob": 0.10,
            "promo_factor": 1.8,
            "noise_std": 10
        },
        "SKU-002": {
            "name": "Whole Milk 1 Gallon",
            "category": "Dairy",
            "unit_price": 3.49,
            "reorder_level": 250,
            "base_demand": 120,
            "weekly_season": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], # Flat weekly
            "yearly_season_peak_months": [11, 12], # Winter baking season
            "yearly_season_peak_factor": 1.15,
            "promo_prob": 0.05,
            "promo_factor": 1.5,
            "noise_std": 8
        },
        "SKU-003": {
            "name": "Sourdough Bread Loaf",
            "category": "Bakery",
            "unit_price": 4.50,
            "reorder_level": 100,
            "base_demand": 60,
            "weekly_season": [0.75, 0.80, 0.85, 0.90, 1.20, 1.35, 1.15], # Weekend peak
            "yearly_season_peak_months": [10, 11, 12], # Autumn/Winter
            "yearly_season_peak_factor": 1.20,
            "promo_prob": 0.08,
            "promo_factor": 1.6,
            "noise_std": 6
        },
        "SKU-004": {
            "name": "Fresh Salmon Fillet",
            "category": "Seafood",
            "unit_price": 12.99,
            "reorder_level": 80,
            "base_demand": 40,
            "weekly_season": [0.70, 0.75, 0.80, 0.90, 1.40, 1.25, 1.00], # Friday peak
            "yearly_season_peak_months": [6, 7, 12], # Summer grilling + Christmas
            "yearly_season_peak_factor": 1.40,
            "promo_prob": 0.04,
            "promo_factor": 2.0,
            "noise_std": 5
        },
        "SKU-005": {
            "name": "Greek Yogurt 32oz",
            "category": "Dairy",
            "unit_price": 1.99,
            "reorder_level": 180,
            "base_demand": 100,
            "weekly_season": [1.10, 1.15, 1.10, 1.05, 0.90, 0.85, 0.85], # Mid-week healthy grocery peak
            "yearly_season_peak_months": [1, 5, 6], # New Year resolution + Summer diet
            "yearly_season_peak_factor": 1.25,
            "promo_prob": 0.12,
            "promo_factor": 1.4,
            "noise_std": 12
        }
    }

    # Set random seed for consistency
    np.random.seed(42)

    # 2. Setup date parameters (2 years daily)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=730)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')

    transactions = []

    # 3. Simulate inventory flow for each SKU
    for sku, meta in products_metadata.items():
        # Initialize running stock tracking
        running_stock = 1500 # Starting stock allocation
        
        # Day 0: Log initial INBOUND replenishment to initialize stock
        transactions.append({
            "date": start_date.strftime("%Y-%m-%d"),
            "sku": sku,
            "product_name": meta["name"],
            "category": meta["category"],
            "unit_price": meta["unit_price"],
            "reorder_level": meta["reorder_level"],
            "quantity": running_stock,
            "transaction_type": "INBOUND",
            "is_promotion": 0
        })

        for single_date in date_range[1:]:
            day_of_week = single_date.dayofweek # Mon=0, Sun=6
            month = single_date.month
            
            # Determine promotion state
            is_promo = 1 if np.random.rand() < meta["promo_prob"] else 0
            
            # Calculate demand elements
            base = meta["base_demand"]
            week_factor = meta["weekly_season"][day_of_week]
            
            year_factor = 1.0
            if month in meta["yearly_season_peak_months"]:
                year_factor = meta["yearly_season_peak_factor"]
                
            promo_multiplier = meta["promo_factor"] if is_promo else 1.0
            noise = np.random.normal(0, meta["noise_std"])
            
            # Calculate final demand quantity (OUTBOUND)
            demand = int(round((base * week_factor * year_factor * promo_multiplier) + noise))
            demand = max(1, demand) # ensure at least 1 unit is sold
            
            # Log OUTBOUND transaction
            transactions.append({
                "date": single_date.strftime("%Y-%m-%d"),
                "sku": sku,
                "product_name": meta["name"],
                "category": meta["category"],
                "unit_price": meta["unit_price"],
                "reorder_level": meta["reorder_level"],
                "quantity": demand,
                "transaction_type": "OUTBOUND",
                "is_promotion": is_promo
            })
            
            # Update running stock tracker
            running_stock = max(0, running_stock - demand)
            
            # Check if replenishment is needed (reorder trigger)
            if running_stock <= meta["reorder_level"]:
                replenishment_quantity = meta["reorder_level"] * 5
                running_stock += replenishment_quantity
                
                # Log INBOUND replenishment transaction
                transactions.append({
                    "date": single_date.strftime("%Y-%m-%d"),
                    "sku": sku,
                    "product_name": meta["name"],
                    "category": meta["category"],
                    "unit_price": meta["unit_price"],
                    "reorder_level": meta["reorder_level"],
                    "quantity": replenishment_quantity,
                    "transaction_type": "INBOUND",
                    "is_promotion": 0
                })

    df = pd.DataFrame(transactions)
    df = df.sort_values(by=["date", "sku"]).reset_index(drop=True)

    # 4. Save to flat file if requested
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Mock dataset generated successfully at: {output_path}")
        print(f"Total Transactions: {len(df)}")
        
    return df

if __name__ == "__main__":
    # Standard default execution path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_csv = os.path.join(script_dir, "raw", "warehouse_sales_raw.csv")
    generate_mock_data(target_csv)
