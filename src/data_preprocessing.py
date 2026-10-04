"""
Data Preprocessing Module
Cleans, normalizes, handles anomalies, and chronologically sorts inventory data.
"""

import pandas as pd
import numpy as np

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare the hotel inventory dataset for analysis and ML.
    
    Steps:
    1. Make a deep copy to avoid modifying raw data.
    2. Normalize text columns (strip whitespace, title casing).
    3. Parse 'date' to datetime and drop unparseable rows.
    4. Clean numeric columns, handle negative or NaN values safely.
    5. Remove duplicate records (same date and food_item).
    6. Sort data chronologically per food_item.
    
    Parameters:
    - df: Raw DataFrame.
    
    Returns:
    - pd.DataFrame: Cleaned and structured DataFrame.
    """
    cleaned_df = df.copy()
    
    # 1. Normalize column names (strip whitespace)
    cleaned_df.columns = [col.strip() for col in cleaned_df.columns]
    
    # 2. Text normalization
    cleaned_df["food_item"] = cleaned_df["food_item"].astype(str).str.strip()
    cleaned_df["category"] = cleaned_df["category"].astype(str).str.strip()
    
    # 3. Date handling
    cleaned_df["date"] = pd.to_datetime(cleaned_df["date"], errors="coerce")
    cleaned_df = cleaned_df.dropna(subset=["date"])
    
    # 4. Clean numeric columns
    numeric_columns = [
        "previous_stock",
        "current_stock",
        "daily_usage",
        "monthly_requirement",
        "safety_stock_percentage"
    ]
    
    for col in numeric_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors="coerce")
            # Fill missing with median or 0
            median_val = cleaned_df[col].median()
            if pd.isna(median_val):
                median_val = 0.0
            cleaned_df[col] = cleaned_df[col].fillna(median_val)
            # Ensure no negative stock or usage values
            cleaned_df[col] = cleaned_df[col].clip(lower=0.0)
            
    # Round numerical values for clean display
    cleaned_df["previous_stock"] = cleaned_df["previous_stock"].round(2)
    cleaned_df["current_stock"] = cleaned_df["current_stock"].round(2)
    cleaned_df["daily_usage"] = cleaned_df["daily_usage"].round(2)
    cleaned_df["monthly_requirement"] = cleaned_df["monthly_requirement"].round(0)
    cleaned_df["safety_stock_percentage"] = cleaned_df["safety_stock_percentage"].round(1)
    
    # 5. Remove duplicates based on date and food item
    cleaned_df = cleaned_df.drop_duplicates(subset=["date", "food_item"], keep="last")
    
    # 6. Sort chronologically per food item
    cleaned_df = cleaned_df.sort_values(by=["food_item", "date"]).reset_index(drop=True)
    
    return cleaned_df

def get_latest_inventory_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the most recent day's record for each food item.
    Represents the 'as-of-today' current stock state for decision making.
    
    Parameters:
    - df: Preprocessed DataFrame.
    
    Returns:
    - pd.DataFrame: Latest record per food item.
    """
    # Group by food item and get the row with maximum date
    latest_indices = df.groupby("food_item")["date"].idxmax()
    snapshot = df.loc[latest_indices].copy().reset_index(drop=True)
    return snapshot
