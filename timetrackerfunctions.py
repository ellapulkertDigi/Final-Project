from datetime import datetime, time
import pandas as pd
import numpy as np
import plotly.graph_objects as go


#GOOGLE SHEETS

def load_entries_gsheet(sheet):
    """
    Load all time entries from the main Google Sheet.
    Returns a DataFrame with predefined columns if sheet is empty.
    """
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    if df.empty:
        df = pd.DataFrame(columns=[
            "Job Name", "Date", "Start time", "End time", "Break minutes", "Hours worked", "Earnings"
        ])
    return df

def save_entry_gsheet(entry, sheet):
    """
    Save a single time entry (dict) as a new row in the main Google Sheet.
    """
    row = [
        entry["Job Name"],
        entry["Date"],
        entry["Start time"],
        entry["End time"],
        entry["Break minutes"],
        entry["Hours worked"],
        entry["Earnings"]
    ]
    sheet.append_row(row)

def load_settings_gsheet(sheet):
    """
    Load app settings from the 'Settings' worksheet.
    Returns a dictionary of key-value pairs, converting numeric values.
    """
    records = sheet.get_all_records()
    settings = {row["key"]: row["value"] for row in records}
    # Convert expected numeric values
    if "default_hourly_wage" in settings:
        settings["default_hourly_wage"] = float(settings["default_hourly_wage"])
    if "estimated_weekly_hours" in settings:
        settings["estimated_weekly_hours"] = float(settings["estimated_weekly_hours"])
    return settings

def save_settings_gsheet(settings, sheet):
    """
    Save the current settings dictionary to the 'Settings' worksheet.
    Clears and overwrites the sheet.
    """
    data = [[k, v] for k, v in settings.items()]
    sheet.clear()
    sheet.append_row(["key", "value"])
    for row in data:
        sheet.append_row(row)

def load_weekly_hours_history_gsheet(weekly_sheet):
    """
    Load weekly hour targets history from the 'WeeklyHistory' worksheet.
    Returns a dictionary: {week_id: estimated_weekly_hours}.
    """
    records = weekly_sheet.get_all_records()
    return {str(row["week_id"]): float(row["estimated_weekly_hours"]) for row in records}

def save_weekly_hours_history_gsheet(whist, weekly_sheet):
    """
    Save the weekly hour targets history to the 'WeeklyHistory' worksheet.
    Overwrites the entire sheet.
    """
    weekly_sheet.clear()
    weekly_sheet.append_row(["week_id", "estimated_weekly_hours"])
    for week_id, hours in whist.items():
        weekly_sheet.append_row([week_id, hours])

#VALIDATION

def validate_entry(start_time, end_time, break_minutes, hourly_wage):
    """
    Validate user input for a new time entry.
    Returns an error message string or an empty string if input is valid.
    """
    if start_time is None or end_time is None:
        return "Please enter both start and end time."
    if end_time <= start_time:
        return "End time must be after start time."
    if break_minutes < 0:
        return "Break cannot be negative."
    if hourly_wage <= 0:
        return "Please enter an hourly wage greater than 0."
    return ""

#CALCULATION

def calculate_daily_hours(start_time: time, end_time: time, break_minutes: float = 0):
    """
    Calculate the number of hours worked in a day, minus break minutes.
    Returns 0 if the result is negative.
    """
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    duration = (end_dt - start_dt).total_seconds() / 3600
    duration -= break_minutes / 60
    return max(duration, 0)

def calculate_earnings(hours_worked: float, hourly_wage: float) -> float:
    """
    Calculate total earnings for the given number of hours and wage.
    """
    return round(hours_worked * hourly_wage, 2)


def summarize_weekly_hours(df):
    """
    Summarize total hours and earnings per week.
    Returns a DataFrame with columns: Year, Week, total_hours, total_earnings.
    """
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.isocalendar().year
    df["Week"] = df["Date"].dt.isocalendar().week
    week_summary = df.groupby(["Year", "Week"]).agg(
        total_hours=("Hours worked", "sum"),
        total_earnings=("Earnings", "sum")
    ).reset_index()
    return week_summary

