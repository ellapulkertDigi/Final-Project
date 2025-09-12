#here is the ground structure for the functions used in the web app

from datetime import datetime, time  # Used for combining and computing time differences
import pandas as pd # Pandas is used for efficient table (DataFrame) handling, grouping, and summarizing time tracking data
import os
import json

#SETTINGS
def load_settings(filename="settings.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        # Default settings if file does not exist
        return {
            "default_job_name": "",
            "default_hourly_wage": 0.0
        }

def save_settings(settings, filename="settings.json"):
    # Save settings dictionary to a JSON file
    with open(filename, "w") as f:
        json.dump(settings, f, indent=2)

#VALIDATION
def validate_entry(start_time, end_time, break_minutes, hourly_wage):
    if start_time is None or end_time is None:
        return "Please enter both start and end time."
    if end_time <= start_time:
        return "End time must be after start time."
    if break_minutes < 0:
        return "Break cannot be negative."
    if hourly_wage <= 0:
        return "Please enter an hourly wage greater than 0."
    return ""  # No error

#CALCULATION
def calculate_daily_hours(start_time: time, end_time: time, break_minutes: float = 0): # calculate hours worked per day
    start_dt = datetime.combine(datetime.today(), start_time) # Combines today's date with the provided start and end times to create full datetime objects.
    end_dt = datetime.combine(datetime.today(), end_time)
    duration = (end_dt - start_dt).total_seconds() / 3600
    duration -= break_minutes / 60  # deduct break time
    return max(duration, 0)

def calculate_earnings(hours_worked: float, hourly_wage: float) -> float: # compute earnings based on hourly wage
    return round(hours_worked * hourly_wage, 2)

def summarize_weekly_hours(df):
    # Make sure 'Date' is in datetime format
    df["Date"] = pd.to_datetime(df["Date"])
    # Create a column for ISO week number
    df["Week"] = df["Date"].dt.isocalendar().week
    # Group by week and sum up hours and earnings
    week_summary = df.groupby("Week").agg(
        total_hours=("Hours worked", "sum"),
        total_earnings=("Earnings", "sum")
    ).reset_index()
    return week_summary

def summarize_monthly_hours(df):
    df["Date"] = pd.to_datetime(df["Date"])
    # Create a column for year-month
    df["Month"] = df["Date"].dt.strftime("%Y-%m")
    # Group by month and sum up hours and earnings
    month_summary = df.groupby("Month").agg(
        total_hours=("Hours worked", "sum"),
        total_earnings=("Earnings", "sum")
    ).reset_index()
    return month_summary

#DATA SAVING AND LOADING
def save_entry(entry, filename="entries.csv"):
    # entry: dict with all fields
    df_new = pd.DataFrame([entry])
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(filename, index=False)

def load_entries(filename="entries.csv"):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=[
            "Job Name", "Date", "Start time", "End time", "Break minutes", "Hours worked", "Earnings"
        ])

def set_personal_settings():
    # hourly wage, weekly target hours, working days
    pass

def add_time_entry():
    # date, start/end time, break, notes
    pass

def calculate_overtime():
    # check overtime above
    pass

def prepare_chart_data():
    # create data structures for plotting charts (optional)
    pass