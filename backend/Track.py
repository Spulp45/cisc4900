import hashlib
import datetime
    
class Track:
    """
    Docstring for Track
    Represents a GPS track that contains multiple trackPoints

    Stores all the information of the trackpoint attributes in
    arrays Note: All the lists length must always be equal to each other
    if not then something is going wrong

    """
    def __init__(self, name):
        """
        Creates Track object
        
        Args:
            name(str):
                Name of the track
        """
        self.name = name
        self.lat = []
        self.lon =  []
        self.ele = []
        self.time = []
        self.course = []
        self.speed = []
        self.geoidheight = []
        self.src = []
        self.sat = []
        self.hdop = []
        self.vdop = []
        self.pdop = []
        self.counter = 0


    def add_point(self, lat: float, lon: float, ele:float , time: datetime, course: float, 
                  speed: float, geoidheight: float, src: str, sat: int, hdop: float,
                   vdop: float, pdop: float):
        
        """
    Adds a trackpoint to the track object

    Args:
        lat (float): Latitude in degrees.
        lon (float): Longitude in degrees.
        ele (float): Elevation in meters.
        time (datetime): Timestamp of the trkpt.
        course (float): Course over ground in degrees.
        speed (float): Current speed in m/s.
        geoidheight (float): Height of geoid above WGS84.
        src (str): Source of GPS data.
        hdop (float): Horizontal dilution of precision.
        vdop (float): Vertical dilution of precision.
        pdop (float): Position dilution of precision.
        """

        self.lat.append(lat)
        self.lon.append(lon)
        self.ele.append(ele)
        self.time.append(time)
        self.course.append(course)
        self.speed.append(speed)
        self.geoidheight.append(geoidheight)
        self.src.append(src)
        self.sat.append(sat)
        self.hdop.append(hdop)
        self.vdop.append(vdop)
        self.pdop.append(pdop)
        self.counter += 1

    def track_hash(self):
        """
        Docstring for track_hash
        
        Compute the hash of the data of ALL trackpoints
        (not just the Track Object itself)

        Returns:
            str: Hex SHA-256 hash of the data
        """
        points_str = "|".join(f"{lat},{lon},{ele},{time}" for lat, lon, ele, time in zip(self.lat, self.lon, self.ele, self.time))
        return hashlib.sha256(points_str.encode()).hexdigest()
    
    def integrityCheck(self) -> bool:
        """
        Checks if all arrays in the track are parallel.

        Returns:
            bool: True if everything is fine, false otherwise

        
        """

        lists = [
        self.lat, self.lon, self.ele, self.time,
        self.course, self.speed, self.geoidheight,
        self.src, self.sat, self.hdop, self.vdop, self.pdop
    ]
        lengths = {len(lst) for lst in lists}

        if self.counter != lengths.pop():
            return False
        
        return True


        

       