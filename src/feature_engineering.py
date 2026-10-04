"""
Feature Engineering Module
Constructs time-series features without data leakage for demand forecasting.
"""

from typing import Tuple, List, Dict
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

FEATURE_COLUMNS = [
    "day_of_week",
    "day_of_month",
    "month",
    "is_weekend",
    "lag_1",
    "lag_7",
    "lag_14",
    "rolling_mean_7",
    "rolling_std_7",
    "rolling_mean_14",
    "previous_stock",
    "current_stock",
    "food_item_encoded",
    "category_encoded"
]

TARGET_COLUMN = "daily_usage"

def create_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, LabelEncoder]]:
    """
    Generate calendar, lag, and rolling window features for consumption prediction.
    Ensures strict temporal integrity (zero future data leakage).
    
    Parameters:
    - df: Preprocessed DataFrame sorted by food_item and date.
    
    Returns:
    - Tuple[pd.DataFrame, Dict[str, LabelEncoder]]: Feature DataFrame and dictionary of fitted encoders.
    """
    df_feat = df.copy()
    
    # 1. Calendar / Temporal Features
    df_feat["day_of_week"] = df_feat["date"].dt.dayofweek
    df_feat["day_of_month"] = df_feat["date"].dt.day
    df_feat["month"] = df_feat["date"].dt.month
    df_feat["is_weekend"] = df_feat["day_of_week"].apply(lambda x: 1 if x in [4, 5, 6] else 0)
    
    # 2. Lag Features (Shifted consumption per item)
    # Using shift(1), shift(7), shift(14) ensures day t only sees historical consumption up to day t-1
    grouped = df_feat.groupby("food_item")["daily_usage"]
    
    df_feat["lag_1"] = grouped.shift(1)
    df_feat["lag_7"] = grouped.shift(7)
    df_feat["lag_14"] = grouped.shift(14)
    
    # 3. Rolling Statistics
    # CRITICAL: Rolling on shifted usage (shift(1)) ensures today's actual usage is never leaked
    shifted_usage = grouped.shift(1)
    df_feat["rolling_mean_7"] = df_feat.groupby("food_item", group_keys=False).apply(
        lambda g: g["daily_usage"].shift(1).rolling(window=7, min_periods=1).mean()
    )
    df_feat["rolling_std_7"] = df_feat.groupby("food_item", group_keys=False).apply(
        lambda g: g["daily_usage"].shift(1).rolling(window=7, min_periods=1).std()
    ).fillna(0.0)
    
    df_feat["rolling_mean_14"] = df_feat.groupby("food_item", group_keys=False).apply(
        lambda g: g["daily_usage"].shift(1).rolling(window=14, min_periods=1).mean()
    )
    
    # For early rows where lag_7 or lag_14 is NaN, fill with rolling_mean or lag_1
    df_feat["lag_1"] = df_feat["lag_1"].bfill().fillna(df_feat["daily_usage"])
    df_feat["lag_7"] = df_feat["lag_7"].bfill().fillna(df_feat["lag_1"])
    df_feat["lag_14"] = df_feat["lag_14"].bfill().fillna(df_feat["lag_7"])
    
    # 4. Categorical Encoding
    encoders = {}
    
    item_encoder = LabelEncoder()
    df_feat["food_item_encoded"] = item_encoder.fit_transform(df_feat["food_item"])
    encoders["food_item"] = item_encoder
    
    cat_encoder = LabelEncoder()
    df_feat["category_encoded"] = cat_encoder.fit_transform(df_feat["category"])
    encoders["category"] = cat_encoder
    
    # Clean up any lingering NaNs
    df_feat = df_feat.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN]).reset_index(drop=True)
    
    return df_feat, encoders

def prepare_feature_row_for_inference(
    date: pd.Timestamp,
    food_item: str,
    category: str,
    historical_usages: List[float],
    current_stock: float,
    encoders: Dict[str, LabelEncoder]
) -> pd.DataFrame:
    """
    Construct a single-day feature vector for forward-looking forecasting.
    
    Parameters:
    - date: The future date being predicted.
    - food_item: Food item name.
    - category: Category name.
    - historical_usages: Ordered list of recent daily usage values (most recent last).
    - current_stock: Stock available before consumption.
    - encoders: Pre-fitted LabelEncoders.
    
    Returns:
    - pd.DataFrame: Single-row DataFrame matching FEATURE_COLUMNS.
    """
    dow = date.dayofweek
    dom = date.day
    month = date.month
    is_weekend = 1 if dow in [4, 5, 6] else 0
    
    # Recent usage lookbacks
    # historical_usages[-1] is yesterday, [-7] is last week, [-14] is two weeks ago
    lag_1 = historical_usages[-1] if len(historical_usages) >= 1 else 10.0
    lag_7 = historical_usages[-7] if len(historical_usages) >= 7 else lag_1
    lag_14 = historical_usages[-14] if len(historical_usages) >= 14 else lag_7
    
    last_7 = historical_usages[-7:] if len(historical_usages) >= 7 else historical_usages
    last_14 = historical_usages[-14:] if len(historical_usages) >= 14 else historical_usages
    
    rolling_mean_7 = float(np.mean(last_7))
    rolling_std_7 = float(np.std(last_7)) if len(last_7) > 1 else 0.0
    rolling_mean_14 = float(np.mean(last_14))
    
    # Safe encoding for unseen categories/items if user uploads custom data
    try:
        food_encoded = int(encoders["food_item"].transform([food_item])[0])
    except Exception:
        food_encoded = 0
        
    try:
        cat_encoded = int(encoders["category"].transform([category])[0])
    except Exception:
        cat_encoded = 0
        
    row = {
        "day_of_week": dow,
        "day_of_month": dom,
        "month": month,
        "is_weekend": is_weekend,
        "lag_1": lag_1,
        "lag_7": lag_7,
        "lag_14": lag_14,
        "rolling_mean_7": rolling_mean_7,
        "rolling_std_7": rolling_std_7,
        "rolling_mean_14": rolling_mean_14,
        "previous_stock": current_stock,
        "current_stock": current_stock,
        "food_item_encoded": food_encoded,
        "category_encoded": cat_encoded
    }
    
    return pd.DataFrame([row])[FEATURE_COLUMNS]
