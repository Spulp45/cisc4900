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
    if units == "metric":
        return f"{value * MPS_TO_KMH:.2f} km/h"
    if units == "raw":
        return value

def format_distance(value, units) -> str:
    if value is None:
        return "0"

    if units == "imperial":
        return f"{value * METERS_TO_MILES:.2f} miles"
    if units == 'metric':
        return f"{value * METERS_TO_KM:.2f} km"
    if units == "raw":
        return value

def format_elevation(value, units) -> str:
    if value is None:
        return "0"

    if units == "imperial":
        return f"{value * METERS_TO_FEET:.0f} ft"
    if units == "metric":
        return f"{value:.0f} m"
    if units == "raw":
        return value
def format_time(seconds: float, units) -> str:
    total_seconds = int(round(seconds))  # round to nearest second
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if units == "raw":
        return seconds
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    

