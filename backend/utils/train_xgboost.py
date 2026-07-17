'''XGBoost training utility.
- prepare_features(df) adds lag/rolling columns using utils.preprocess functions.
- split_chronological(df) splits data into train and validation sets based on date order.
- train_xgb(X_train, y_train, params=None) returns a fitted XGBRegressor.
'''
import pandas as pd
from xgboost import XGBRegressor
from utils.preprocess import add_lag_features

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df = add_lag_features(df)
    return df.dropna().reset_index(drop=True)

def split_chronological(df: pd.DataFrame, train_ratio: float = 0.78):
    df = df.sort_values('date')
    split_idx = int(len(df) * train_ratio)
    train = df.iloc[:split_idx]
    val = df.iloc[split_idx:]
    X_train = train.drop(columns=['quantity', 'date'])
    y_train = train['quantity']
    X_val = val.drop(columns=['quantity', 'date'])
    y_val = val['quantity']
    return X_train, y_train, X_val, y_val

def train_xgb(X_train, y_train, params=None):
    default_params = {
        'n_estimators': 500,
        'max_depth': 6,
        'learning_rate': 0.05,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'objective': 'reg:squarederror',
        'n_jobs': -1,
        'random_state': 42,
    }
    if params:
        default_params.update(params)
    model = XGBRegressor(**default_params)
    model.fit(X_train, y_train)
    return model
