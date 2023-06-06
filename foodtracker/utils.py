from datetime import date


def calculate_age(dob):
    today = date.today()

    # Calculate the difference between the two dates in years
    year_diff = today.year - dob.year

    # Adjust the difference based on the month and day of the dates
    if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
        year_diff -= 1

    return year_diff
