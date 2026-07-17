import os
import pandas as pd
import numpy as np
import pickle
from pathlib import Path

# Prophet and XGBoost imports
try:
    from prophet import Prophet
except ImportError:
    raise ImportError("Please install Prophet: pip install prophet")

try:
    import xgboost as xgb
except ImportError:
    raise ImportError("Please install XGBoost: pip install xgboost")


def find_column(df: pd.DataFrame, candidates: list) -> str:
    """Return the first matching column name from candidates (case‑insensitive)."""
    lowered = {c.lower(): c for c in df.columns}
    for cand in candidates:
        for col_lower, col_orig in lowered.items():
            if cand in col_lower:
                return col_orig
    raise KeyError(f"No column matching any of {candidates} found in dataframe columns: {list(df.columns)}")


def load_and_clean_data(raw_path: Path, cleaned_path: Path) -> pd.DataFrame:
    # Load raw data
    df = pd.read_csv(raw_path)

    # Identify relevant columns using flexible name mapping
    date_col = find_column(df, ["date", "date_", "order_date", "sale_date"])
    sales_col = find_column(df, ["sales", "sale", "units_sold", "quantity_sold", "quantity", "qty"])
    # Stock column may be missing – try to locate it
    try:
        stock_col = find_column(df, ["stock_quantity", "stock", "inventory", "stock_qty"])
    except KeyError:
        stock_col = None

    # Convert date column to datetime
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    # Drop rows where date could not be parsed
    df = df.dropna(subset=[date_col])

    # Ensure sales column is numeric
    df[sales_col] = pd.to_numeric(df[sales_col], errors="coerce")

    # Handle missing stock information
    if stock_col:
        df[stock_col] = pd.to_numeric(df[stock_col], errors="coerce")
        # Fill missing numeric values with median of the column
        median_stock = df[stock_col].median()
        df[stock_col] = df[stock_col].fillna(median_stock)
    else:
        # Simulate realistic stock values based on sales * random multiplier (1.0‑1.5)
        stock_col = "Stock_Quantity"
        multiplier = np.random.uniform(1.0, 1.5, size=len(df))
        df[stock_col] = df[sales_col] * multiplier

    # Fill missing sales values with median
    median_sales = df[sales_col].median()
    df[sales_col] = df[sales_col].fillna(median_sales)

    # Persist cleaned dataset
    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cleaned_path, index=False)
    return df, date_col, sales_col, stock_col


def train_prophet(df: pd.DataFrame, date_col: str, sales_col: str, model_path: Path):
    # Aggregate sales per day
    daily = (
        df[[date_col, sales_col]]
        .groupby(date_col)
        .sum()
        .reset_index()
        .rename(columns={date_col: "ds", sales_col: "y"})
    )
    model = Prophet(yearly_seasonality=False, daily_seasonality=False, weekly_seasonality=True)
    model.fit(daily)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"Prophet model saved to {model_path}")


def train_risk_classifier(df: pd.DataFrame, stock_col: str, sales_col: str, model_path: Path):
    # Create binary risk label
    df["Risk_Label"] = (df[stock_col] < 1.5 * df[sales_col]).astype(int)

    X = df[[stock_col, sales_col]]
    y = df["Risk_Label"]

    clf = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="logloss",
    )
    clf.fit(X, y)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(clf, f)
    print(f"Risk classification model saved to {model_path}")


def main():
    project_root = Path(__file__).resolve().parent.parent  # opsmind-ai
    raw_path = project_root / "dataset" / "raw_data.csv"
    cleaned_path = project_root / "dataset" / "cleaned_inventory.csv"
    prophet_path = project_root / "models" / "prophet_demand_model.pkl"
    risk_path = project_root / "models" / "risk_model.pkl"

    if not raw_path.is_file():
        raise FileNotFoundError(f"Raw dataset not found at {raw_path}")

    df, date_col, sales_col, stock_col = load_and_clean_data(raw_path, cleaned_path)
    train_prophet(df, date_col, sales_col, prophet_path)
    train_risk_classifier(df, stock_col, sales_col, risk_path)


if __name__ == "__main__":
    main()
