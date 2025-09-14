# Time Tracker

A simple, web-based time tracking app for tracking your work hours, overtime, and earnings.

All you need is your browser – no installation required!

---

## How to Use

1. **Open the app in your browser:**  
   (https://final-project-timetrackerbyella.streamlit.app) 
  
2. **Login:**  
   - For project/demo purposes, use the password:  
     **TechBasics**

3. **Adjust your settings:**  
   - Use the sidebar to set job name, hourly wage, and estimated weekly hours
     
4. **Track your hours:**  
   - Enter the date, start/end time, and any break (in minutes)
   - Click "Save Entry" to record your work

5. **Explore your data:**  
   - See your work week as a calendar
   - View summaries for weeks and months
   - See a four-week bar chart (worked vs. target hours)
   - Browse or delete previous entries under "All entries"

---

## Features

- Works on desktop & mobile browsers
- Password protection (see above)
- All data is stored in a private Google Sheet (not visible to others)
- No installation needed – just use the web URL
- Clear summaries, overtime calculation, and interactive charts

---

## Requirements (for developers)

If you want to run the app locally or develop further, install requirements:
```bash
pip install -r requirements.txt
streamlit run timetracker.py
