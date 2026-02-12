import hashlib

class Track:
    def __init__(self, name):
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

    def add_point(self, lat, lon, ele, time, course, speed,
                  geoidheight, src, sat, hdop, vdop, pdop):
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

    def track_hash(self):
        points_str = "|".join(f"{lat},{lon},{ele},{time}" for lat, lon, ele, time in zip(self.lat, self.lon, self.ele, self.time))
        return hashlib.sha256(points_str.encode()).hexdigest()