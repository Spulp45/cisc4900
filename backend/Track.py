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
    def __init__(self, name: str, length_2d: float, length_3d: float, moving_data: tuple, 
                 avg_speed: float, uphill: tuple, time_bounds: datetime, points: int):
        """
        Creates Track object.
        
        Args:
            name(str):
                Name of the track
            length_2d(float):
                2 Dimensional length altitude and longitude only
            length_3d(float):
                3 Dimensional length atitude, longitude and elevation
            moving_data(tuple):
                Tuple that contains data in the following order:
                (moving_time, stopped_time, moving_distance, stopped_distance, max_speed)
            avg_speed(float):
                Average speed of the entire track
            uphill(tuple):
                Tuple containing data in the following order:
                (uphill, downhill)
            time_bounds(datetime):
                Tuple containing data in this order: (startTime, endTime)
            points(int):
                Total number of track_points
        """
        self.name = name
        
        # Computed Data
        self.length_2d = length_2d
        self.length_3d = length_3d
        self.moving_data = moving_data
        self.avg_speed = avg_speed
        self.uphill = uphill
        self.time_bounds = time_bounds
        self.points = points

        # Counts how many times something is added to Track
        self.counter = 0

        # Parallel Arrays
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
        


    def add_point(self, lat: float, lon: float, ele:float , time: datetime, course: float, 
                  speed: float, geoidheight: float, src: str, sat: int, hdop: float,
                   vdop: float, pdop: float):
        
        """
    Adds a trackpoint to the track object and increases the counter

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


        

       