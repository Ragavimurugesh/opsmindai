"""Orchestrates training, evaluation, serialization, and forecast storage.

Functions:
* `train_and_select(db, sku)` – runs Prophet & XGBoost, computes RMSE/MAE/MAPE,
  selects the best model, and saves it.
* `store_forecast(db, sku, forecast_df, model_name)` – inserts forecast rows
  into the ``forecasts`` table.
"""

import os
import joblib
import pandas as pd
from sqlalchemy.orm import Session
from models import Forecast, Product, Transaction
from utils.train_prophet import get_history, train_prophet, forecast_prophet
from utils.train_xgboost import prepare_features, split_chronological, train_xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error


def mape(y_true, y_pred):
    """Mean Absolute Percentage Error."""
    y_true, y_pred = pd.Series(y_true), pd.Series(y_pred)
    return (
        abs((y_true - y_pred) / y_true)
        .replace([float("inf"), float("nan")], 0)
        .mean()
        * 100
    )


def evaluate(y_true, y_pred):
    """Return RMSE, MAE, and MAPE metrics."""
    return {
        "rmse": mean_squared_error(y_true, y_pred, squared=False),
        "mae": mean_absolute_error(y_true, y_pred),
        "mape": mape(y_true, y_pred),
    }


def train_and_select(db: Session, sku: str, model_dir: str = "ml/saved_models") -> dict:
    # ---------- Prophet ----------
    hist_df = get_history(db, sku)
    prophet_model = train_prophet(hist_df)

    # Evaluate on recent period (last 30 days)
    eval_df = hist_df.tail(30)
    prophet_pred = prophet_model.predict(eval_df)["yhat"]
    prophet_metrics = evaluate(eval_df["y"], prophet_pred)

    # ---------- XGBoost ----------
    raw_rows = (
        db.query(Transaction.created_at.label("date"), Transaction.quantity)
        .join(Product, Transaction.product_id == Product.id)
        .filter(Product.sku == sku)
        .order_by("date")
        .all()
    )
    df_raw = pd.DataFrame(raw_rows, columns=["date", "quantity"])
    xgb_df = prepare_features(df_raw)
    X_train, y_train, X_val, y_val = split_chronological(xgb_df)
    xgb_model = train_xgb(X_train, y_train)
    xgb_pred = xgb_model.predict(X_val)
    xgb_metrics = evaluate(y_val, xgb_pred)

    # ---------- Choose best model ----------
    best_name = "Prophet" if prophet_metrics["rmse"] <= xgb_metrics["rmse"] else "XGBoost"
    best_model = prophet_model if best_name == "Prophet" else xgb_model
    best_metrics = prophet_metrics if best_name == "Prophet" else xgb_metrics

    # ---------- Serialize model ----------
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"{sku}_{best_name}.joblib")
    joblib.dump(best_model, model_path)

    # ---------- Forecast storage (90‑day horizon) ----------
    if best_name == "Prophet":
        future = forecast_prophet(best_model, periods=90)
    else:
        # XGBoost future: generate dates, attach lag features, predict
        last_date = pd.to_datetime(df_raw["date"].max())
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=90)
        future_df = pd.DataFrame({"date": future_dates})
        extended = pd.concat([df_raw, future_df], ignore_index=True)
        future_features = prepare_features(extended).tail(90)
        preds = best_model.predict(future_features.drop(columns=["quantity"]))
        future = pd.DataFrame(
            {
                "ds": future_dates,
                "yhat": preds,
                "yhat_lower": preds * 0.95,
                "yhat_upper": preds * 1.05,
            }
        )
    store_forecast(db, sku, future, best_name)

    return {
        "status": "trained",
        "sku": sku,
        "best_model": best_name,
        "metrics": best_metrics,
        "model_path": model_path,
    }


def store_forecast(db: Session, sku: str, forecast_df: pd.DataFrame, model_name: str):
    """Insert (or replace) forecasts for a product."""
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise ValueError(f"Product with SKU {sku} not found")

    # Remove existing forecasts for idempotency
    db.query(Forecast).filter(Forecast.product_id == product.id).delete()

    rows = [
        {
            "product_id": product.id,
            "forecast_date": row["ds"].date()
            if hasattr(row["ds"], "date")
            else row["ds"],
            "forecast_quantity": row["yhat"],
            "confidence_lower": row.get("yhat_lower"),
            "confidence_upper": row.get("yhat_upper"),
            "model_engine": model_name,
        }
        for _, row in forecast_df.iterrows()
    ]

    db.bulk_insert_mappings(Forecast, rows)
    db.commit()
