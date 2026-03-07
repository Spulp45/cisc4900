# units.py

MPS_TO_MPH = 2.23694
MPS_TO_KMH = 3.6
METERS_TO_MILES = 0.000621371
METERS_TO_KM = 0.001
METERS_TO_FEET = 3.28084


def format_speed(value, units) -> str:
    if value is None:
        return "0"

    if units == "imperial":
        return f"{value * MPS_TO_MPH:.2f} mph"
    return f"{value * MPS_TO_KMH:.2f} km/h"

def format_distance(value, units) -> str:
    if value is None:
        return "0"

    if units == "imperial":
        return f"{value * METERS_TO_MILES:.2f} miles"
    return f"{value * METERS_TO_KM:.2f} km"

def format_elevation(value, units) -> str:
    if value is None:
        return "0"

    if units == "imperial":
        return f"{value * METERS_TO_FEET:.0f} ft"
    return f"{value:.0f} m"

def format_time(seconds: float) -> str:
    total_seconds = int(round(seconds))  # round to nearest second
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
