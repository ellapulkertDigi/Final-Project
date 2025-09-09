# here will be the streamlit script using the ground structure from timetrackerfunctions.py

import streamlit as st
import pandas as pd
from timetrackerfunctions import calculate_daily_hours, calculate_earnings, validate_entry, save_entry, load_entries

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
            "Hours worked": duration,
            "Earnings": earnings
        }
        save_entry(entry)
        st.success(f"Worked hours: {duration:.2f}\nEarnings: {earnings:.2f} €")

# Show saved entries as table
entries_df = load_entries()
st.subheader("All entries")
st.dataframe(entries_df)
