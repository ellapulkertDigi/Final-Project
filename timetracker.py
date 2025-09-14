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
    save_weekly_hours_history_gsheet
)

# 1. Passwortschutz
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

check_password()

st.title("Time Tracker")

# 2. Google Sheets Verbindung aufbauen
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

# Hauptdatenblatt (Entries)
sheet = client.open("timetracker-data").sheet1  # Passe ggf. den Namen an!

# Settings- und WeeklyHistory-Blätter holen
settings_sheet = client.open("timetracker-data").worksheet("Settings")
weekly_sheet = client.open("timetracker-data").worksheet("WeeklyHistory")

# 3. Settings & WeeklyHistory laden
settings = load_settings_gsheet(settings_sheet)
whist = load_weekly_hours_history_gsheet(weekly_sheet)

estimated_weekly_hours = settings.get("estimated_weekly_hours", 40)
job_name = settings.get("default_job_name", "")
hourly_wage = settings.get("default_hourly_wage", 0.0)

# 4. Markup für die aktiven Einstellungen
st.markdown(
    f"<span style='color:green; font-weight:bold;'>"
    f"Active job: {job_name}   |   "
    f"Hourly wage: {hourly_wage:.2f} €   |   "
    f"Estimated weekly hours: {estimated_weekly_hours}"
    f"</span>",
    unsafe_allow_html=True
)


# 5. Eingabe-Felder
work_date = st.date_input("Date")
start_time = st.time_input("Start Time")
end_time = st.time_input("End Time")
break_minutes = st.number_input("Break (minutes)", min_value=0, value=0)

# 6. Settings sidebar (unverändert)
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
        save_settings_gsheet(settings, settings_sheet)

        from datetime import date

        year, week, _ = date.today().isocalendar()
        week_id = f"{year}-{week:02d}"
        whist[week_id] = new_weekly_hours
        save_weekly_hours_history_gsheet(whist, weekly_sheet)

        st.success("Settings saved!")
        st.rerun()

# 7. Eintrag speichern
if st.button("Calculate Entry"):
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

# 8. Einträge laden (Google Sheet)
entries_df = load_entries_gsheet(sheet)

# 9. Datums- und Zeitspalten korrekt umwandeln
entries_df["Date"] = pd.to_datetime(entries_df["Date"], errors='coerce')
if "Start time" in entries_df.columns:
    entries_df["Start time"] = pd.to_datetime(entries_df["Start time"], format="%H:%M", errors="coerce")

entries_df = entries_df.sort_values(
    by=["Date", "Start time"], ascending=[False, False]
).reset_index(drop=True)

from datetime import date, timedelta

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

# ======= THIS WEEK =======
def safe_float(x):
    try:
        return float(x)
    except Exception:
        return float('nan')

def safe_sum(series):
    vals = pd.to_numeric(series, errors="coerce")
    result = vals.sum()
    try:
        return float(result)
    except Exception:
        return 0.0

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
    # Summen robust berechnen
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


# ========== SUMMARIES & CHART ==========

def style_entries_table(df):
    return df.style.format({
        "Hours worked": "{:.2f}",
        "Earnings": "{:.2f} €"
    })

def style_summary_table_with_overtime(df):
    return df.style.format({
        "Total hours": "{:.2f}",
        "Total earnings": "{:.2f} €",
        "Estimated weekly hours": "{:.2f}",
        "Overtime": "{:.2f}"
    })

def style_summary_table(df):
    return df.style.format({
        "Total hours": "{:.2f}",
        "Total earnings": "{:.2f} €"
    })

if not entries_df.empty:
    entries_df["Hours worked"] = pd.to_numeric(entries_df["Hours worked"], errors="coerce").round(2)
    entries_df["Earnings"] = pd.to_numeric(entries_df["Earnings"], errors="coerce").round(2)

    # WEEKLY SUMMARY
    weekly_summary = summarize_weekly_hours(entries_df)
    weekly_summary["total_hours"] = weekly_summary["total_hours"].round(2)
    weekly_summary["total_earnings"] = weekly_summary["total_earnings"].round(2)
    weekly_summary = calculate_overtime(weekly_summary, settings, whist)

    # Chart: aufsteigend sortieren
    weekly_summary_chart = weekly_summary.sort_values(
        by=["Year", "Week"], ascending=[True, True]
    ).reset_index(drop=True)

    # Für Tabelle: absteigend sortieren
    weekly_summary = weekly_summary.sort_values(
        by=["Year", "Week"], ascending=[False, False]
    ).reset_index(drop=True)

    # Rename columns for table display
    weekly_summary = weekly_summary.rename(columns={
        "total_hours": "Total hours",
        "total_earnings": "Total earnings",
        "Estimated weekly hours": "Estimated weekly hours",
        "Overtime": "Overtime"
    })

    # MONTHLY SUMMARY
    monthly_summary = summarize_monthly_hours(entries_df)
    monthly_summary["total_hours"] = monthly_summary["total_hours"].round(2)
    monthly_summary["total_earnings"] = monthly_summary["total_earnings"].round(2)
    monthly_summary = monthly_summary.sort_values(by="Month", ascending=False).reset_index(drop=True)

    monthly_summary = monthly_summary.rename(columns={
        "total_hours": "Total hours",
        "total_earnings": "Total earnings"
    })

    # CHART
    st.subheader("4 Weeks Overview")
    fig = plot_weekly_hours(weekly_summary_chart)
    st.plotly_chart(fig, use_container_width=True)

    # WEEKLY SUMMARY (EXPANDER)
    with st.expander("Weekly summary"):
        st.write(style_summary_table_with_overtime(weekly_summary))

    # MONTHLY SUMMARY (EXPANDER)
    with st.expander("Monthly summary"):
        st.write(style_summary_table(monthly_summary))

    # ALL ENTRIES (EXPANDER)
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
            # Mülleimer-Button: Lösche Zeile im Google Sheet (idx+2, da Header Zeile 1)
            if cols[5].button("🗑️", key=f"del_{idx}"):
                sheet.delete_rows(idx + 2, idx + 2)
                st.rerun()
                break

else:
    st.info("No entries yet. Add some time entries to see summaries!")