def summarize_monthly_hours(df):
    """
    Summarize total hours and earnings per month
    Returns a DataFrame with columns: Month, total_hours, total_earnings.
    """
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.strftime("%Y-%m")
    month_summary = df.groupby("Month").agg(
        total_hours=("Hours worked", "sum"),
        total_earnings=("Earnings", "sum")
    ).reset_index()
    return month_summary

def calculate_overtime(weekly_summary, settings, whist):
    """
    Add columns 'Estimated weekly hours' and 'Overtime' to weekly_summary DataFrame.
    Fills with target hours from weekly history (whist) or falls back to settings.
    """
    def get_estimated_weekly_hours(year, week):
        week_id = f"{year}-{week:02d}"
        return whist.get(week_id, settings.get("estimated_weekly_hours", 40))

    overtime_list = []
    used_weekly_hours = []
    for _, row in weekly_summary.iterrows():
        year = row["Year"]
        week = row["Week"]
        est_hours = get_estimated_weekly_hours(year, week)
        used_weekly_hours.append(est_hours)
        overtime = max(row["total_hours"] - est_hours, 0)
        overtime_list.append(overtime)

    weekly_summary["Estimated weekly hours"] = used_weekly_hours
    weekly_summary["Overtime"] = overtime_list
    return weekly_summary

# VISUALIZATION

def plot_weekly_hours(weekly_summary):
    """
    Create a stacked bar chart of worked hours vs. target (overtime highlighted).
    Returns a Plotly figure.
    """
    x = [f"{int(y)}-KW{int(w):02d}" for y, w in zip(weekly_summary["Year"], weekly_summary["Week"])]
    y_hours = weekly_summary["total_hours"].values
    y_target = weekly_summary["Estimated weekly hours"].values

    normal_hours = np.minimum(y_hours, y_target)
    overtime_hours = np.maximum(y_hours - y_target, 0)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=x,
        y=normal_hours,
        name="Worked (target or less)",
        marker_color="royalblue"
    ))

    fig.add_trace(go.Bar(
        x=x,
        y=overtime_hours,
        name="Overtime",
        marker_color="red"
    ))

    fig.update_layout(
        barmode="stack",
        yaxis_title="Hours",
        xaxis_title="Week",
        legend_title="Legend",
        bargap=0.2
    )
    return fig

#UTILITIES

def safe_float(x):
    """
    Convert input to float; returns NaN on failure.
    """
    try:
        return float(x)
    except Exception:
        return float('nan')

def safe_sum(series):
    """
    Convert a pandas Series to numeric and sum it, returning 0.0 on failure.
    """
    vals = pd.to_numeric(series, errors="coerce")
    result = vals.sum()
    try:
        return float(result)
    except Exception:
        return 0.0

def fmt_time(t):
    """
    Format a time value for display as 'HH:MM'.
    Returns '' if input is None or invalid.
    """
    if pd.isnull(t) or t is None:
        return ""
    if hasattr(t, "strftime"):
        return t.strftime("%H:%M")
    t_str = str(t)
    if len(t_str) >= 5 and t_str[2] == ":":
        return t_str[:5]
    if " " in t_str and ":" in t_str:
        try:
            return t_str.split(" ")[1][:5]
        except Exception:
            pass
    if ":" in t_str:
        return t_str[-5:]
    return ""

def style_entries_table(df):
    """
    Apply standard number formatting for entries table (hours, earnings).
    """
    return df.style.format({
        "Hours worked": "{:.2f}",
        "Earnings": "{:.2f} €"
    })

def style_summary_table_with_overtime(df):
    """
    Apply formatting for weekly summary table with overtime and targets.
    """
    return df.style.format({
        "Total hours": "{:.2f}",
        "Total earnings": "{:.2f} €",
        "Estimated weekly hours": "{:.2f}",
        "Overtime": "{:.2f}"
    })

def style_summary_table(df):
    """
    Apply formatting for monthly or plain summary tables (hours, earnings).
    """
    return df.style.format({
        "Total hours": "{:.2f}",
        "Total earnings": "{:.2f} €"
    })


