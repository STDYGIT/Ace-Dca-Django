# resources/utils.py
import datetime

def get_target_semesters():
    today = datetime.date.today()
    year = today.year
    month = today.month

    # Odd semesters → after mid-January
    if today >= datetime.date(year, 6, 15):
        return [2, 4, 6]
    elif today >= datetime.date(year, 1, 15):
        return [1, 3, 5]
    else:
        return []

def get_current_academic_year():
    today = datetime.date.today()
    year = today.year
    return f"{year}-{year+1}" if today.month >= 3 else f"{year-1}-{year}"
