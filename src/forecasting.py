"""
Demand Forecasting Module
Generates forward-looking consumption forecasts over 7, 14, or 30-day planning horizons.
"""

from typing import Dict, Tuple, List
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

from src.feature_engineering import prepare_feature_row_for_inference

def generate_future_forecast(
    model: RandomForestRegressor,
    df_preprocessed: pd.DataFrame,
    encoders: Dict[str, LabelEncoder],
    horizon_days: int = 7
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate multi-step future demand forecasts using recursive forward projection.
    
    Parameters:
    - model: Trained RandomForestRegressor.
    - df_preprocessed: Cleaned historical dataset.
    - encoders: Fitted label encoders for food_item and category.
    - horizon_days: Forecast period in days (e.g. 7, 14, 30).
    
    Returns:
    - Tuple[pd.DataFrame, pd.DataFrame]:
        1. summary_df: Item-level aggregate demand for the forecast period.
        2. trajectory_df: Daily projected consumption for each item (for plotting).
    """
    food_items = df_preprocessed["food_item"].unique()
    
    summary_records = []
    trajectory_records = []
    
    for item in food_items:
        item_data = df_preprocessed[df_preprocessed["food_item"] == item].sort_values("date")
        
        if item_data.empty:
            continue
            
        category = item_data["category"].iloc[-1]
        last_row = item_data.iloc[-1]
        last_date = last_row["date"]
        current_stock = float(last_row["current_stock"])
        safety_stock_pct = float(last_row["safety_stock_percentage"])
        monthly_req = float(last_row["monthly_requirement"])
        
        # Recent usage history (last 14 days)
        recent_usages = item_data["daily_usage"].tail(14).tolist()
        if len(recent_usages) < 14:
            # Pad if history is short
            mean_val = float(np.mean(recent_usages)) if recent_usages else 10.0
            recent_usages = [mean_val] * (14 - len(recent_usages)) + recent_usages
            
        daily_preds = []
        
        # Recursive forward forecasting for each day in horizon
        for step in range(1, horizon_days + 1):
            future_date = last_date + pd.Timedelta(days=step)
            
            # Build feature vector
            feature_row = prepare_feature_row_for_inference(
                date=future_date,
                food_item=item,
                category=category,
                historical_usages=recent_usages,
                current_stock=current_stock,
                encoders=encoders
            )
            
            # Predict daily usage
            pred_usage = float(model.predict(feature_row)[0])
            pred_usage = max(0.5, round(pred_usage, 2))
            
            daily_preds.append(pred_usage)
            
            # Update history window for next step recursive prediction
            recent_usages.append(pred_usage)
            if len(recent_usages) > 14:
                recent_usages.pop(0)
                
            trajectory_records.append({
                "date": future_date.strftime("%Y-%m-%d"),
                "food_item": item,
                "category": category,
                "predicted_daily_usage": pred_usage
            })
            
        total_predicted_demand = round(float(np.sum(daily_preds)), 2)
        daily_avg_demand = round(total_predicted_demand / horizon_days, 2)
        
        summary_records.append({
            "food_item": item,
            "category": category,
            "current_stock": current_stock,
            "daily_avg_demand": daily_avg_demand,
            "predicted_demand": total_predicted_demand,
            "forecast_days": horizon_days,
            "safety_stock_percentage": safety_stock_pct,
            "monthly_requirement": monthly_req
        })
        
    summary_df = pd.DataFrame(summary_records)
    trajectory_df = pd.DataFrame(trajectory_records)
    
    return summary_df, trajectory_df
