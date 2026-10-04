"""
Machine Learning Model Module
Trains and evaluates a RandomForestRegressor on time-series engineered features.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.feature_engineering import FEATURE_COLUMNS, TARGET_COLUMN

def train_demand_model(
    df_features: pd.DataFrame,
    test_ratio: float = 0.20,
    random_state: int = 42
) -> Tuple[RandomForestRegressor, Dict[str, float], pd.DataFrame, pd.DataFrame]:
    """
    Train a Random Forest regression model using a chronological time-series split.
    
    Why Chronological Split?
    In time-series demand forecasting, random shuffling causes temporal leakage.
    Training on older data and testing on recent data simulates actual deployment.
    
    Parameters:
    - df_features: DataFrame with engineered features and target.
    - test_ratio: Fraction of recent data reserved for testing (default: 20%).
    - random_state: Seed for reproducible tree generation.
    
    Returns:
    - Tuple: (trained_model, metrics_dict, feature_importance_df, test_predictions_df)
    """
    # Sort chronologically by date
    df_sorted = df_features.sort_values(by="date").reset_index(drop=True)
    
    split_index = int(len(df_sorted) * (1 - test_ratio))
    train_df = df_sorted.iloc[:split_index]
    test_df = df_sorted.iloc[split_index:].copy()
    
    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]
    
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]
    
    # Initialize Random Forest Regressor
    # 100 trees, max_depth 12 to prevent overfitting while capturing non-linear interactions
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=random_state,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Generate predictions on unseen test split
    y_pred = model.predict(X_test)
    y_pred = np.clip(y_pred, a_min=0.0, a_max=None)  # Consumption cannot be negative
    
    test_df["predicted_usage"] = y_pred.round(2)
    test_df["actual_usage"] = y_test.values
    test_df["error"] = (test_df["predicted_usage"] - test_df["actual_usage"]).round(2)
    
    # Compute evaluation metrics
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = float(r2_score(y_test, y_pred))
    
    metrics = {
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "R2": round(r2, 3),
        "Train_Samples": len(train_df),
        "Test_Samples": len(test_df)
    }
    
    # Extract Feature Importances
    importances = model.feature_importances_
    feat_df = pd.DataFrame({
        "Feature": FEATURE_COLUMNS,
        "Importance": importances
    }).sort_values(by="Importance", ascending=False).reset_index(drop=True)
    feat_df["Importance_Pct"] = (feat_df["Importance"] * 100).round(2)
    
    return model, metrics, feat_df, test_df
