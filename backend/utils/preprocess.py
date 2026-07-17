import pandas as pd
import numpy as np
from typing import Union

def extract_temporal_features(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """
    Parses date column and extracts chronological markers: year, month, day, day_of_week, and is_weekend.
    """
    df = df.copy()
    # Ensure column is parsed to datetime
    df[date_col] = pd.to_datetime(df[date_col])
    
    df["year"] = df[date_col].dt.year
    df["month"] = df[date_col].dt.month
    df["day"] = df[date_col].dt.day
    df["day_of_week"] = df[date_col].dt.dayofweek # Mon=0, Sun=6
    df["is_weekend"] = df["day_of_week"].apply(lambda x: 1 if x in (5, 6) else 0)
    
    return df

def create_lag_features(
    df: pd.DataFrame, 
    sku_col: str = "sku", 
    date_col: str = "date", 
    value_col: str = "quantity"
) -> pd.DataFrame:
    """
    Generates historical rolling window metrics and lagging features (lag_7, lag_30, rolling_mean_7)
    grouped by SKU to prevent data leakage between products.
    """
    df = df.copy()
    # Sort chronological order per SKU
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(by=[sku_col, date_col]).reset_index(drop=True)
    
    # 7-day and 30-day offsets
    df["lag_7"] = df.groupby(sku_col)[value_col].shift(7)
    df["lag_30"] = df.groupby(sku_col)[value_col].shift(30)
    
    # 7-day rolling average (excluding the current day's quantity to prevent leakage)
    df["rolling_mean_7"] = (
        df.groupby(sku_col)[value_col]
        .transform(lambda x: x.shift(1).rolling(window=7).mean())
    )
    
    # Fill NaN values introduced by shifting operations with 0 or group median
    df["lag_7"] = df["lag_7"].fillna(0)
    df["lag_30"] = df["lag_30"].fillna(0)
    df["rolling_mean_7"] = df["rolling_mean_7"].fillna(0)
    
    return df

def to_prophet_format(
    df: pd.DataFrame, 
    target_sku: str, 
    sku_col: str = "sku", 
    date_col: str = "date", 
    value_col: str = "quantity"
) -> pd.DataFrame:
    """
    Filters the dataset by a specific SKU and formats columns into Prophet-mandated 'ds' and 'y' columns.
    """
    filtered_df = df[df[sku_col] == target_sku].copy()
    
    # Sort by date
    filtered_df[date_col] = pd.to_datetime(filtered_df[date_col])
    filtered_df = filtered_df.sort_values(by=date_col)
    
    # Extract only required columns for Prophet model fitting
    prophet_df = filtered_df[[date_col, value_col]].rename(
        columns={date_col: "ds", value_col: "y"}
    )
    
    # Convert 'ds' column to timezone-naive datestamps as required by Prophet
    prophet_df["ds"] = prophet_df["ds"].dt.tz_localize(None)
    
    return prophet_df.reset_index(drop=True)

def clean_data(df: pd.DataFrame, numeric_cols: list = None) -> pd.DataFrame:
    """
    Runs automated exception handling to remove/clamp statistical outliers,
    replaces infinite values, and fills missing row values safely.
    """
    df = df.copy()
    
    # If no columns specified, clean numeric types
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
    for col in numeric_cols:
        # 1. Replace infinite bounds with NaNs
        df[col] = df[col].replace([np.inf, -np.inf], np.nan)
        
        # 2. Fill missing row indexes with column median
        col_median = df[col].median()
        if pd.isna(col_median):
            col_median = 0
        df[col] = df[col].fillna(col_median)
        
        # 3. Handle outliers using Z-score clamping (Z > 3 std devs)
        mean_val = df[col].mean()
        std_val = df[col].std()
        
        # Prevent division-by-zero if std is zero (e.g. static values)
        if std_val > 0:
            upper_bound = mean_val + (3 * std_val)
            lower_bound = mean_val - (3 * std_val)
            
            # Clamp outliers within standard boundaries
            df[col] = np.clip(df[col], lower_bound, upper_bound)
            
    return df

def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """Alias for create_lag_features for backward compatibility."""
    return create_lag_features(df)
