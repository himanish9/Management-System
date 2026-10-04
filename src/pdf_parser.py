"""
PDF Parser Module for Hotel Food Inventory Management System
Extracts dynamic monthly inventory records and 4-week consumption data
from uploaded PDF documents using pdfplumber.
No hard-coding of months or food items.
"""

from typing import Tuple, Dict, Any, Union, List
import io
import re
from pathlib import Path
import pandas as pd
import pdfplumber

# Calendar months reference list used strictly for detection & chronological ordering
CALENDAR_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

def clean_text(text: Any) -> str:
    """Normalize text by stripping whitespace and extra line breaks."""
    if text is None:
        return ""
    return re.sub(r'\s+', ' ', str(text)).strip()

def clean_cell_value(val: Any) -> Any:
    """Convert cell string to int or float if numeric, else trimmed string."""
    if val is None:
        return None
    val_str = str(val).strip().replace(',', '')
    if val_str == "" or val_str.lower() in ["none", "nan", "-"]:
        return None
    try:
        if '.' in val_str:
            return float(val_str)
        return int(val_str)
    except ValueError:
        return str(val).strip()

def detect_month_from_text(text: str) -> Union[str, None]:
    """Dynamically detect which month is mentioned in the page text."""
    if not text:
        return None
    for month in CALENDAR_MONTHS:
        # Match whole word to avoid substring mismatches
        if re.search(rf"\b{month}\b", text, re.IGNORECASE):
            return month
    return None

def normalize_columns(columns: List[str]) -> Dict[str, str]:
    """Map raw table column headers to standardized names dynamically."""
    mapping = {}
    for col in columns:
        c = clean_text(col).lower()
        if "item" in c and ("id" in c or "code" in c or "no" in c):
            mapping[col] = "Item ID"
        elif "item" in c or "food" in c or "name" in c or "commodity" in c:
            mapping[col] = "Food Item"
        elif "cat" in c:
            mapping[col] = "Category"
        elif "unit" in c or "uom" in c:
            mapping[col] = "Unit"
        elif "open" in c:
            mapping[col] = "Opening Stock"
        elif "purchas" in c or "receiv" in c or "inward" in c:
            mapping[col] = "Purchased"
        elif re.search(r'\b(week\s*1|w1)\b', c):
            mapping[col] = "Week 1"
        elif re.search(r'\b(week\s*2|w2)\b', c):
            mapping[col] = "Week 2"
        elif re.search(r'\b(week\s*3|w3)\b', c):
            mapping[col] = "Week 3"
        elif re.search(r'\b(week\s*4|w4)\b', c):
            mapping[col] = "Week 4"
        elif "total" in c or "month" in c or "consum" in c or "usage" in c:
            mapping[col] = "Monthly Total"
        elif "clos" in c or "remain" in c or "ending" in c:
            mapping[col] = "Closing Stock"
    return mapping

