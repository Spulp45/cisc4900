from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True) # Prevent accidental modification of the GPS data
class trackPoint:
  """
    Represents a single GPS track point.

    Attributes:
        lat (float):
            Latitude in decimal degrees.
        lon (float):
            Longitude in decimal degrees.
        ele (Optional[float]):
            Elevation in meters.
        time (Optional[datetime]):
            Timestamp of the track point.
        course (Optional[float]):
            Course over ground in degrees.
        speed (Optional[float]):
            Speed at this point.
        geoidheight (Optional[float]):
            Height of geoid above WGS84.
        src (Optional[str]):
            Source of the GPS data.
        sat (Optional[int]):
            Number of satellites used.
        hdop (Optional[float]):
            Horizontal dilution of precision.
        vdop (Optional[float]):
            Vertical dilution of precision.
        pdop (Optional[float]):
            Position dilution of precision.
    """
lat: float
lon: float
ele: Optional[float] 
time: Optional[datetime] 
course: Optional[float] 
speed: Optional[float] 
geoidheight: Optional[float] 
src: Optional[str] 
sat: Optional[int] 
hdop: Optional[float] 
vdop: Optional[float] 
pdop: Optional[float]
