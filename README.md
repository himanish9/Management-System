# 🏨 Hotel Food Inventory Management System

A clean, professional Python and Streamlit web application designed for a hotel client to analyze historical food inventory and consumption using weekly and monthly graphs.

---

## 📌 1. Project Context & Purpose

- **Role:** B.Tech Software Engineering student developing a project for a hotel client.
- **Client:** Hotel Food & Beverage Operations Department.
- **Purpose:** Analyze historical food consumption using interactive monthly and weekly graphs, providing clear operational visibility into kitchen demand patterns without unnecessary complexity.

---

## 🚀 2. Stage 1 Features (Current Scope)

### 📄 First Page — PDF Dataset Upload
- Clean, professional first page where users can upload an inventory PDF file.
- **Sample Datasets Included:**
  - `data/hotel_food_inventory_sample.pdf`: Formal cover page + 4 months of verified data (**September, October, November, December**).
  - `data/hotel_food_inventory_3months_sample.pdf`: Formal cover page + 3 months of verified data (**September, October, November**) to validate dynamic month detection.
- **Dataset Specifications:**
  - **10 Primary Hotel Food Commodities:**
    - *Basmati Rice (kg)*
    - *Wheat Flour (kg)*
    - *Fresh Chicken (kg)*
    - *Whole Milk (litres)*
    - *Fresh Eggs (dozen)*
    - *Cooking Oil (litres)*
    - *Onions (kg)*
    - *Tomatoes (kg)*
    - *Potatoes (kg)*
    - *Paneer (kg)*
  - **Weekly Consumption for All Months:** Every single month has records for **Week 1**, **Week 2**, **Week 3**, and **Week 4**.
  - **Mathematical Consistency:** The weekly values add up exactly to the monthly consumption total (`Week 1 + Week 2 + Week 3 + Week 4 == Monthly Total`).
  - **Stock Balances:** Opening stock, purchased quantity, and closing stock are tracked (`Opening + Purchased - Consumed == Closing`).
  - **Formal Cover Page:** Includes dataset title, client details, reporting period, and description.

### 🔍 Dynamic PDF Extraction (No Hard-Coding)
- Uses `pdfplumber` to extract structured tables from uploaded PDFs.
- Dynamically detects available months from page headers and table metadata.
- Dynamically identifies food items and their respective measurement units (`kg`, `litres`, `dozen`).
- Displays descriptive error messages if the PDF is unreadable, corrupted, or missing required tabular data.
- Never invents missing data.

### 📊 Weekly Analysis Section
- **Month Dropdown:** Contains **only** the months found in the uploaded PDF.
- **Food Item Dropdown:**
  - Select an individual food item to drill down into its **Week 1, Week 2, Week 3, and Week 4** consumption.
  - Or select **"All Food Items"** to view a grouped comparison across all 10 commodities.
- **Interactive Plotly Bar Chart:** Updates automatically upon selection changes, displaying data labels and tooltips with the item's specific unit.
- **Data Table:** Formatted table showing matching values.
- **Summary Cards:** Shows Month Total, Peak Consumption Week, and Weekly Average for the selected item.

### 📅 Monthly Analysis Section
- **Food Item Dropdown:** Select any food item discovered in the dataset.
- **Dynamic Months Comparison:** Compares consumption across **all months available in the uploaded PDF** (e.g. shows 4 bars for a 4-month file, 3 bars for a 3-month file; never shows absent months).
- **Interactive Plotly Bar Chart:** Highlights the **Highest Month** (Coral Red) and **Lowest Month** (Emerald Green).
- **Monthly Consumption Table:** Lists exact consumption per month with classification tags.
- **KPI Summary Cards:** Clearly identifies the highest month, lowest month, and multi-month total consumption with correct units.
- **Zero Cross-Unit Mixing:** Never combines quantities with different units into misleading aggregate totals.

---

## 🚫 3. Important Restrictions Adhered To

The application strictly excludes:
- ❌ AI, machine learning, and future demand forecasting
- ❌ Automatic purchase recommendations or reorder triggers
- ❌ Supplier scoring or management
- ❌ User authentication, login, or registration
- ❌ Hotel room booking or reservations
- ❌ Databases, external backends, or heavy microservices

---

## 📁 4. Files Created or Modified

