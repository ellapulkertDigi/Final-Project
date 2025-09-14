
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
    load_settings,
    save_settings,
    calculate_overtime,
    plot_weekly_hours
)

import hashlib

def check_password():
    """Simple password protection for Streamlit apps."""
    def password_entered():
        if hashlib.sha256(st.session_state["pw"].encode()).hexdigest() == st.secrets["password_hash"]:
            st.session_state["authenticated"] = True
            del st.session_state["pw"]
        else:
            st.session_state["authenticated"] = False

    if "authenticated" not in st.session_state:
        st.text_input("Password", type="password", key="pw", on_change=password_entered)
        st.stop()
    elif not st.session_state["authenticated"]:
        st.text_input("Password", type="password", key="pw", on_change=password_entered)
        st.error("Wrong password. Try again.")
        st.stop()

# Call this at the very top!
check_password()

st.title("Time Tracker")

# Load settings and entries
settings = load_settings()
estimated_weekly_hours = settings.get("estimated_weekly_hours", 40)

# Hole aktuelle Einstellungen aus dem Sidebar-Formular
job_name = settings.get("default_job_name", "")
hourly_wage = settings.get("default_hourly_wage", 0.0)

# Zeige die aktiven Einstellungen grün und fett an
st.markdown(
    f"<span style='color:green; font-weight:bold;'>"
    f"Active job: {job_name}   |   "
    f"Hourly wage: {hourly_wage:.2f} €   |   "
    f"Estimated weekly hours: {estimated_weekly_hours}"
    f"</span>",
    unsafe_allow_html=True
)

# Nur noch die wirklich nötigen Felder in der Mitte:
work_date = st.date_input("Date")
start_time = st.time_input("Start Time")
end_time = st.time_input("End Time")
break_minutes = st.number_input("Break (minutes)", min_value=0, value=0)

# Settings sidebar (unverändert)
st.sidebar.header("Settings")
with st.sidebar.form("settings_form"):
    new_job_name = st.text_input("Default job name", value=settings.get("default_job_name", ""))
    new_hourly_wage = st.number_input("Default hourly wage (€)", min_value=0.0, value=settings.get("default_hourly_wage", 0.0), format="%.2f")
    new_weekly_hours = st.number_input("Estimated weekly hours", min_value=1, value=settings.get("estimated_weekly_hours", 40))
    save_btn = st.form_submit_button("Save settings")
    if save_btn:
        settings["default_job_name"] = new_job_name
        settings["default_hourly_wage"] = new_hourly_wage
        settings["estimated_weekly_hours"] = new_weekly_hours
        save_settings(settings)
        st.success("Settings saved!")
        st.rerun()

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
            "Earnings": round(earnings, 2)
        }
        save_entry(entry)
        st.success(f"Worked hours: {duration:.2f}\nEarnings: {earnings:.2f} €")


# Load and display entries
entries_df = load_entries()

def style_entries_table(df):
    # Format "Hours worked" with two decimals and "Earnings" with two decimals plus euro sign
    return df.style.format({
        "Hours worked": "{:.2f}",
        "Earnings": "{:.2f} €"
    })

def style_summary_table_with_overtime(df):
    # Format all relevant columns, including Overtime
    return df.style.format({
        "Total hours": "{:.2f}",
        "Total earnings": "{:.2f} €",
        "Overtime": "{:.2f}"
    })

def style_summary_table(df):
    # Format summary columns with two decimals and add euro sign to earnings
    return df.style.format({
        "Total hours": "{:.2f}",
        "Total earnings": "{:.2f} €"
    })

if not entries_df.empty:
    entries_df["Hours worked"] = entries_df["Hours worked"].round(2)
    entries_df["Earnings"] = entries_df["Earnings"].round(2)

    weekly_summary = summarize_weekly_hours(entries_df)
    weekly_summary["total_hours"] = weekly_summary["total_hours"].round(2)
    weekly_summary["total_earnings"] = weekly_summary["total_earnings"].round(2)
    weekly_summary = calculate_overtime(weekly_summary, estimated_weekly_hours)

    # Plot chart BEFORE renaming columns!
    st.subheader("Weekly worked hours (chart, last 4 weeks)")
    fig = plot_weekly_hours(weekly_summary, estimated_weekly_hours)
    st.plotly_chart(fig, use_container_width=True)

    # Rename columns for table display
    weekly_summary = weekly_summary.rename(columns={
        "total_hours": "Total hours",
        "total_earnings": "Total earnings",
        "Overtime": "Overtime"
    })

    monthly_summary = summarize_monthly_hours(entries_df)
    monthly_summary["total_hours"] = monthly_summary["total_hours"].round(2)
    monthly_summary["total_earnings"] = monthly_summary["total_earnings"].round(2)
    monthly_summary = monthly_summary.rename(columns={
        "total_hours": "Total hours",
        "total_earnings": "Total earnings"
    })

    st.subheader("All entries")
    st.write(style_entries_table(entries_df))

    st.subheader("Weekly summary")
    st.write(style_summary_table_with_overtime(weekly_summary))

    st.subheader("Monthly summary")
    st.write(style_summary_table(monthly_summary))
else:
    st.info("No entries yet. Add some time entries to see summaries!")

