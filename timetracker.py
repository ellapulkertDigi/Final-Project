# here will be the streamlit script using the ground structure from timetrackerfunctions.py

import streamlit as st
from timetrackerfunctions import calculate_daily_hours #the function that calculates the working hours

st.title("Time Tracker") #this will show the header for the app

job_name = st.text_input("Job Name")
work_date = st.date_input("Date")
start_time = st.time_input("Start Time")
end_time = st.time_input("End Time")

if st.button("Calculate Entry"):
    # calculate_daily_hours will be implemented in timetrackerfunctions.py
    duration = calculate_daily_hours(start_time, end_time)
    st.write(f"Worked hours: {duration:.2f}")
