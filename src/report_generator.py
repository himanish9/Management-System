"""
Report Generator Module
Exports structured inventory reports in CSV and Executive Purchase Order text formats.
"""

from datetime import datetime
from typing import Dict, Any
import pandas as pd

REPORT_CSV_COLUMNS = [
    "food_item",
    "category",
    "current_stock",
    "predicted_demand",
    "safety_stock",
    "required_inventory",
    "stock_gap",
    "status",
    "recommended_purchase_quantity",
    "reason"
]

def generate_csv_report(df_inventory: pd.DataFrame) -> bytes:
    """
    Format inventory decision DataFrame into exportable CSV bytes.
    
    Parameters:
    - df_inventory: Inventory analysis DataFrame.
    
    Returns:
    - bytes: CSV content encoded in utf-8.
    """
    # Select and order designated columns
    available_cols = [c for c in REPORT_CSV_COLUMNS if c in df_inventory.columns]
    report_df = df_inventory[available_cols].copy()
    
    return report_df.to_csv(index=False).encode("utf-8")

def generate_executive_summary(
    df_inventory: pd.DataFrame,
    kpi_metrics: Dict[str, Any],
    forecast_days: int,
    safety_stock_pct: float
) -> str:
    """
    Generate a formatted text executive purchase summary suitable for hotel kitchen procurement.
    
    Parameters:
    - df_inventory: Inventory analysis DataFrame.
    - kpi_metrics: Dictionary of calculated KPI counts.
    - forecast_days: Planning horizon in days.
    - safety_stock_pct: Applied safety stock percentage.
    
    Returns:
    - str: Plain text formatted executive procurement report.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    critical_items = df_inventory[df_inventory["status"] == "Critical"]
    reorder_items = df_inventory[df_inventory["status"] == "Reorder Required"]
    
    lines = [
        "=" * 70,
        "HOTEL FOOD INVENTORY & PROCUREMENT EXECUTIVE SUMMARY",
        "=" * 70,
        f"Generated At: {now_str}",
        f"Forecast Planning Horizon: {forecast_days} Days",
        f"Safety Stock Policy: {safety_stock_pct}% buffer applied",
        "-" * 70,
        "PORTFOLIO HEALTH OVERVIEW:",
        f"  Total Monitored Food Items:      {kpi_metrics.get('total_items', 0)}",
        f"  Items with Sufficient Stock:     {kpi_metrics.get('sufficient_count', 0)}",
        f"  Items in Low Stock:              {kpi_metrics.get('low_stock_count', 0)}",
        f"  Items Requiring Routine Reorder: {kpi_metrics.get('reorder_count', 0)}",
        f"  Critical Stockout Alerts:        {kpi_metrics.get('critical_count', 0)}",
        f"  Total Recommended Purchase:      {kpi_metrics.get('total_purchase_quantity', 0.0)} units",
        "=" * 70,
        ""
    ]
    
    if not critical_items.empty:
        lines.append("EMERGENCY PROCUREMENT ORDERS (CRITICAL STATUS - ACT IMMEDIATELY):")
        lines.append("-" * 70)
        for _, row in critical_items.iterrows():
            lines.append(
                f"  * {row['food_item']} ({row['category']}): Order {row['recommended_purchase_quantity']} units! "
                f"[Current: {row['current_stock']} | Required: {row['required_inventory']}]"
            )
            lines.append(f"    Notice: {row['reason']}")
        lines.append("")
        
    if not reorder_items.empty:
        lines.append("ROUTINE REORDER ITEMS (REORDER REQUIRED):")
        lines.append("-" * 70)
        for _, row in reorder_items.iterrows():
            lines.append(
                f"  * {row['food_item']} ({row['category']}): Order {row['recommended_purchase_quantity']} units "
                f"[Current: {row['current_stock']} | Required: {row['required_inventory']}]"
            )
        lines.append("")
        
    lines.append("=" * 70)
    lines.append("END OF REPORT - HOTEL FOOD INVENTORY INTELLIGENCE SYSTEM")
    lines.append("=" * 70)
    
    return "\n".join(lines)
