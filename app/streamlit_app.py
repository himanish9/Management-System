"""
Hotel Food Inventory Management System
B.Tech Software Engineering Project for Hotel Client Operations
Analyzes historical food consumption using dynamic monthly and weekly graphs.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pdf_parser import extract_inventory_from_pdf
from src.visualization import (
    plot_weekly_single_item,
    plot_weekly_all_items,
    plot_monthly_single_item
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Hotel Food Inventory Management System",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 24px 28px;
        border-radius: 12px;
        color: #ffffff;
        margin-bottom: 22px;
        border: 1px solid #334155;
    }
    .main-header h1 {
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0 0 6px 0;
        color: #f8fafc;
    }
    .main-header p {
        font-size: 0.92rem;
        color: #94a3b8;
        margin: 0;
    }
    .client-tag {
        display: inline-block;
        padding: 3px 10px;
        font-size: 0.72rem;
        font-weight: 600;
        border-radius: 9999px;
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stat-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    }
    .stat-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748b;
        margin-bottom: 4px;
    }
    .stat-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #0f172a;
    }
    .stat-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 3px;
    }
    .highlight-card-green {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 10px;
        padding: 16px 18px;
    }
    .highlight-card-red {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 10px;
        padding: 16px 18px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <span class="client-tag">Client: Hotel Food & Beverage Operations</span>
    <h1>🏨 Hotel Food Inventory Management System</h1>
    <p>A simple, professional system to analyze historical food inventory consumption using weekly and monthly graphs.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS & PDF DATASET UPLOAD
# -----------------------------------------------------------------------------
sample_4m_path = PROJECT_ROOT / "data" / "hotel_food_inventory_sample.pdf"
sample_3m_path = PROJECT_ROOT / "data" / "hotel_food_inventory_3months_sample.pdf"

with st.sidebar:
    st.header("📤 Upload PDF Dataset")
    st.write("Upload a PDF file containing hotel food inventory records with monthly and weekly consumption tables.")
    
    uploaded_file = st.file_uploader(
        "Choose an Inventory PDF",
        type=["pdf"],
        help="Upload the client's food inventory PDF document."
    )
    
    st.markdown("---")
    st.subheader("📥 Sample Test Datasets")
    st.caption("Pre-generated sample datasets with realistic hotel inventory data (units: kg, litres, dozen):")
    
    if sample_4m_path.exists():
        with open(sample_4m_path, "rb") as f:
            st.download_button(
                label="⬇️ Download 4-Month PDF",
                data=f.read(),
                file_name="hotel_food_inventory_sample.pdf",
                mime="application/pdf",
                help="September, October, November, December (10 items, 4 weeks each)"
            )
            
    if sample_3m_path.exists():
        with open(sample_3m_path, "rb") as f:
            st.download_button(
                label="⬇️ Download 3-Month PDF",
                data=f.read(),
                file_name="hotel_food_inventory_3months_sample.pdf",
                mime="application/pdf",
                help="September, October, November (10 items, 4 weeks each for testing dynamic months)"
            )

    use_sample = False
    sample_choice = "4-Month Dataset (Sep-Dec)"
    if uploaded_file is None:
        use_sample = st.checkbox("Use pre-loaded sample data for testing", value=True)
        if use_sample:
            sample_choice = st.radio(
                "Select Sample Dataset:",
                ["4-Month Dataset (Sep-Dec)", "3-Month Dataset (Sep-Nov)"],
                index=0
            )

    st.markdown("---")
    st.caption("Hotel Food & Beverage Management • Client Reporting Stage")

# -----------------------------------------------------------------------------
# LOAD & EXTRACT DATA FROM PDF
# -----------------------------------------------------------------------------
active_file = None
source_description = ""

if uploaded_file is not None:
    active_file = uploaded_file
    source_description = f"Uploaded PDF: `{uploaded_file.name}`"
elif use_sample:
    if sample_choice.startswith("4-Month") and sample_4m_path.exists():
        active_file = str(sample_4m_path)
        source_description = "Pre-loaded 4-Month Sample Dataset (Sep, Oct, Nov, Dec)"
    elif sample_choice.startswith("3-Month") and sample_3m_path.exists():
        active_file = str(sample_3m_path)
        source_description = "Pre-loaded 3-Month Sample Dataset (Sep, Oct, Nov)"
else:
    st.info("👆 Please upload an inventory PDF file in the sidebar to begin analysis.")
    st.stop()

# Extract and validate
with st.spinner("Extracting inventory tables and consumption records from PDF..."):
    success, message, datasets = extract_inventory_from_pdf(active_file)

if not success:
    st.error(f"❌ **Error Reading PDF:** {message}")
    st.info(
        "**Requirements for uploaded PDF:**\n"
        "- Must contain clear, readable tables (not image scans).\n"
        "- Tables must include columns for Food Item and Weekly Consumption (Week 1 to Week 4) or Monthly Total.\n"
        "- You can download the sample PDFs from the sidebar to inspect the expected table layout."
    )
    st.stop()

# Dynamically extract available months and food items (no hardcoding)
available_months = list(datasets.keys())
first_df = list(datasets.values())[0]

# Build map of food items and their units dynamically from the extracted data
item_unit_map = {}
for m in available_months:
    m_df = datasets[m]
    for _, row in m_df.iterrows():
        name = row["Food Item"]
        unit = row.get("Unit", "units")
        if name not in item_unit_map and pd.notna(name) and str(name).strip():
            item_unit_map[name] = unit

available_food_items = sorted(list(item_unit_map.keys()))

# -----------------------------------------------------------------------------
# MAIN APPLICATION SECTIONS (NAVIGATION TABS)
# -----------------------------------------------------------------------------
tab_upload, tab_weekly, tab_monthly = st.tabs([
    "📤 Uploaded Dataset Overview",
    "📊 Weekly Analysis",
    "📅 Monthly Analysis"
])

# =============================================================================
# TAB 1: UPLOADED DATASET OVERVIEW
# =============================================================================
with tab_upload:
    st.subheader("Dataset Extraction Summary")
    st.success(f"✅ {message}")
    st.caption(f"**Data Source:** {source_description}")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Extracted Months</div>
            <div class="stat-value">{len(available_months)}</div>
            <div class="stat-sub">{', '.join(available_months)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Monitored Food Items</div>
            <div class="stat-value">{len(available_food_items)}</div>
            <div class="stat-sub">Identified dynamically from PDF</div>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        units_found = sorted(list(set(item_unit_map.values())))
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Measurement Units</div>
            <div class="stat-value" style="font-size: 1.25rem; padding-top: 4px;">{', '.join(units_found)}</div>
            <div class="stat-sub">Preserved without cross-unit mixing</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📋 Extracted Monthly Data Tables")
    
    preview_month = st.selectbox(
        "Preview Table for Month:",
        options=available_months,
        index=0,
        key="preview_month_select"
    )
    
    preview_df = datasets[preview_month]
    st.dataframe(preview_df, use_container_width=True, hide_index=True)


# =============================================================================
# TAB 2: WEEKLY ANALYSIS
# =============================================================================
with tab_weekly:
    st.subheader("Weekly Consumption Analysis")
    st.write(
        "Analyze consumption across **Week 1**, **Week 2**, **Week 3**, and **Week 4** for any month found in the uploaded PDF. "
        "Select a specific food item to drill down, or select 'All Food Items' to view a comprehensive comparison."
    )
    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        selected_weekly_month = st.selectbox(
            "Select Month:",
            options=available_months,
            index=0,
            help="Contains only the months identified in the uploaded PDF."
        )
    with col_sel2:
        item_options = ["All Food Items"] + available_food_items
        selected_weekly_item = st.selectbox(
            "Select Food Item to Compare:",
            options=item_options,
            index=0,
            help="Select an individual item or 'All Food Items' for full comparison."
        )
        
    df_current_month = datasets[selected_weekly_month]
    weekly_cols = ["Week 1", "Week 2", "Week 3", "Week 4"]
    
    # Check if weekly columns exist for this month
    has_weekly = all(col in df_current_month.columns for col in weekly_cols)
    
    if not has_weekly:
        st.warning(f"⚠️ Weekly consumption columns (Week 1 to Week 4) were not found for {selected_weekly_month}.")
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Scenario A: Individual Food Item Selected
        if selected_weekly_item != "All Food Items":
            item_match = df_current_month[df_current_month["Food Item"] == selected_weekly_item]
            if item_match.empty:
                st.error(f"Item '{selected_weekly_item}' was not found in {selected_weekly_month} records.")
            else:
                item_row = item_match.iloc[0]
                unit = item_unit_map.get(selected_weekly_item, "units")
                
                w1_val = item_row["Week 1"]
                w2_val = item_row["Week 2"]
                w3_val = item_row["Week 3"]
                w4_val = item_row["Week 4"]
                month_total_val = item_row["Monthly Total"]
                
                # Determine peak week for this item
                week_vals = {"Week 1": w1_val, "Week 2": w2_val, "Week 3": w3_val, "Week 4": w4_val}
                peak_week = max(week_vals, key=week_vals.get)
                peak_week_val = week_vals[peak_week]
                
                # KPI Cards for Selected Item
                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-label">Selected Item</div>
                        <div class="stat-value" style="font-size: 1.25rem;">{selected_weekly_item}</div>
                        <div class="stat-sub">Unit: {unit}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with k2:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-label">{selected_weekly_month} Total Consumption</div>
                        <div class="stat-value">{month_total_val:,.1f}</div>
                        <div class="stat-sub">{unit} consumed in month</div>
                    </div>
                    """, unsafe_allow_html=True)
                with k3:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-label">Peak Consumption Week</div>
                        <div class="stat-value">{peak_week}</div>
                        <div class="stat-sub">{peak_week_val:,.1f} {unit}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with k4:
                    avg_weekly = month_total_val / 4.0
                    st.markdown(f"""
                    <div class="stat-card">
                        <div class="stat-label">Weekly Average</div>
                        <div class="stat-value">{avg_weekly:,.1f}</div>
                        <div class="stat-sub">{unit} per week</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Interactive Chart: Single Item across Week 1 to 4
                st.markdown(f"#### 📈 {selected_weekly_item} — Weekly Consumption Bar Chart ({selected_weekly_month})")
                fig_item_weekly = plot_weekly_single_item(item_row, selected_weekly_month)
                st.plotly_chart(fig_item_weekly, use_container_width=True)
                
                # Table for single item
                st.markdown(f"#### 📋 Values Table for {selected_weekly_item}")
                single_item_table = pd.DataFrame([{
                    "Food Item": selected_weekly_item,
                    "Unit": unit,
                    "Week 1": w1_val,
                    "Week 2": w2_val,
                    "Week 3": w3_val,
                    "Week 4": w4_val,
                    "Monthly Total (W1+W2+W3+W4)": month_total_val
                }])
                st.dataframe(single_item_table, use_container_width=True, hide_index=True)
                
        # Scenario B: "All Food Items" Selected
        else:
            st.markdown(f"#### 📈 Weekly Consumption Comparison (All Items) — {selected_weekly_month}")
            fig_all_weekly = plot_weekly_all_items(df_current_month, selected_weekly_month)
            st.plotly_chart(fig_all_weekly, use_container_width=True)
            
            st.markdown(f"#### 📋 {selected_weekly_month} Weekly Consumption Table (All 10 Items)")
            table_cols = ["Food Item", "Category", "Unit", "Week 1", "Week 2", "Week 3", "Week 4", "Monthly Total"]
            present_cols = [c for c in table_cols if c in df_current_month.columns]
            st.dataframe(df_current_month[present_cols], use_container_width=True, hide_index=True)


# =============================================================================
# TAB 3: MONTHLY ANALYSIS
# =============================================================================
with tab_monthly:
    st.subheader("Monthly Consumption Analysis")
    st.write(
        "Select an individual food item to view and compare its consumption across **all months available in the uploaded PDF**. "
        "The graph and table dynamically adapt to show only the months present in the uploaded dataset."
    )
    
    selected_monthly_item = st.selectbox(
        "Select Food Item for Monthly Comparison:",
        options=available_food_items,
        index=0,
        help="Select a food item to compare its monthly consumption history."
    )
    
    item_unit = item_unit_map.get(selected_monthly_item, "units")
    
    # Build dynamic monthly consumption series across available months for this item
    monthly_records = []
    for month in available_months:
        df_m = datasets[month]
        row_match = df_m[df_m["Food Item"] == selected_monthly_item]
        if not row_match.empty:
            c_val = float(row_match.iloc[0].get("Monthly Total", 0))
            monthly_records.append({"Month": month, "Consumption": c_val})
            
    df_item_monthly = pd.DataFrame(monthly_records)
    
    if df_item_monthly.empty:
        st.warning(f"No records found for '{selected_monthly_item}' across available months.")
    else:
        # Identify Month with Highest and Lowest consumption strictly from actual values
        idx_max = df_item_monthly["Consumption"].idxmax()
        idx_min = df_item_monthly["Consumption"].idxmin()
        
        highest_month = df_item_monthly.loc[idx_max, "Month"]
        highest_val = df_item_monthly.loc[idx_max, "Consumption"]
        
        lowest_month = df_item_monthly.loc[idx_min, "Month"]
        lowest_val = df_item_monthly.loc[idx_min, "Consumption"]
        
        total_item_consumed = df_item_monthly["Consumption"].sum()
        avg_month_consumed = df_item_monthly["Consumption"].mean()
        
        # Display Highlighting KPI Cards
        st.markdown("<br>", unsafe_allow_html=True)
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown(f"""
            <div class="highlight-card-red">
                <div class="stat-label" style="color: #991b1b;">🔥 Highest Consumption Month</div>
                <div class="stat-value" style="color: #991b1b; font-size: 1.45rem;">{highest_month}</div>
                <div class="stat-sub" style="color: #b91c1c;"><b>{highest_val:,.1f} {item_unit}</b> consumed</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m2:
            st.markdown(f"""
            <div class="highlight-card-green">
                <div class="stat-label" style="color: #166534;">💧 Lowest Consumption Month</div>
                <div class="stat-value" style="color: #166534; font-size: 1.45rem;">{lowest_month}</div>
                <div class="stat-sub" style="color: #15803d;"><b>{lowest_val:,.1f} {item_unit}</b> consumed</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Total Consumption ({len(available_months)} Months)</div>
                <div class="stat-value">{total_item_consumed:,.1f}</div>
                <div class="stat-sub"><b>{item_unit}</b> (Average: {avg_month_consumed:,.1f} {item_unit}/month)</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Interactive Plotly Bar Chart: Selected item across available months
        st.markdown(f"#### 📈 Monthly Consumption Chart: {selected_monthly_item}")
        fig_monthly = plot_monthly_single_item(
            df_item_monthly,
            selected_monthly_item,
            item_unit,
            highest_month=highest_month,
            lowest_month=lowest_month
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Monthly Data Table
        st.markdown(f"#### 📋 Monthly Consumption Table: {selected_monthly_item}")
        display_monthly_df = df_item_monthly.copy()
        display_monthly_df["Unit"] = item_unit
        display_monthly_df["Monthly Consumption"] = display_monthly_df["Consumption"]
        
        # Add a column indicating Highest / Lowest
        status_col = []
        for m in display_monthly_df["Month"]:
            if m == highest_month and highest_month != lowest_month:
                status_col.append("🔥 Highest Consumption")
            elif m == lowest_month and highest_month != lowest_month:
                status_col.append("💧 Lowest Consumption")
            else:
                status_col.append("Normal")
        display_monthly_df["Classification"] = status_col
        
        st.dataframe(
            display_monthly_df[["Month", "Food Item" if "Food Item" in display_monthly_df else "Month", "Monthly Consumption", "Unit", "Classification"]]
            if "Food Item" in display_monthly_df else
            display_monthly_df[["Month", "Monthly Consumption", "Unit", "Classification"]],
            use_container_width=True,
            hide_index=True
        )
