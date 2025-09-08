#here is the ground structure for the functions used in the web app

from datetime import datetime, time  # Used for combining and computing time differences
# calculate hours worked per day
def calculate_daily_hours(start_time: time, end_time: time) -> float:
    start_dt = datetime.combine(datetime.today(), start_time) #Combines today's date with the provided start and end times to create full datetime objects.
    end_dt = datetime.combine(datetime.today(), end_time)
    duration = (end_dt - start_dt).total_seconds() / 3600
    return duration if duration > 0 else 0


def set_personal_settings():
    # hourly wage, weekly target hours, working days
    pass

def add_time_entry():
    # date, start/end time, break, notes
    pass

def calculate_overtime():
    # check overtime above
    pass

def calculate_earnings():
    # compute earnings based on hourly wage
    pass

def save_data():
    # write data to JSON or CSV
    pass

def load_data():
    # read data from JSON or CSV
    pass

def summarize_weekly_hours():
    # total hours for each week
    pass

def summarize_monthly_hours():
    # total hours for each month
    pass

def prepare_chart_data():
    # create data structures for plotting charts (optional)
    pass