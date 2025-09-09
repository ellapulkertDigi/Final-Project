# here will be the streamlit script using the ground structure from timetrackerfunctions.py

import streamlit as st
from timetrackerfunctions import calculate_daily_hours, calculate_earnings, validate_entry

st.title("Time Tracker") #this will show the header for the app

job_name = st.text_input("Job Name")
work_date = st.date_input("Date")
start_time = st.time_input("Start Time")
end_time = st.time_input("End Time")
break_minutes = st.number_input("Break (minutes)", min_value=0, value=0)
hourly_wage = st.number_input("Hourly Wage (€)", min_value=0.0, value=0.0, format="%.2f")


if st.button("Calculate Entry"):
    error_msg = validate_entry(start_time, end_time, break_minutes, hourly_wage)
    if error_msg:
        st.error(error_msg)
    else:
        duration = calculate_daily_hours(start_time, end_time, break_minutes)
        earnings = calculate_earnings(duration, hourly_wage)
        st.write(f"Worked hours: {duration:.2f}")
        st.write(f"Earnings: {earnings:.2f} €")

