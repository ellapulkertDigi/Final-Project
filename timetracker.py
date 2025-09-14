import streamlit as st
import pandas as pd
import hashlib
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, timedelta

from timetrackerfunctions import (
    calculate_daily_hours,
    calculate_earnings,
    validate_entry,
    summarize_weekly_hours,
    summarize_monthly_hours,
    calculate_overtime,
    plot_weekly_hours,
    fmt_time,
    load_settings_gsheet,
    save_settings_gsheet,
    load_entries_gsheet,
    save_entry_gsheet,
    load_weekly_hours_history_gsheet,
    save_weekly_hours_history_gsheet,
    safe_float,
    safe_sum,
    style_summary_table_with_overtime,
    style_summary_table
)

def check_password():
    """
    Simple password protection for the Streamlit app.
    Stores authentication status in session_state.
    Stops execution if the entered password is wrong.
    """
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

# Authenticate user before loading the app
check_password()

# App title
st.title("Time Tracker")

# Connect to Google Sheets
"""
Set up Google Sheets client using credentials stored in Streamlit secrets.
Access three worksheets: entries (main), settings, and weekly hours history.
"""
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

sheet = client.open("timetracker-data").sheet1
settings_sheet = client.open("timetracker-data").worksheet("Settings")
weekly_sheet = client.open("timetracker-data").worksheet("WeeklyHistory")

# Load settings and weekly hour targets
"""
Retrieve app settings (default job, wage, target hours) and weekly hour history from Google Sheets.
"""
settings = load_settings_gsheet(settings_sheet)
whist = load_weekly_hours_history_gsheet(weekly_sheet)

estimated_weekly_hours = settings.get("estimated_weekly_hours", 40)
job_name = settings.get("default_job_name", "")
hourly_wage = settings.get("default_hourly_wage", 0.0)

# Display current settings at the top of the app
st.markdown(
    f"<span style='color:green; font-weight:bold;'>"
    f"Active job: {job_name}   |   "
    f"Hourly wage: {hourly_wage:.2f} €   |   "
    f"Estimated weekly hours: {estimated_weekly_hours}"
    f"</span>",
    unsafe_allow_html=True
)

# Input fields for new work entry
"""
Collect user input for a new work entry: date, start time, end time, and break duration.
"""
work_date = st.date_input("Date")
start_time = st.time_input("Start Time")
end_time = st.time_input("End Time")
break_minutes = st.number_input("Break (minutes)", min_value=0, value=0)

# Sidebar: Settings form
"""
Provide a sidebar form for editing and saving default job name, hourly wage, and estimated weekly hours.
Updates settings and weekly hour history in Google Sheets.
"""
st.sidebar.header("Settings")
with st.sidebar.form("settings_form"):
    new_job_name = st.text_input("Default job name", value=settings.get("default_job_name", ""))
    new_hourly_wage = st.number_input(
        "Default hourly wage (€)",
        min_value=0.0,
        value=settings.get("default_hourly_wage", 0.0),
        step=0.5,
        format="%.2f"
    )
    # this is needed so that the user can have several different "overtime settings" for different weeks
    new_weekly_hours = st.number_input(
        "Estimated weekly hours",
        min_value=1.0,
        value=float(settings.get("estimated_weekly_hours", 40)),
        step=0.5
    )
    save_btn = st.form_submit_button("Save settings")
    if save_btn:
        settings["default_job_name"] = new_job_name
        settings["default_hourly_wage"] = new_hourly_wage
        settings["estimated_weekly_hours"] = new_weekly_hours
        save_settings_gsheet(settings, settings_sheet)

        year, week, _ = date.today().isocalendar()
        week_id = f"{year}-{week:02d}"
        whist[week_id] = new_weekly_hours
        save_weekly_hours_history_gsheet(whist, weekly_sheet)

        st.success("Settings saved!")
        st.rerun()

# Save new entry to Google Sheets
"""
Button to validate and save a new work entry.
Shows error messages for invalid input and success message after saving.
"""
if st.button("Save Entry"):
    error_msg = validate_entry(start_time, end_time, break_minutes, hourly_wage)
    if error_msg:
        st.error(error_msg)
    else:
        duration = calculate_daily_hours(start_time, end_time, break_minutes)
        earnings = calculate_earnings(duration, hourly_wage)
        entry = {
            "Job Name": job_name,
            "Date": str(work_date),
            "Start time": start_time.strftime("%H:%M"),
            "End time": end_time.strftime("%H:%M"),
            "Break minutes": break_minutes,
            "Hours worked": round(duration, 2),
            "Earnings": round(earnings, 2)
        }
        save_entry_gsheet(entry, sheet)
        st.success(f"Worked hours: {duration:.2f}\nEarnings: {earnings:.2f} €")
        st.rerun()
st.caption('To delete an entry, go to **All entries**.')

# Load and preprocess all work entries
"""
Read all entries from Google Sheets, convert date/time columns,
and sort entries by date and start time (descending).
"""
entries_df = load_entries_gsheet(sheet)
entries_df["Date"] = pd.to_datetime(entries_df["Date"], errors='coerce')
if "Start time" in entries_df.columns:
    entries_df["Start time"] = pd.to_datetime(entries_df["Start time"], format="%H:%M", errors="coerce")
entries_df = entries_df.sort_values(
    by=["Date", "Start time"], ascending=[False, False]
).reset_index(drop=True)

# Weekly overview: calendar-style display for current week
"""
Show a grid with each weekday, displaying job, times, hours, and earnings for each day.
Summarize total hours and earnings for the current week.
"""
today = date.today()
year_now, week_now, _ = today.isocalendar()
mask_this_week = (
    entries_df["Date"].dt.isocalendar().year == year_now
) & (
    entries_df["Date"].dt.isocalendar().week == week_now
)
entries_this_week = entries_df[mask_this_week].copy()

