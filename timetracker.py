# here will be the streamlit script using the ground structure from timetrackerfunctions.py

import streamlit as st
import pandas as pd
from timetrackerfunctions import (
    calculate_daily_hours,
    calculate_earnings,
    validate_entry,
    save_entry,
    load_entries,
    summarize_weekly_hours,
    summarize_monthly_hours,
)

st.title("Time Tracker") #this will show the header for the app

job_name = st.text_input("Job Name")
work_date = st.date_input("Date")
start_time = st.time_input("Start Time")
end_time = st.time_input("End Time")
break_minutes = st.number_input("Break (minutes)", min_value=0, value=0)
hourly_wage = st.number_input("Hourly Wage (€)", min_value=0.0, value=0.0, format="%.2f")


# Button and validation
if st.button("Calculate Entry"):
    error_msg = validate_entry(start_time, end_time, break_minutes, hourly_wage)
    if error_msg:
        st.error(error_msg)
    else:
        duration = calculate_daily_hours(start_time, end_time, break_minutes)
        earnings = calculate_earnings(duration, hourly_wage)
        entry = {
            "Job Name": job_name,
            "Date": work_date,
            "Start time": start_time.strftime("%H:%M"),
            "End time": end_time.strftime("%H:%M"),
            "Break minutes": break_minutes,
            "Hours worked": round(duration, 2),
            "Earnings": earnings
        }
        save_entry(entry)
        st.success(f"Worked hours: {duration:.2f}\nEarnings: {earnings:.2f} €")

# Show saved entries as table
entries_df = load_entries()

def style_entries_table(df):
    # Format "Hours worked" with two decimals and "Earnings" with two decimals plus euro sign
    return df.style.format({
        "Hours worked": "{:.2f}",
        "Earnings": "{:.2f} €"
    })

def style_summary_table(df):
    # Format summary columns with two decimals and add euro sign to earnings
    return df.style.format({
        "Total hours": "{:.2f}",
        "Total earnings": "{:.2f} €"
    })

if not entries_df.empty:
    # Round numbers for safety
    entries_df["Hours worked"] = entries_df["Hours worked"].round(2)
    entries_df["Earnings"] = entries_df["Earnings"].round(2)

    weekly_summary = summarize_weekly_hours(entries_df)
    monthly_summary = summarize_monthly_hours(entries_df)

    # Round using the original column names
    weekly_summary["total_hours"] = weekly_summary["total_hours"].round(2)
    weekly_summary["total_earnings"] = weekly_summary["total_earnings"].round(2)
    monthly_summary["total_hours"] = monthly_summary["total_hours"].round(2)
    monthly_summary["total_earnings"] = monthly_summary["total_earnings"].round(2)

    # Rename columns for display
    weekly_summary = weekly_summary.rename(columns={
        "total_hours": "Total hours",
        "total_earnings": "Total earnings"
    })
    monthly_summary = monthly_summary.rename(columns={
        "total_hours": "Total hours",
        "total_earnings": "Total earnings"
    })

    st.subheader("All entries")
    st.write(style_entries_table(entries_df))

    st.subheader("Weekly summary")
    st.write(style_summary_table(weekly_summary))

    st.subheader("Monthly summary")
    st.write(style_summary_table(monthly_summary))
else:
    st.info("No entries yet. Add some time entries to see summaries!")