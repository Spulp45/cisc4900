import gpxpy
import xml.etree.ElementTree as ET
from backend.Track import Track
import os
from backend.TrackPoint import TrackPoint

FILE_CORRUPTED = 2
FILE_NOT_FOUND = 3


"""
GPX parser function.

This module parses a GPX file and converts each entry into a
track point object and then bundles it up into a Track object.
"""

def getGPX(filename: str) -> Track | int:
    """
    parse the GPX file by providing its name and get a Track object back

    Args:
        filename (str):
            Path to the GPX file to parse.

    Returns:
        Track | int:
            A track object containing all the parsed track points,
            or an error code if something went wrong.

    Raises:
        ValueError:
            If conversion fails for GPX point attributes.
        xml.etree.ElementTree:
            If the XML structure is invalid or corrupted.
        FileNotFoundError:
            If the specified file does not exist.
    """

    try:
        with open(filename, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)

    except gpxpy.gpx.GPXXMLSyntaxException:
        print(f"File '{filename}' is not well-formed")
        return FILE_CORRUPTED

    except FileNotFoundError:
        print(f"File '{filename}' was not found.")
        return FILE_NOT_FOUND

    length_2d = gpx.length_2d()         # float
    length_3d = gpx.length_3d()         # float
    moving_data = gpx.get_moving_data() # tuple (moving_time, stopped_time, moving_distance, stopped_distance, max_speed)
    avg_speed = moving_data.moving_distance / moving_data.moving_time # float
    uphill = gpx.get_uphill_downhill() #tuple (uphill, downhill)
    time_bounds = gpx.get_time_bounds() # datetime (start, end)
    points = gpx.get_points_no() # int
    gpxVersion = gpx.version # str

    # Initialize the track with the filename as its name and include all
    # computed data
    filename_only = os.path.basename(filename)
    track = Track(filename_only, length_2d, length_3d, moving_data, 
                  avg_speed, uphill, time_bounds, points, filename, filename_only, gpxVersion)
    
    
    # Read each data and child of the gpx file
    for trk in gpx.tracks:
        for segment in trk.segments:
            for p in segment.points:

                track_point = TrackPoint(p.latitude, p.longitude)

                if p.elevation:
                    track_point.addChild("ele", p.elevation)
                
                if p.time:
                    track_point.addChild("time", p.time)
                
                course = p.course if p.course else None
                speed = p.speed if p.speed else None

                if(course is None or speed is None) and p.extensions:
                    for ext in p.extensions:
                        for child in ext:
                            tag = child.tag.lower()
                            if "speed" in tag and speed is None:
                                try:
                                    speed = float(child.text)
                                except (TypeError, ValueError):
                                    print("TypeError or ValueError Exception in getting speed from extensions")
                                    pass
                            if "course" in tag and course is None:
                                try:
                                    course = float(child.text)
                                except (TypeError, ValueError):
                                    print("TypeError or ValueError Exception in getting course from extensions")
                                    pass
                
                track_point.addChild("course", course)
                track_point.addChild("speed", speed)

                if p.course:
                    track_point.addChild("course", p.course) 
                if p.speed:
                    track_point.addChild("speed", p.speed)
                
                if p.geoid_height:
                    track_point.addChild("geoidheight", p.geoid_height)
                
                if p.source:
                    track_point.addChild("src", p.source)
                
                if p.satellites:
                    track_point.addChild("sat", p.satellites)
                
                if p.horizontal_dilution:
                    track_point.addChild("hdop", p.horizontal_dilution)
                
                if p.vertical_dilution:
                    track_point.addChild("vdop", p.vertical_dilution)
                
                if p.position_dilution:
                    track_point.addChild("pdop",p.position_dilution)
                
                # Add each parsed point to the track_point object
                track.add_point(track_point.lat,
                        track_point.lon, 
                        track_point.ele,
                        track_point.time, 
                        track_point.course, 
                        track_point.speed,
                        track_point.geoidheight, 
                        track_point.src,
                        track_point.sat,
                        track_point.hdop,
                        track_point.vdop,
                        track_point.pdop)
                
    return track

def is_valid_gpx(filepath):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        if "gpx" in root.tag.lower():
            return True
        return False
    except ET.ParseError:
        return False

