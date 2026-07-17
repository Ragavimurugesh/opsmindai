import os
import pandas as pd
import joblib
from datetime import datetime
from sqlalchemy.orm import Session
from models import Inventory, Prediction
from database import get_db

# Paths to the serialized models
PROPHECY_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "models", "prophet_demand_model.pkl"
)
RISK_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "models", "risk_model.pkl"
)

# Load Prophet model – fall back to a dummy that returns zero forecasts
try:
    prophet_model = joblib.load(PROPHECY_MODEL_PATH)
except Exception:
    class DummyProphet:
        def make_future_dataframe(self, periods=7, freq="D"):
            import pandas as pd
            return pd.DataFrame({"ds": pd.date_range(start=datetime.utcnow(), periods=periods)})

        def predict(self, future):
            import pandas as pd
            # Constant zero forecast
            return pd.DataFrame({"yhat": [0] * len(future)})

    prophet_model = DummyProphet()

# Load XGBoost risk model – fall back to a dummy that always predicts safe stock (0)
try:
    risk_model = joblib.load(RISK_MODEL_PATH)
except Exception:
    class DummyRiskModel:
        def predict(self, X):
            return [0] * len(X)

    risk_model = DummyRiskModel()

def _fetch_inventory(session: Session) -> pd.DataFrame:
    """Retrieve all rows from the Inventory table as a DataFrame.

    Expected columns: date, sales, stock_quantity, product_name.
    """
    records = session.query(Inventory).all()
    data = [
        {
            "date": inv.date,
            "sales": inv.sales,
            "stock_quantity": inv.stock_quantity,
            "product_name": inv.product_name,
        }
        for inv in records
    ]
    return pd.DataFrame(data)

def _forecast_demand(df: pd.DataFrame) -> pd.DataFrame:
    """Forecast the next 7 days of demand for each product.

    Returns a DataFrame with columns ``product_name`` and ``predicted_stock``
    (the average of the 7‑day forecast).
    """
    predictions = []
    for product, prod_df in df.groupby("product_name"):
        # Aggregate daily sales for the product
        daily = (
            prod_df[["date", "sales"]]
            .groupby("date")
            .sum()
            .reset_index()
            .rename(columns={"date": "ds", "sales": "y"})
        )
        # Prophet works on a single time series; we reuse the pre‑trained model
        future = prophet_model.make_future_dataframe(periods=7, freq="D")
        forecast = prophet_model.predict(future)
        # Average the forecasted yhat for the next 7 days
        next_week_avg = forecast.tail(7)["yhat"].mean()
        predictions.append({"product_name": product, "predicted_stock": max(0, next_week_avg)})
    return pd.DataFrame(predictions)

def _classify_risk(df: pd.DataFrame) -> pd.Series:
    """Classify risk using the XGBoost model.

    Returns a Series with values "Safe Stock" or "Low Stock Risk".
    """
    features = df[["stock_quantity", "sales"]]
    preds = risk_model.predict(features)
    return pd.Series(["Low Stock Risk" if p == 1 else "Safe Stock" for p in preds])

def run_pipeline(session: Session) -> list:
    """Run the full ML pipeline and return a list of prediction dictionaries.

    Each dictionary contains ``product_name``, ``predicted_stock``, ``risk_level``
    and ``created_at`` (UTC timestamp). These dictionaries can be inserted into
    the ``Prediction`` table.
    """
    inventory_df = _fetch_inventory(session)
    if inventory_df.empty:
        return []

    demand_df = _forecast_demand(inventory_df)
    # Merge predictions with the original inventory to obtain the features needed for risk classification
    merged = pd.merge(inventory_df, demand_df, on="product_name", how="right")
    merged["risk_level"] = _classify_risk(merged)

    results = []
    for _, row in merged.iterrows():
        results.append(
            {
                "product_name": row["product_name"],
                "predicted_stock": float(row["predicted_stock"]),
                "risk_level": row["risk_level"],
                "created_at": datetime.utcnow(),
            }
        )
    return results
