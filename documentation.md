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
## Weekly Hours Bar Chart

**Goal:** Visualize the number of hours worked for each week to provide a quick overview of work trends and overtime.

**Steps completed:**
- Added a new function `plot_weekly_hours using` Plotly Express to create an interactive bar chart.
- The chart displays "Week Number" on the X-axis and "Hours Worked" on the Y-axis.
- A red dashed horizontal line indicates the user-defined overtime threshold (estimated_weekly_hours) for easy comparison.
- The chart is embedded directly in the Streamlit UI below the weekly summary table for better accessibility.

**Definition of Done:**
Users can now quickly see how much they worked in the most recent weeks and immediately recognize if their working time exceeds their weekly target.

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

---

## Weekly Overview & Multiple Entries per Day

**Goal:** Provide a "This Week" calendar view, with support for multiple work sessions per day.

**Steps completed:**
- Added a new UI block showing the current week as a calendar.
- Each day lists all entries for that date (not just one).
- Users can enter multiple work periods per day (e.g., split shifts).
- The week view automatically updates and summarizes total hours and earnings for the current week.

**Definition of Done:**
Users see a clear weekly overview and can track multiple sessions per day.

---

## Entry Deletion Feature

**Goal:**
Allow users to delete individual time entries if they made a mistake.

**Steps completed:**
- Added a delete button (trash icon) next to each entry in the "All entries" table.
- Clicking the button removes the entry from Google Sheets immediately.
- The app reloads updated data after deletion.

**Definition of Done:**
Users can remove any entry directly from the UI; changes are reflected instantly.

---

## UI and Table Improvements

**Goal:**
Make the app visually clearer and more user-friendly.

**Steps completed:**
- Improved time formatting (displaying times as HH:MM).
- Optimized table and summary layouts for clarity and readability.
- Sidebar settings are now clearer and easier to use.
- Streamlined the order of UI elements for better workflow.

**Definition of Done:**
Tables and summaries are easy to read, and all common operations are intuitive.

---

## Deploying the App on Streamlit Cloud
To make the time tracker available from anywhere, I deployed it on 
STREAMLIT CLOUD:
- The app code and requirements are pushed to GitHub.
- Secrets (Google credentials, password hash) are managed securely using Streamlit Cloud's secret storage.
- The app is launched by pointing Streamlit Cloud to timetracker.py.
- Once deployed, users can simply open the web URL, log in, and use the app from any device—no installation needed.

--- 

## Migration to Google Sheets (Cloud Storage)

**Goal:**
Make the time tracker usable from any device and location, not just locally.

**Steps completed:**
- Switched all data saving/loading from local CSV/JSON files to Google Sheets.
- Set up a Google Service Account and shared the sheet for API access.
- Updated all functions (save_entry, load_entries, settings, weekly history) to read/write directly from Google Sheets.
- This enables true "cloud" usage: entries and settings are always up-to-date, even across devices and after reinstalling.

**Definition of Done:**
All app data is now stored in Google Sheets. The app can be opened and used from any browser, anywhere.

**During the migration from local CSV/JSON storage to Google Sheets, I leveraged AI (ChatGPT) to help design and implement the connection between my Python code and the Google Sheets API. This made it much easier to solve the challenge of making my data globally accessible, as I could quickly get examples and overcome issues around authentication, API usage, and data structure. Without AI support, this cloud-based approach would have taken much longer to figure out.** -> see comments in code

--- 

## Additional Notes / Known Limitations
- No user accounts: All users share a single password and data set. For individual profiles, a more complex login system would be needed.
- No offline mode: The app requires internet access to Google Sheets.
- No undo for deletions: Deleted entries are gone immediately.
- No multi-language support: All UI text is currently in English.
- No advanced reporting/export features yet.
