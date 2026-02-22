from datetime import datetime
from typing import Optional


class TrackPoint:
    """
    Represents a single GPS track point.
    """

    def __init__(self, lat: float, lon: float):
        """
        Initialize a TrackPoint, requires latitude and longitude data.

        Args:
            lat (float): Latitude of the track point.
            long (float): Longitude of the track point.

        """
        # Required Data
        self.lat = lat
        self.lon = lon

        # Optional Data
        self.ele: Optional[float] = None
        self.time: Optional[datetime] = None
        self.course: Optional[float] = None
        self.speed: Optional[float] = None
        self.geoidheight: Optional[float] = None
        self.src: Optional[str] = None
        self.sat: Optional[int] = None
        self.hdop: Optional[float] = None
        self.vdop: Optional[float] = None
        self.pdop: Optional[float] = None

    def addChild(self, tag: str, data):
        """
        If present add optional data to the trackpoint based on the tag name you give.

        Args:
            tag (str): The name of the GPS data type Examples: "sat", "time", "speed").
            data: The value that of the tag.

        """
        if tag == "ele":
            self.ele = float(data)
        elif tag == "time":
            self.time = datetime.fromisoformat(data)
        elif tag == "course":
            self.course = float(data)
        elif tag == "speed":
            self.speed = float(data)
        elif tag == "geoidheight":
            self.geoidheight = float(data)
        elif tag == "src":
            self.src = str(data)
        elif tag == "sat":
            self.sat = int(data)
        elif tag == "hdop":
            self.hdop = float(data)
        elif tag == "vdop":
            self.vdop = float(data)
        elif tag == "pdop":
            self.pdop = float(data)
