from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class trackPoint:
    lat: float
    lon: float
    ele: Optional[float] = None
    time: Optional[datetime] = None
    course: Optional[float] = None
    speed: Optional[float] = None
    geoidheight: Optional[float] = None
    src: Optional[str] = None
    sat: Optional[int] = None
    hdop: Optional[float] = None
    vdop: Optional[float] = None
    pdop: Optional[float] = None
