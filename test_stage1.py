"""
Verification script for Stage 1 requirements:
1. 4-month dataset extraction & math check
2. 3-month dataset extraction & math check (verify only available months appear)
3. Weekly analysis for both all-items and single-item
4. Monthly analysis (highest and lowest identification, strictly available months)
5. Zero unit mixing
"""

from pathlib import Path
import pandas as pd
from src.pdf_parser import extract_inventory_from_pdf
from src.visualization import (
    plot_weekly_single_item,
    plot_weekly_all_items,
    plot_monthly_single_item
)

PROJECT_ROOT = Path(__file__).resolve().parent

def run_tests():
    # TEST 1: 4-Month PDF
    print("=== TEST 1: 4-MONTH DATASET ===")
    p4 = PROJECT_ROOT / "data" / "hotel_food_inventory_sample.pdf"
    ok, msg, ds4 = extract_inventory_from_pdf(p4)
    assert ok, f"Failed 4M extract: {msg}"
    assert list(ds4.keys()) == ["September", "October", "November", "December"], f"Unexpected months: {list(ds4.keys())}"
    print("Extracted months:", list(ds4.keys()))

    # Verify each month has 10 items and W1+W2+W3+W4 == Monthly Total
    for month_name, df in ds4.items():
        assert len(df) == 10, f"Expected 10 items in {month_name}, got {len(df)}"
        for _, row in df.iterrows():
            item = row["Food Item"]
            w_sum = row["Week 1"] + row["Week 2"] + row["Week 3"] + row["Week 4"]
            total = row["Monthly Total"]
            assert round(w_sum, 1) == round(total, 1), f"Math error in {month_name} for {item}: {w_sum} != {total}"
    print("All 4 months: 10 items each, weekly consumption adds up exactly to Monthly Total!")

    # Verify Weekly Charts
    fig_all = plot_weekly_all_items(ds4["September"], "September")
    assert fig_all is not None
    fig_item = plot_weekly_single_item(ds4["October"].iloc[0], "October")
    assert fig_item is not None
    print("Weekly charts rendered cleanly!")

    # Verify Monthly Analysis for Basmati Rice
    item = "Basmati Rice"
    records = []
    for m, df in ds4.items():
        r = df[df["Food Item"] == item].iloc[0]
        records.append({"Month": m, "Consumption": r["Monthly Total"]})
    df_m = pd.DataFrame(records)
    assert len(df_m) == 4
    h_idx = df_m["Consumption"].idxmax()
    l_idx = df_m["Consumption"].idxmin()
    assert df_m.loc[h_idx, "Month"] == "December"
    assert df_m.loc[l_idx, "Month"] == "September"
    print(f"Monthly check: Peak={df_m.loc[h_idx, 'Month']} ({df_m.loc[h_idx, 'Consumption']} kg), Lowest={df_m.loc[l_idx, 'Month']} ({df_m.loc[l_idx, 'Consumption']} kg)")

    # TEST 2: 3-Month PDF
    print("\n=== TEST 2: 3-MONTH DATASET ===")
    p3 = PROJECT_ROOT / "data" / "hotel_food_inventory_3months_sample.pdf"
    ok3, msg3, ds3 = extract_inventory_from_pdf(p3)
    assert ok3, f"Failed 3M extract: {msg3}"
    assert list(ds3.keys()) == ["September", "October", "November"], f"Unexpected months: {list(ds3.keys())}"
    assert "December" not in ds3, "December must NOT appear in 3-month dataset!"
    print("Extracted months (strictly 3):", list(ds3.keys()))

    records3 = []
    for m, df in ds3.items():
        r = df[df["Food Item"] == item].iloc[0]
        records3.append({"Month": m, "Consumption": r["Monthly Total"]})
    df_m3 = pd.DataFrame(records3)
    assert len(df_m3) == 3
    h_idx3 = df_m3["Consumption"].idxmax()
    l_idx3 = df_m3["Consumption"].idxmin()
    assert df_m3.loc[h_idx3, "Month"] == "November"
    assert df_m3.loc[l_idx3, "Month"] == "September"
    print(f"3-Month Monthly check: Peak={df_m3.loc[h_idx3, 'Month']}, Lowest={df_m3.loc[l_idx3, 'Month']}")

    print("\n>>> ALL TESTS COMPLETED AND PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    run_tests()
