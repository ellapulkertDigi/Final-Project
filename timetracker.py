
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
    new_hourly_wage = st.number_input("Default hourly wage (€)", min_value=0.0, value=settings.get("default_hourly_wage", 0.0), step=0.5, format="%.2f")
    new_weekly_hours = st.number_input("Estimated weekly hours", min_value=1.0, value=float(settings.get("estimated_weekly_hours", 40)), step=0.5)
    save_btn = st.form_submit_button("Save settings")
    if save_btn:
        settings["default_job_name"] = new_job_name
        settings["default_hourly_wage"] = new_hourly_wage
        settings["estimated_weekly_hours"] = new_weekly_hours
        save_settings(settings)

        from datetime import date
        import json, os
        year, week, _ = date.today().isocalendar()
        week_id = f"{year}-{week:02d}"
        hist_file = "weekly_hours_history.json"
        if os.path.exists(hist_file):
            with open(hist_file, "r") as f:
                whist = json.load(f)
        else:
            whist = {}
        whist[week_id] = new_weekly_hours
        with open(hist_file, "w") as f:
            json.dump(whist, f)

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

# Stelle sicher, dass Date ein datetime-Objekt ist (wichtig für korrektes Sortieren)
entries_df["Date"] = pd.to_datetime(entries_df["Date"])

# Optional: Auch nach Startzeit sortieren, falls mehrere Einträge am selben Tag
if "Start time" in entries_df.columns:
    entries_df["Start time"] = pd.to_datetime(entries_df["Start time"], format="%H:%M", errors="coerce")

# Nach Datum (und ggf. Startzeit) absteigend sortieren:
entries_df = entries_df.sort_values(
    by=["Date", "Start time"], ascending=[False, False]
).reset_index(drop=True)

st.subheader("This Week")
from datetime import date, timedelta

def fmt_time(t):
    if pd.isnull(t):
        return ""
    if hasattr(t, "strftime"):
        return t.strftime("%H:%M")
    try:
        from datetime import datetime
        return datetime.strptime(str(t), "%H:%M:%S").strftime("%H:%M")
    except Exception:
        try:
            return datetime.strptime(str(t), "%H:%M").strftime("%H:%M")
        except Exception:
            return str(t)[-5:]

# Kalenderlogik
today = date.today()
year_now, week_now, _ = today.isocalendar()
mask_this_week = (
    entries_df["Date"].dt.isocalendar().year == year_now
) & (
    entries_df["Date"].dt.isocalendar().week == week_now
)
entries_this_week = entries_df[mask_this_week].copy()

weekday_today = today.weekday()  # 0 = Montag
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
                hours = row['Hours worked']
                earnings = row['Earnings']
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
    total_hours = entries_this_week["Hours worked"].sum()
    total_earnings = entries_this_week["Earnings"].sum()
    st.info(
        f"**Total this week:** {total_hours:.2f} hours   |   {total_earnings:.2f} €",
        icon="🧮"
    )
else:
    st.info("No entries for this week yet.")


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
    weekly_summary = calculate_overtime(weekly_summary, settings)

    weekly_summary = weekly_summary.sort_values(by=["Year", "Week"], ascending=[False, False]).reset_index(drop=True)

    # Für das Chart: Chronologisch (ascending)
    weekly_summary_chart = weekly_summary.sort_values(
        by=["Year", "Week"], ascending=[True, True]
    ).reset_index(drop=True)

    # CHART anzeigen (chronologisch, alt → neu)
    st.subheader("Weekly worked hours (chart, last 4 weeks)")
    fig = plot_weekly_hours(weekly_summary_chart)
    st.plotly_chart(fig, use_container_width=True)

    # Rename columns for table display
    weekly_summary = weekly_summary.rename(columns={
        "total_hours": "Total hours",
        "total_earnings": "Total earnings",
        "Estimated weekly hours": "Estimated weekly hours",
        "Overtime": "Overtime"
    })

    monthly_summary = summarize_monthly_hours(entries_df)
    monthly_summary["total_hours"] = monthly_summary["total_hours"].round(2)
    monthly_summary["total_earnings"] = monthly_summary["total_earnings"].round(2)
    monthly_summary = monthly_summary.sort_values(by="Month", ascending=False).reset_index(drop=True)

    monthly_summary = monthly_summary.rename(columns={
        "total_hours": "Total hours",
        "total_earnings": "Total earnings"
    })

    if not entries_df.empty:
        with st.expander("Show all entries"):
            st.subheader("All entries")
            # Tabellenkopf
            cols = st.columns([2, 2, 2, 2, 2, 1])
            headers = ["Date", "Start-End", "Job Name", "Hours worked", "Earnings", ""]
            for col, header in zip(cols, headers):
                col.markdown(f"**{header}**")

            # Tabellenzeilen
            for idx, row in entries_df.iterrows():
                cols = st.columns([2, 2, 2, 2, 2, 1])
                cols[0].write(row["Date"])
                cols[1].write(f"{row['Start time']}–{row['End time']}")
                cols[2].write(row["Job Name"])
                cols[3].write(f"{row['Hours worked']} h")
                cols[4].write(f"{row['Earnings']} €")
                if cols[5].button("Delete", key=f"del_{idx}"):
                    entries_df = entries_df.drop(idx)
                    entries_df.to_csv("entries.csv", index=False)
                    st.rerun()
                    break

    st.subheader("Weekly summary")
    st.write(style_summary_table_with_overtime(weekly_summary))

    st.subheader("Monthly summary")
    st.write(style_summary_table(monthly_summary))
else:
    st.info("No entries yet. Add some time entries to see summaries!")