| File | Purpose |
| :--- | :--- |
| [app/streamlit_app.py](file:///c:/Users/sunka/OneDrive/Desktop/RetailOps%20Intelligence/hotel-food-inventory/app/streamlit_app.py) | Main Streamlit dashboard with Upload Dataset Overview, Weekly Analysis, and Monthly Analysis sections. |
| [src/pdf_parser.py](file:///c:/Users/sunka/OneDrive/Desktop/RetailOps%20Intelligence/hotel-food-inventory/src/pdf_parser.py) | Dynamic PDF extraction engine using `pdfplumber`. Extracts months, items, units, and weekly consumption without hardcoding. |
| [src/visualization.py](file:///c:/Users/sunka/OneDrive/Desktop/RetailOps%20Intelligence/hotel-food-inventory/src/visualization.py) | Interactive Plotly visualization charts for single-item weekly bars, all-item weekly grouped bars, and dynamic monthly comparisons. |
| [data/generate_sample_pdf.py](file:///c:/Users/sunka/OneDrive/Desktop/RetailOps%20Intelligence/hotel-food-inventory/data/generate_sample_pdf.py) | Generator script using `reportlab` that builds both the 4-month and 3-month sample PDF datasets with cover pages and verified math. |
| [data/hotel_food_inventory_sample.pdf](file:///c:/Users/sunka/OneDrive/Desktop/RetailOps%20Intelligence/hotel-food-inventory/data/hotel_food_inventory_sample.pdf) | Verified 4-month testing PDF (September to December, 10 items, 4 weeks each). |
| [data/hotel_food_inventory_3months_sample.pdf](file:///c:/Users/sunka/OneDrive/Desktop/RetailOps%20Intelligence/hotel-food-inventory/data/hotel_food_inventory_3months_sample.pdf) | Verified 3-month testing PDF (September to November, 10 items, 4 weeks each) for testing dynamic month detection. |
| [test_stage1.py](file:///c:/Users/sunka/OneDrive/Desktop/RetailOps%20Intelligence/hotel-food-inventory/test_stage1.py) | Automated test suite validating data extraction, mathematical consistency, weekly analysis, and monthly analysis. |
| [requirements.txt](file:///c:/Users/sunka/OneDrive/Desktop/RetailOps%20Intelligence/hotel-food-inventory/requirements.txt) | Python dependencies (`streamlit`, `pandas`, `plotly`, `pdfplumber`, `reportlab`). |

---

## 💻 5. How to Run the Application

```powershell
cd "c:\Users\sunka\OneDrive\Desktop\RetailOps Intelligence\hotel-food-inventory"
python -m streamlit run app/streamlit_app.py
```

Open your browser to:
👉 **`http://localhost:8501`**

---

## 🧪 6. How to Upload & Test the Sample PDFs

1. Open **`http://localhost:8501`** in your browser.
2. In the sidebar, you can download:
   - Click **"⬇️ Download 4-Month PDF"** to get `hotel_food_inventory_sample.pdf`.
   - Click **"⬇️ Download 3-Month PDF"** to get `hotel_food_inventory_3months_sample.pdf`.
3. Drag and drop either PDF into the **"Choose an Inventory PDF"** upload area in the sidebar.
4. The system will extract the tables dynamically, confirm the detected months and items, and update the dashboard.

---

## 📊 7. How to Use Weekly Analysis

1. Click on the **`📊 Weekly Analysis`** tab at the top.
2. In the **"Select Month"** dropdown, pick any month (only months from the uploaded PDF appear).
3. In the **"Select Food Item to Compare"** dropdown:
   - Select an individual food item (e.g. *Basmati Rice*, *Fresh Chicken*, *Whole Milk*):
     - View the 4 summary KPI cards (Month Total, Peak Week, Weekly Average).
     - View the interactive bar chart showing Week 1, Week 2, Week 3, and Week 4 with data labels and units.
     - View the values table showing exact numbers.
   - Or select **"All Food Items"**:
     - View the grouped bar chart comparing all 10 items side-by-side across the 4 weeks.
     - View the full 10-item weekly consumption table.

---

## 📅 8. How to Use Monthly Analysis

1. Click on the **`📅 Monthly Analysis`** tab at the top.
2. In the **"Select Food Item for Monthly Comparison"** dropdown, pick any food item.
3. The dashboard will display:
   - **Highest Consumption Month** card (highlighted in red with peak quantity and unit).
   - **Lowest Consumption Month** card (highlighted in green with minimum quantity and unit).
   - **Total Consumption** across the available months in the item's unit.
   - **Interactive Plotly Bar Chart:** Displays only the months present in the uploaded PDF, color-coded for quick visual recognition.
   - **Monthly Consumption Table:** Lists exact consumption per month with status tags.
