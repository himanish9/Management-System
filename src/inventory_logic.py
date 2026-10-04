"""
Inventory Decision Logic Module
Calculates safety stock, inventory requirements, stock gaps, and alert statuses.
"""

from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np

# Status string constants
STATUS_SUFFICIENT = "Sufficient Stock"
STATUS_LOW = "Low Stock"
STATUS_REORDER = "Reorder Required"
STATUS_CRITICAL = "Critical"

# Threshold constants (Coverage Ratio = Current Stock / Required Inventory)
THRESHOLD_SUFFICIENT = 1.00     # Current stock >= Required inventory
THRESHOLD_LOW_STOCK = 0.70      # 70% <= Stock < 100% of requirement
THRESHOLD_REORDER = 0.30        # 30% <= Stock < 70% of requirement
# Below 30% is Critical

def calculate_inventory_decisions(
    forecast_df: pd.DataFrame,
    override_safety_stock_pct: Optional[float] = None
) -> pd.DataFrame:
    """
    Apply inventory replenishment logic, stock gap analysis, and status classification.
    
    Formulas:
    1. Safety Stock = Predicted Demand * (Safety Stock % / 100)
    2. Required Inventory = Predicted Demand + Safety Stock
    3. Stock Gap = Required Inventory - Current Stock
    4. Recommended Purchase Quantity = max(Required Inventory - Current Stock, 0)
    
    Parameters:
    - forecast_df: DataFrame with predicted demand and current stock per item.
    - override_safety_stock_pct: Optional user-configured global safety stock % override.
    
    Returns:
    - pd.DataFrame: Analysis table with calculated stock metrics, statuses, and reasons.
    """
    df = forecast_df.copy()
    
    # Apply safety stock percentage (from dataset column or user override)
    if override_safety_stock_pct is not None:
        df["applied_safety_stock_pct"] = float(override_safety_stock_pct)
    else:
        df["applied_safety_stock_pct"] = df["safety_stock_percentage"]
        
    # 1. Safety stock calculation
    df["safety_stock"] = (df["predicted_demand"] * (df["applied_safety_stock_pct"] / 100.0)).round(1)
    
    # 2. Required inventory calculation
    df["required_inventory"] = (df["predicted_demand"] + df["safety_stock"]).round(1)
    
    # 3. Stock gap calculation
    df["stock_gap"] = (df["required_inventory"] - df["current_stock"]).round(1)
    
    # 4. Recommended purchase quantity
    df["recommended_purchase_quantity"] = df["stock_gap"].apply(lambda x: max(0.0, round(x, 1)))
    
    # Days of coverage remaining = Current Stock / Daily Avg Demand
    df["days_of_coverage"] = np.where(
        df["daily_avg_demand"] > 0,
        (df["current_stock"] / df["daily_avg_demand"]).round(1),
        0.0
    )
    
    # Calculate stock status and detailed explainable reasons
    statuses = []
    reasons = []
    
    for _, row in df.iterrows():
        curr = row["current_stock"]
        req = row["required_inventory"]
        gap = row["stock_gap"]
        pred = row["predicted_demand"]
        days_cov = row["days_of_coverage"]
        horizon = int(row["forecast_days"])
        
        # Coverage ratio against required inventory
        ratio = curr / req if req > 0 else 1.0
        
        if gap <= 0:
            status = "Sufficient Stock"
            surplus = round(abs(gap), 1)
            reason = (
                f"Current stock ({curr}) exceeds required inventory ({req}) by {surplus} units. "
                f"Sufficient for ~{days_cov} days of operations."
            )
        elif ratio >= THRESHOLD_LOW_STOCK:
            status = "Low Stock"
            reason = (
                f"Current stock ({curr}) covers {int(ratio*100)}% of required inventory ({req}). "
                f"Covers ~{days_cov} days. Routine reorder of {row['recommended_purchase_quantity']} units recommended."
            )
        elif ratio >= THRESHOLD_REORDER:
            status = "Reorder Required"
            reason = (
                f"Current stock ({curr}) covers only {int(ratio*100)}% of required inventory ({req}). "
                f"Stockout risk within ~{days_cov} days. Reorder {row['recommended_purchase_quantity']} units soon."
            )
        else:
            status = "Critical"
            reason = (
                f"Current stock ({curr}) covers only {int(ratio*100)}% of requirement ({req}). "
                f"Estimated stockout in < {max(1, int(days_cov))} days! Immediate emergency purchase of {row['recommended_purchase_quantity']} units required."
            )
            
        statuses.append(status)
        reasons.append(reason)
        
    df["status"] = statuses
    df["reason"] = reasons
    
    # Sort with Critical and Reorder Required at the top for immediate operational focus
    status_order = {"Critical": 0, "Reorder Required": 1, "Low Stock": 2, "Sufficient Stock": 3}
    df["status_priority"] = df["status"].map(status_order)
    df = df.sort_values(by=["status_priority", "recommended_purchase_quantity"], ascending=[True, False]).reset_index(drop=True)
    df = df.drop(columns=["status_priority"])
    
    return df

def get_kpi_metrics(df_inventory: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute headline KPI summary metrics for the main dashboard display.
    """
    total_items = len(df_inventory)
    sufficient_count = int((df_inventory["status"] == "Sufficient Stock").sum())
    low_stock_count = int((df_inventory["status"] == "Low Stock").sum())
    reorder_count = int((df_inventory["status"] == "Reorder Required").sum())
    critical_count = int((df_inventory["status"] == "Critical").sum())
    total_purchase_qty = round(float(df_inventory["recommended_purchase_quantity"].sum()), 1)
    
    return {
        "total_items": total_items,
        "sufficient_count": sufficient_count,
        "low_stock_count": low_stock_count,
        "reorder_count": reorder_count,
        "critical_count": critical_count,
        "total_purchase_quantity": total_purchase_qty
    }

def filter_inventory_by_status(df_inventory: pd.DataFrame, statuses: List[str]) -> pd.DataFrame:
    """
    Filter inventory DataFrame by a list of statuses.
    """
    if not statuses:
        return df_inventory
    return df_inventory[df_inventory["status"].isin(statuses)]

