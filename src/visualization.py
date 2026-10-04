"""
Visualization Module for Hotel Food Inventory Management System
Provides interactive Plotly charts for:
1. Weekly Analysis (single food item or all items across Weeks 1 to 4)
2. Monthly Analysis (single food item across all available months in the uploaded PDF)
"""

from typing import List, Optional
import pandas as pd
import plotly.graph_objects as go

# Clean, professional layout theme
THEME_LAYOUT = dict(
    font=dict(family="Inter, Roboto, sans-serif", size=12),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=40, t=60, b=40),
)

WEEK_COLORS = {
    "Week 1": "#38bdf8",  # Sky Blue
    "Week 2": "#6366f1",  # Indigo
    "Week 3": "#8b5cf6",  # Purple
    "Week 4": "#ec4899",  # Rose Pink
}

def plot_weekly_single_item(item_row: pd.Series, month_name: str) -> go.Figure:
    """
    Renders a bar chart comparing Week 1 to Week 4 consumption for a single food item.
    """
    fig = go.Figure()
    
    item_name = item_row.get("Food Item", "Food Item")
    unit = item_row.get("Unit", "units")
    
    weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
    available_weeks = [w for w in weeks if w in item_row.index]
    
    values = [item_row[w] for w in available_weeks]
    bar_colors = [WEEK_COLORS.get(w, "#3b82f6") for w in available_weeks]
    
    # Custom hover and text labels
    hover_texts = [
        f"<b>{item_name}</b><br>{w}<br>Consumed: <b>{v:,.1f} {unit}</b>"
        for w, v in zip(available_weeks, values)
    ]
    
    text_labels = [f"{v:,.1f} {unit}" for v in values]
    
    fig.add_trace(go.Bar(
        x=available_weeks,
        y=values,
        marker=dict(
            color=bar_colors,
            line=dict(color="#ffffff", width=1)
        ),
        text=text_labels,
        textposition="auto",
        hovertext=hover_texts,
        hoverinfo="text"
    ))
    
    fig.update_layout(
        title=f"<b>{item_name}</b> — Weekly Consumption in {month_name}",
        xaxis_title="Week",
        yaxis_title=f"Quantity Consumed ({unit})",
        showlegend=False,
        **THEME_LAYOUT
    )
    fig.update_yaxes(gridcolor="#e2e8f0", zeroline=False)
    fig.update_xaxes(showgrid=False)
    
    return fig


def plot_weekly_all_items(df_month: pd.DataFrame, month_name: str) -> go.Figure:
    """
    Renders a grouped bar chart comparing Week 1, 2, 3, 4 across all food items in a month.
    """
    fig = go.Figure()
    
    weeks = ["Week 1", "Week 2", "Week 3", "Week 4"]
    available_weeks = [w for w in weeks if w in df_month.columns]
    
    if df_month.empty or "Food Item" not in df_month.columns or not available_weeks:
        return fig
        
    units = df_month["Unit"] if "Unit" in df_month.columns else ["units"] * len(df_month)
    categories = df_month["Category"] if "Category" in df_month.columns else [""] * len(df_month)
    
    for week in available_weeks:
        color = WEEK_COLORS.get(week, "#3b82f6")
        hover_texts = [
            f"<b>{item}</b> ({cat})<br>{week} Consumption: <b>{val:,.1f} {u}</b>"
            for item, cat, val, u in zip(df_month["Food Item"], categories, df_month[week], units)
        ]
        
        fig.add_trace(go.Bar(
            name=week,
            x=df_month["Food Item"],
            y=df_month[week],
            marker=dict(color=color, line=dict(color="#ffffff", width=0.5)),
            hovertext=hover_texts,
            hoverinfo="text"
        ))
        
    fig.update_layout(
        title=f"<b>Weekly Food Consumption Comparison — {month_name}</b>",
        barmode="group",
        xaxis_title="Food Item",
        yaxis_title="Quantity Consumed",
        xaxis_tickangle=-30,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11)
        ),
        **THEME_LAYOUT
    )
    fig.update_yaxes(gridcolor="#e2e8f0", zeroline=False)
    fig.update_xaxes(showgrid=False)
    
    return fig


def plot_monthly_single_item(
    df_item_months: pd.DataFrame,
    item_name: str,
    unit: str,
    highest_month: Optional[str] = None,
    lowest_month: Optional[str] = None
) -> go.Figure:
    """
    Renders an interactive bar chart displaying an individual food item's consumption
    across ONLY the months available in the uploaded PDF.
    Highlights the highest and lowest consumption months.
    """
    fig = go.Figure()
    
    if df_item_months.empty or "Month" not in df_item_months.columns or "Consumption" not in df_item_months.columns:
        return fig
        
    months = df_item_months["Month"].tolist()
    consumptions = df_item_months["Consumption"].tolist()
    
    # Assign distinct colors: Coral for highest, Amber for lowest, Indigo for regular
    bar_colors = []
    for m in months:
        if m == highest_month and highest_month != lowest_month:
            bar_colors.append("#ef4444")  # Coral Red for Peak/Highest
        elif m == lowest_month and highest_month != lowest_month:
            bar_colors.append("#10b981")  # Emerald Green for Lowest
        else:
            bar_colors.append("#3b82f6")  # Blue for regular
            
    hover_texts = [
        f"<b>{item_name}</b><br>Month: {m}<br>Total Consumed: <b>{c:,.1f} {unit}</b>" +
        ("<br>🔥 <i>Highest Month</i>" if m == highest_month and highest_month != lowest_month else "") +
        ("<br>💧 <i>Lowest Month</i>" if m == lowest_month and highest_month != lowest_month else "")
        for m, c in zip(months, consumptions)
    ]
    
    text_labels = [f"{c:,.1f} {unit}" for c in consumptions]
    
    fig.add_trace(go.Bar(
        x=months,
        y=consumptions,
        marker=dict(
            color=bar_colors,
            line=dict(color="#ffffff", width=1)
        ),
        text=text_labels,
        textposition="auto",
        hovertext=hover_texts,
        hoverinfo="text"
    ))
    
    # Add informative subtitle
    months_str = " → ".join(months)
    fig.update_layout(
        title=f"<b>{item_name}</b> — Monthly Consumption History ({months_str})",
        xaxis_title="Available Months",
        yaxis_title=f"Monthly Consumption ({unit})",
        showlegend=False,
        **THEME_LAYOUT
    )
    fig.update_yaxes(gridcolor="#e2e8f0", zeroline=False)
    fig.update_xaxes(showgrid=False)
    
    return fig
