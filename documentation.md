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
