"""
Dataset Generator for AI-Powered Hotel Food Inventory & Demand Forecasting System.
Generates realistic historical consumption, restocking, and inventory data for 365 days.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Fix seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_hotel_dataset(output_path: str = None, num_days: int = 365) -> pd.DataFrame:
    """
    Generate realistic hotel inventory and daily consumption data.
    
    Parameters:
    - output_path: file path to save the generated CSV.
    - num_days: number of consecutive historical days (default: 365 days).
    
    Returns:
    - pd.DataFrame containing the complete dataset.
    """
    start_date = datetime(2025, 1, 1)
    
    # 14 representative food items across 6 core hotel kitchen categories
    items_config = [
        # item_name, category, base_usage, safety_stock_pct, restock_batch, min_stock_threshold
        ("Basmati Rice", "Grains", 28.0, 15, 300, 70),
        ("Wheat Flour", "Grains", 22.0, 15, 250, 60),
        ("Fresh Chicken", "Meat", 38.0, 20, 220, 80),
        ("Fresh Mutton", "Meat", 18.0, 20, 120, 45),
        ("Fresh Milk", "Dairy", 45.0, 25, 200, 90),
        ("Farm Eggs", "Dairy", 85.0, 20, 500, 180),
        ("Fresh Paneer", "Dairy", 16.0, 25, 100, 40),
        ("Red Onions", "Vegetables", 32.0, 20, 250, 75),
        ("Potatoes", "Vegetables", 26.0, 20, 220, 65),
        ("Fresh Tomatoes", "Vegetables", 24.0, 25, 180, 60),
        ("Cooking Oil", "Pantry", 18.0, 15, 200, 50),
        ("Granulated Sugar", "Pantry", 14.0, 15, 150, 40),
        ("Fresh Bananas", "Fruits", 16.0, 20, 120, 40),
        ("Mixed Spices", "Spices", 7.0, 15, 60, 20),
    ]
    
    records = []
    
    for item_name, category, base_usage, safety_stock_pct, restock_batch, reorder_trigger in items_config:
        # Initial stock to start the year comfortably
        current_stock = float(restock_batch)
        monthly_req = int(round(base_usage * 30))
        
        for day_idx in range(num_days):
            current_date = start_date + timedelta(days=day_idx)
            day_of_week = current_date.weekday()  # 0=Mon, 4=Fri, 5=Sat, 6=Sun
            month = current_date.month
            
            # 1. Day of week multiplier (hotel buffets & banquets spike on weekends)
            if day_of_week in [4, 5, 6]:  # Fri, Sat, Sun
                dow_multiplier = np.random.uniform(1.30, 1.65)
            elif day_of_week == 0:  # Monday is typically lighter
                dow_multiplier = np.random.uniform(0.75, 0.90)
            else:  # Tue, Wed, Thu
                dow_multiplier = np.random.uniform(0.90, 1.10)
                
            # 2. Seasonal / Festival multiplier (hotel occupancy increases during holidays/festivals)
            # Oct, Nov, Dec (Diwali, Wedding season, Christmas/New Year) and Summer (May, June)
            if month in [10, 11, 12]:
                seasonal_multiplier = np.random.uniform(1.15, 1.35)
            elif month in [5, 6]:
                seasonal_multiplier = np.random.uniform(1.05, 1.20)
            else:
                seasonal_multiplier = 1.0
                
            # 3. Occasional banquet / corporate party demand spike (5% probability)
            event_spike = 1.40 if np.random.random() < 0.05 else 1.0
            
            # Calculate raw daily consumption with random noise
            noise = np.random.normal(0, base_usage * 0.08)
            daily_usage = (base_usage * dow_multiplier * seasonal_multiplier * event_spike) + noise
            daily_usage = max(1.0, round(daily_usage, 1))
            
            # Restock check from previous cycle
            # On the last few days of the year, let's control restock so we get a realistic mix
            # of Sufficient, Low Stock, Reorder Required, and Critical items for dashboard demonstration.
            is_final_week = day_idx >= (num_days - 7)
            
            previous_stock = current_stock
            
            # Deduct usage
            daily_usage = min(previous_stock, daily_usage)
            current_stock = max(0.0, round(previous_stock - daily_usage, 1))
            
            records.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "food_item": item_name,
                "category": category,
                "previous_stock": round(previous_stock, 1),
                "current_stock": round(current_stock, 1),
                "daily_usage": round(daily_usage, 1),
                "monthly_requirement": monthly_req,
                "safety_stock_percentage": safety_stock_pct
            })
            
            # Decide if restocking happens for the next day
            # If in the final week, modulate some items to demonstrate different stock statuses
            if is_final_week:
                # Specific items kept low on purpose for demonstration:
                # Fresh Chicken -> Critical
                # Fresh Milk -> Reorder Required
                # Fresh Paneer -> Low Stock
                # Basmati Rice -> Sufficient Stock
                if item_name in ["Fresh Chicken"] and day_idx >= (num_days - 3):
                    # Do not restock, let it become critical
                    pass
                elif item_name in ["Fresh Milk", "Tomatoes"] and day_idx >= (num_days - 2):
                    # Do not restock, let it become reorder required
                    pass
                elif item_name in ["Fresh Paneer", "Cooking Oil"] and day_idx >= (num_days - 1):
                    pass
                elif current_stock < reorder_trigger:
                    current_stock += restock_batch
            else:
                if current_stock < reorder_trigger:
                    # Replenishment batch arrives overnight
                    current_stock += restock_batch
                    
    df = pd.DataFrame(records)
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Dataset successfully created with {len(df)} rows at: {output_path}")
        
    return df

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_csv = os.path.join(current_dir, "sample_hotel_inventory.csv")
    generate_hotel_dataset(output_path=target_csv)
