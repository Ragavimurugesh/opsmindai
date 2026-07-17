'''Prophet training utility.
- get_history(db, sku) loads all transactions for a SKU and returns a dataframe with `ds` and `y`.
- train_prophet(df) fits a Prophet model with weekly & yearly seasonality.
- forecast_prophet(model, periods=90) returns a dataframe with `ds`, `yhat`, `yhat_lower`, `yhat_upper`.
'''
from prophet import Prophet
import pandas as pd
from sqlalchemy.orm import Session
from models.inventory import Transaction, Product

def get_history(db: Session, sku: str) -> pd.DataFrame:
    """Load transaction history for a given SKU and return df with columns ds (date) and y (quantity)."""
    query = (
        db.query(Transaction.created_at.label('ds'), Transaction.quantity.label('y'))
        .join(Product, Transaction.product_id == Product.id)
        .filter(Product.sku == sku)
        .order_by('ds')
    )
    df = pd.read_sql(query.statement, db.bind)
    return df

def train_prophet(df: pd.DataFrame) -> Prophet:
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
    model.fit(df)
    return model

def forecast_prophet(model: Prophet, periods: int = 90) -> pd.DataFrame:
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
