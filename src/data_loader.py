"""
Data Loader and Validator Module
Handles dataset loading, schema validation, and data quality profiling.
"""

from typing import Tuple, List, Dict, Any, Union
import pandas as pd
import numpy as np

# Mandatory columns required for the forecasting and inventory pipeline
REQUIRED_COLUMNS = [
    "date",
    "food_item",
    "category",
    "previous_stock",
    "current_stock",
    "daily_usage",
    "monthly_requirement",
    "safety_stock_percentage"
]

def load_data(file_input: Union[str, Any]) -> pd.DataFrame:
    """
    Load dataset from a file path or a Streamlit UploadedFile object.
    
    Parameters:
    - file_input: Path to file (str) or file-like buffer (e.g. UploadedFile).
    
    Returns:
    - pd.DataFrame: Loaded dataset.
    """
    try:
        df = pd.read_csv(file_input)
        # Strip whitespace from column names if present
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        raise ValueError(f"Failed to read CSV file: {str(e)}")

def validate_data(df: pd.DataFrame) -> Tuple[bool, List[str], str]:
    """
    Validate whether the DataFrame has the required columns and non-empty structure.
    
    Parameters:
    - df: Input DataFrame.
    
    Returns:
    - Tuple[bool, List[str], str]: (is_valid, missing_columns, message)
    """
    if df is None or df.empty:
        return False, REQUIRED_COLUMNS, "The uploaded dataset is empty."
    
    existing_columns = [col.lower() for col in df.columns]
    missing = []
    
    for req_col in REQUIRED_COLUMNS:
        if req_col.lower() not in existing_columns:
            missing.append(req_col)
            
    if missing:
        msg = f"Data validation error: Missing required column(s): {', '.join(missing)}."
        return False, missing, msg
        
    return True, [], "Dataset passed schema validation."

def compute_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute transparent data quality metrics for the user dashboard.
    
    Parameters:
    - df: Input DataFrame.
    
    Returns:
    - Dict with counts of total rows, missing values, duplicates, invalid records, and valid records.
    """
    if df is None or df.empty:
        return {
            "total_rows": 0,
            "missing_values": 0,
            "duplicate_rows": 0,
            "invalid_records": 0,
            "valid_records": 0,
            "unique_items": 0,
            "unique_categories": 0,
            "date_range": "N/A"
        }
        
    total_rows = len(df)
    missing_vals = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    
    # Check for negative numerical values in stock or usage
    numeric_cols = ["previous_stock", "current_stock", "daily_usage", "monthly_requirement", "safety_stock_percentage"]
    negative_mask = pd.Series(False, index=df.index)
    
    for col in numeric_cols:
        if col in df.columns:
            # Coerce to numeric to check for invalid/negative values
            num_series = pd.to_numeric(df[col], errors='coerce')
            negative_mask |= (num_series < 0) | num_series.isna()
            
    # Check for invalid date formatting
    if "date" in df.columns:
        parsed_dates = pd.to_datetime(df["date"], errors='coerce')
        date_invalid_mask = parsed_dates.isna()
    else:
        date_invalid_mask = pd.Series(True, index=df.index)
        
    invalid_mask = negative_mask | date_invalid_mask
    invalid_records = int(invalid_mask.sum())
    valid_records = max(0, total_rows - invalid_records)
    
    unique_items = int(df["food_item"].nunique()) if "food_item" in df.columns else 0
    unique_categories = int(df["category"].nunique()) if "category" in df.columns else 0
    
    if "date" in df.columns and not df["date"].empty:
        valid_dates = pd.to_datetime(df["date"], errors='coerce').dropna()
        if not valid_dates.empty:
            date_range = f"{valid_dates.min().strftime('%Y-%m-%d')} to {valid_dates.max().strftime('%Y-%m-%d')}"
        else:
            date_range = "Invalid dates"
    else:
        date_range = "N/A"
        
    return {
        "total_rows": total_rows,
        "missing_values": missing_vals,
        "duplicate_rows": duplicate_rows,
        "invalid_records": invalid_records,
        "valid_records": valid_records,
        "unique_items": unique_items,
        "unique_categories": unique_categories,
        "date_range": date_range
    }
