## Documentation Entry – Project Thoughts & Preparation

When I started thinking about my final project, I wanted to solve a real problem for myself: tracking my working hours, overtime, and earnings in a way that existing tools don’t fully cover for me.

My first idea was to write a simple Python script. But then I realized I want to actually **use** this tool on my phone or anywhere. So I researched how to turn Python code into a web app and found **Streamlit**, which looks easy to use and perfect for connecting Python logic to a web interface.

---

### What I Planned

- The core functions I’d need (like saving time entries, calculating overtime, etc.)
- How to keep personal settings flexible (hourly wage, working days, etc.)
- How to store data (JSON or CSV)
- How Streamlit can help build the UI

---

### Preparing for the Presentation Helped Me

- Clarify my project’s scope
- Define which challenges to expect
- Split my work into clear steps:
  - first build the Python logic
  - then wrap it in Streamlit

---

**Next step:** I’ll start coding the core logic before moving on to building the Streamlit interface.

--- 

## Project Setup

**Workflow Change:**
Originally, I planned to finish the core logic before building the UI. However, I created a minimal Streamlit interface early to immediately test my functions, get quick feedback, and make development more efficient. 

**Goal:**  
Build a simple time tracking web app for recording working hours and calculating daily totals.

**Steps completed:**
- Initialized repository and created basic folder structure.
- Set up Python virtual environment (`venv`), installed Streamlit, created `requirements.txt`.
- Implemented minimal Streamlit UI: job name, date, start/end time, calculate button.
- Connected UI to calculation function (`calculate_daily_hours`).
- Tested app locally: input fields and time calculation are working.

**Definition of Done:**  
`streamlit run timetracker.py` displays input fields and shows the calculated duration.

---

## Features and Error Handling Update

**Goal:**
Enable users to enter break time and hourly wage, and calculate both worked hours and daily earnings with input validation.

**Steps completed:**
- Added input fields for break (minutes) and hourly wage to the Streamlit UI.
- Extended `calculate_daily_hours` to subtract breaks and always return a non-negative value.
- Created `calculate_earnings` to compute daily wage.
- Added `validate_entry` for input validation (checks for missing values, logical errors).
- Implemented user-friendly error messages in the UI.

**Definition of Done:**
The app calculates both worked hours and earnings, and displays helpful error messages for invalid or missing input.

---

## Storing and Displaying Entries

**Goal:**
Enable users to save each working time entry, and display a table with all entries in the app.

**Steps completed:**
- Implemented save_entry to store each entry as a row in a CSV file.
- Implemented load_entries to load all entries from the CSV into a DataFrame.
- Displayed all saved entries as a table in the Streamlit UI.

**Definition of Done:**
- New entries are appended to a CSV file.
- All entries are visible in the app, with readable column names.
- Table updates automatically after each new entry.

---

## Table Formatting & Data Presentation

**Goal:**
Improve readability of the entries table by rounding hours to two decimal places and appending the euro sign to the earnings. Weekly and monthly summaries are also presented with formatted columns.

**Steps completed:**
- Used Pandas Styler to format "Hours worked" with two decimal places and "Earnings" with a euro sign.
- Applied similar formatting to summary tables (weekly and monthly totals).
- Updated UI to use st.write() for styled DataFrames instead of st.dataframe().

**Definition of Done:**
All tables in the app now display properly formatted values, improving clarity and professionalism.

---

## Weekly and Monthly Summary

**Goal:**
Allow users to view total working hours and earnings summarized by week and by month.

**Steps completed:**
- Implemented `summarize_weekly_hours` and `summarize_monthly_hours` functions to group and sum data.
- Displayed weekly and monthly summaries as tables in the Streamlit UI.
- Used formatted column headers for better readability.

**Definition of Done:**
Users see at a glance whether they worked overtime in any given week, with total overtime hours displayed.

---

## User Settings

**Goal:**
Enable users to set and update default values (job name, hourly wage, estimated weekly hours) via a settings file and UI section.

**Steps completed:**
- Created a `settings.json` file to store default preferences.
- Added functions to load and save settings.
- Built a sidebar settings form in Streamlit for users to update their preferences, with persistent storage.
- Updated main input fields to use these default values.

**Definition of Done:**
Settings are loaded at startup, can be changed via the UI, and changes persist across sessions.

---

## Overtime Calculation
**Goal:**
Automatically calculate and display weekly overtime based on user-defined estimated weekly hours.

**Steps completed:**
- Added `estimated_weekly_hours` to settings and settings UI.
- Implemented `calculate_overtime` to add an "Overtime" column to the weekly summary.
- Displayed overtime in the weekly summary, formatted for clarity.

**Definition of Done:**
Users see at a glance whether they worked overtime in any given week, with total overtime hours displayed.

---

## Password Protection

**Goal:** Restrict access to the app for privacy and security, especially when the app is deployed publicly (e.g., on Streamlit Cloud).

**Steps completed:**

- Implemented a simple password protection at the very start of the Streamlit app.
- On startup, the user is prompted to enter a password. Only after successful authentication is the main interface displayed.
- The password is not stored in plain text, but as a SHA256 hash in the `.streamlit/secrets.toml` file. During login, the entered password is hashed and compared to this value.
- The secrets file is excluded from version control via `.gitignore` to keep the password confidential.

**Definition of Done:**
The app requests a password before showing any content. Only users with the pre-set password can access the main interface.

**Known Limitation:**
This approach only allows for **a single, pre-defined password** that must be set in advance by the admin or developer. There is **no account management or the possibility for end users to set their own password or have individual profiles.** All users share the same access and settings. If true multi-user support with personalized data is required, a more advanced authentication and user management system would be needed.