def extract_inventory_from_pdf(
    file_source: Union[str, Path, io.BytesIO, bytes, Any]
) -> Tuple[bool, str, Dict[str, pd.DataFrame]]:
    """
    Extracts tabular monthly inventory data and weekly consumption records from PDF.
    
    Returns:
    - success (bool)
    - message (str)
    - datasets (dict): Month Name -> DataFrame containing extracted records.
    """
    datasets: Dict[str, pd.DataFrame] = {}
    
    # 1. Open the PDF source
    try:
        if isinstance(file_source, (str, Path)):
            pdf_file = pdfplumber.open(str(file_source))
        elif hasattr(file_source, "read"):
            file_bytes = file_source.read()
            if hasattr(file_source, "seek"):
                file_source.seek(0)
            pdf_file = pdfplumber.open(io.BytesIO(file_bytes))
        elif isinstance(file_source, bytes):
            pdf_file = pdfplumber.open(io.BytesIO(file_source))
        else:
            return False, "Unsupported file format. Please upload a valid PDF document.", {}
    except Exception as e:
        return False, f"Could not open or read the PDF file: {str(e)}. Please check if the file is corrupted or password-protected.", {}

    with pdf_file:
        if not pdf_file.pages:
            return False, "The uploaded PDF document contains no pages.", {}
            
        unnamed_month_idx = 1
        
        for page_idx, page in enumerate(pdf_file.pages):
            page_text = page.extract_text() or ""
            tables = page.extract_tables()
            if not tables:
                continue
                
            # Detect month from page text
            detected_month = detect_month_from_text(page_text)
            
            # Find the table that contains inventory data
            for table in tables:
                if not table or len(table) < 2:
                    continue
                    
                raw_headers = [clean_text(h) for h in table[0]]
                col_map = normalize_columns(raw_headers)
                standardized_headers = [col_map.get(h, h) for h in raw_headers]
                
                # Verify that this table is an inventory table (must contain 'Food Item')
                if "Food Item" not in standardized_headers:
                    continue
                    
                # Clean rows
                cleaned_rows = []
                for row in table[1:]:
                    if not any(cell and str(cell).strip() for cell in row):
                        continue
                    row_aligned = row[:len(standardized_headers)]
                    if len(row_aligned) < len(standardized_headers):
                        row_aligned.extend([None] * (len(standardized_headers) - len(row_aligned)))
                    cleaned_rows.append([clean_cell_value(c) for c in row_aligned])
                    
                if not cleaned_rows:
                    continue
                    
                df = pd.DataFrame(cleaned_rows, columns=standardized_headers)
                
                # Drop rows where Food Item is empty or None
                df = df.dropna(subset=["Food Item"])
                df = df[df["Food Item"].astype(str).str.strip() != ""]
                
                if df.empty:
                    continue
                    
                # Determine month name if not detected from page text
                month_name = detected_month
                if not month_name:
                    # Try finding month in table header or text inside the table
                    for cell in raw_headers:
                        m = detect_month_from_text(cell)
                        if m:
                            month_name = m
                            break
                if not month_name:
                    month_name = f"Month_{unnamed_month_idx}"
                    unnamed_month_idx += 1
                    
                # Ensure numeric conversion for known numerical columns
                num_cols = ["Opening Stock", "Purchased", "Week 1", "Week 2", "Week 3", "Week 4", "Monthly Total", "Closing Stock"]
                for nc in num_cols:
                    if nc in df.columns:
                        df[nc] = pd.to_numeric(df[nc], errors='coerce').fillna(0)
                
                # If Monthly Total is missing but Week 1..4 are present, compute it dynamically
                weekly_cols = ["Week 1", "Week 2", "Week 3", "Week 4"]
                if "Monthly Total" not in df.columns and all(w in df.columns for w in weekly_cols):
                    df["Monthly Total"] = df[weekly_cols].sum(axis=1)
                
                # If Unit is missing, default to empty string
                if "Unit" not in df.columns:
                    df["Unit"] = ""
                else:
                    df["Unit"] = df["Unit"].astype(str).str.strip()
                    
                datasets[month_name] = df
                # Once we find the inventory table for this page, move to the next page
                break

    # Validation
    if not datasets:
        return False, "No valid food inventory tables found in the uploaded PDF. Please ensure the PDF contains tables with food item and consumption records.", {}

    # Sort months chronologically if they belong to CALENDAR_MONTHS
    ordered_datasets = {}
    found_calendar_months = [m for m in CALENDAR_MONTHS if m in datasets]
    for m in found_calendar_months:
        ordered_datasets[m] = datasets[m]
    # Add any other non-standard month names
    for m in datasets:
        if m not in ordered_datasets:
            ordered_datasets[m] = datasets[m]
            
    months_list = list(ordered_datasets.keys())
    sample_df = list(ordered_datasets.values())[0]
    total_items = len(sample_df["Food Item"].unique())
    
    return True, f"Successfully extracted inventory data for {len(months_list)} month(s): {', '.join(months_list)} ({total_items} food items).", ordered_datasets