weekday_today = today.weekday()  # Monday=0
monday = today - timedelta(days=weekday_today)
weekdays = [monday + timedelta(days=i) for i in range(7)]
weekday_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

st.subheader("This Week")
if not entries_this_week.empty:
    cols = st.columns(7)
    for col, wd, label in zip(cols, weekdays, weekday_labels):
        col.markdown(f"**{label}<br>{wd.strftime('%d.%m.')}**", unsafe_allow_html=True)
        day_entries = entries_this_week[entries_this_week["Date"].dt.date == wd]
        if not day_entries.empty:
            for _, row in day_entries.iterrows():
                start = fmt_time(row['Start time'])
                end = fmt_time(row['End time'])
                hours = safe_float(row['Hours worked'])
                earnings = safe_float(row['Earnings'])
                job = row['Job Name']

                if start and end:
                    time_str = f"{start}–{end}"
                elif start:
                    time_str = f"{start}"
                elif end:
                    time_str = f"{end}"
                else:
                    time_str = ""

                col.markdown(
                    f"<b>{job}</b><br>"
                    f"{time_str}<br>"
                    f"⏰ {hours:.2f}h<br>"
                    f"💶 {earnings:.2f}€",
                    unsafe_allow_html=True
                )
        else:
            col.write("–")
    total_hours = safe_sum(entries_this_week["Hours worked"])
    total_earnings = safe_sum(entries_this_week["Earnings"])
    if pd.isna(total_hours):
        total_hours = 0.0
    if pd.isna(total_earnings):
        total_earnings = 0.0

    st.info(
        f"**Total this week:** {total_hours:.2f} hours   |   {total_earnings:.2f} €",
        icon="🧮"
    )
else:
    st.info("No entries for this week yet.")

# Summaries and charts: weekly and monthly
"""
Display weekly and monthly summaries of worked hours and earnings.
Show a bar chart for the last 4 weeks, expandable tables for weekly and monthly summaries,
and a full entries table with delete option.
"""
if not entries_df.empty:
    entries_df["Hours worked"] = pd.to_numeric(entries_df["Hours worked"], errors="coerce").round(2)
    entries_df["Earnings"] = pd.to_numeric(entries_df["Earnings"], errors="coerce").round(2)

    # Weekly summary (per ISO week)
    weekly_summary = summarize_weekly_hours(entries_df)
    weekly_summary["total_hours"] = weekly_summary["total_hours"].round(2)
    weekly_summary["total_earnings"] = weekly_summary["total_earnings"].round(2)
    weekly_summary = calculate_overtime(weekly_summary, settings, whist)

    # Ascending for chart, descending for table
    weekly_summary_chart = weekly_summary.sort_values(
        by=["Year", "Week"], ascending=[True, True]
    ).reset_index(drop=True)
    weekly_summary = weekly_summary.sort_values(
        by=["Year", "Week"], ascending=[False, False]
    ).reset_index(drop=True)
    weekly_summary = weekly_summary.rename(columns={
        "total_hours": "Total hours",
        "total_earnings": "Total earnings",
        "Estimated weekly hours": "Estimated weekly hours",
        "Overtime": "Overtime"
    })

    # Monthly summary
    monthly_summary = summarize_monthly_hours(entries_df)
    monthly_summary["total_hours"] = monthly_summary["total_hours"].round(2)
    monthly_summary["total_earnings"] = monthly_summary["total_earnings"].round(2)
    monthly_summary = monthly_summary.sort_values(by="Month", ascending=False).reset_index(drop=True)
    monthly_summary = monthly_summary.rename(columns={
        "total_hours": "Total hours",
        "total_earnings": "Total earnings"
    })

    # Bar chart: last 4 weeks
    st.subheader("4 Weeks Overview")
    fig = plot_weekly_hours(weekly_summary_chart)
    st.plotly_chart(fig, use_container_width=True)

    # Expanders for summaries and all entries
    with st.expander("Weekly summary"):
        st.write(style_summary_table_with_overtime(weekly_summary))

    with st.expander("Monthly summary"):
        st.write(style_summary_table(monthly_summary))

    with st.expander("All entries"):
        cols = st.columns([2, 2, 2, 2, 2, 1])
        headers = ["Date", "Start–End", "Job Name", "Hours worked", "Earnings", ""]
        for col, header in zip(cols, headers):
            col.markdown(f"**{header}**")

        for idx, row in entries_df.iterrows():
            try:
                date_str = pd.to_datetime(row["Date"]).strftime("%d.%m.%Y")
            except Exception:
                date_str = str(row["Date"])

            start_fmt = fmt_time(row['Start time'])
            end_fmt = fmt_time(row['End time'])

            if start_fmt and end_fmt:
                start_end_str = f"{start_fmt}–{end_fmt}"
            elif start_fmt:
                start_end_str = start_fmt
            elif end_fmt:
                start_end_str = end_fmt
            else:
                start_end_str = "-"

            job = row["Job Name"]
            hours = f"{row['Hours worked']:.2f} h"
            earnings = f"{row['Earnings']:.2f} €"

            cols = st.columns([2, 2, 2, 2, 2, 1])
            cols[0].write(date_str)
            cols[1].write(start_end_str)
            cols[2].write(job)
            cols[3].write(hours)
            cols[4].write(earnings)
            # Delete button: removes row in Google Sheet (idx+2 because header is row 1)
            if cols[5].button("🗑️", key=f"del_{idx}"):
                sheet.delete_rows(idx + 2, idx + 2)
                st.rerun()
                break
else:
    st.info("No entries yet. Add some time entries to see summaries!")



