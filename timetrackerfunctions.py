from datetime import datetime, time
import pandas as pd  # Pandas is used for efficient table (DataFrame) handling, grouping, and summarizing time tracking data
import os
import json
import plotly.express as px

# SETTINGS
def load_settings_gsheet(sheet):
    records = sheet.get_all_records()
    settings = {row["key"]: row["value"] for row in records}
    # Typumwandlung
    if "default_hourly_wage" in settings:
        settings["default_hourly_wage"] = float(settings["default_hourly_wage"])
    if "estimated_weekly_hours" in settings:
        settings["estimated_weekly_hours"] = float(settings["estimated_weekly_hours"])
    return settings

def save_settings_gsheet(settings, sheet):
    # sheet: Das "Settings"-Tabellenblatt
    data = [[k, v] for k, v in settings.items()]
    # Überschreibe ganzes Blatt
    sheet.clear()
    sheet.append_row(["key", "value"])
    for row in data:
        sheet.append_row(row)

# VALIDATION
def validate_entry(start_time, end_time, break_minutes, hourly_wage):
    if start_time is None or end_time is None:
        return "Please enter both start and end time."
    if end_time <= start_time:
        return "End time must be after start time."
    if break_minutes < 0:
        return "Break cannot be negative."
    if hourly_wage <= 0:
        return "Please enter an hourly wage greater than 0."
    return ""

# CALCULATION
def calculate_daily_hours(start_time: time, end_time: time, break_minutes: float = 0):
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    duration = (end_dt - start_dt).total_seconds() / 3600
    duration -= break_minutes / 60
    return max(duration, 0)

def calculate_earnings(hours_worked: float, hourly_wage: float) -> float:
    return round(hours_worked * hourly_wage, 2)

def summarize_weekly_hours(df):
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.isocalendar().year
    df["Week"] = df["Date"].dt.isocalendar().week
    week_summary = df.groupby(["Year", "Week"]).agg(
        total_hours=("Hours worked", "sum"),
        total_earnings=("Earnings", "sum")
    ).reset_index()
    return week_summary

def summarize_monthly_hours(df):
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.strftime("%Y-%m")
    month_summary = df.groupby("Month").agg(
        total_hours=("Hours worked", "sum"),
        total_earnings=("Earnings", "sum")
    ).reset_index()
    return month_summary



def load_weekly_hours_history_gsheet(weekly_sheet):
    """Lädt die Wochen-Historie aus dem Tabellenblatt 'WeeklyHistory'."""
    records = weekly_sheet.get_all_records()
    # Gibt ein Dict {week_id: estimated_weekly_hours}
    return {str(row["week_id"]): float(row["estimated_weekly_hours"]) for row in records}

def save_weekly_hours_history_gsheet(whist, weekly_sheet):
    """Speichert die Wochen-Historie in das Tabellenblatt 'WeeklyHistory'."""
    weekly_sheet.clear()
    weekly_sheet.append_row(["week_id", "estimated_weekly_hours"])
    for week_id, hours in whist.items():
        weekly_sheet.append_row([week_id, hours])


def calculate_overtime(weekly_summary, settings, whist):
    """
    Fügt dem weekly_summary-DataFrame die Spalten
    'Estimated weekly hours' und 'Overtime' hinzu,
    mit Sollwerten aus whist (Google Sheet).
    """
    def get_estimated_weekly_hours(year, week):
        week_id = f"{year}-{week:02d}"
        return whist.get(week_id, settings.get("estimated_weekly_hours", 40))  # fallback

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
import plotly.graph_objects as go
import numpy as np

def plot_weekly_hours(weekly_summary):
    x = [f"{int(y)}-KW{int(w):02d}" for y, w in zip(weekly_summary["Year"], weekly_summary["Week"])]
    y_hours = weekly_summary["total_hours"].values
    y_target = weekly_summary["Estimated weekly hours"].values

    # Normale Stunden: Minimum von gearbeitete Stunden und Ziel
    normal_hours = np.minimum(y_hours, y_target)
    # Overtime: Differenz (nur falls > 0, sonst 0)
    overtime_hours = np.maximum(y_hours - y_target, 0)

    fig = go.Figure()

    # Blauer Balken: bis zum Ziel
    fig.add_trace(go.Bar(
        x=x,
        y=normal_hours,
        name="Worked (target or less)",
        marker_color="royalblue"
    ))

    # Roter Balken: Overtime (gestapelt oben drauf)
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

def fmt_time(t):
    """Formatiert Uhrzeit für die Tabelle als HH:MM oder ''."""
    import pandas as pd
    if pd.isnull(t) or t is None:
        return ""
    if hasattr(t, "strftime"):
        return t.strftime("%H:%M")
    t_str = str(t)
    # Falls Format "18:30:00" oder "18:30", dann die ersten 5 Zeichen nehmen
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
