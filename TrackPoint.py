from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True) # Prevent accidental modification of the GPS data
class trackPoint:
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
