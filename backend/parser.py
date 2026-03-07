import gpxpy
import xml.etree.ElementTree as ET
from backend.Track import Track
import os
from backend.TrackPoint import TrackPoint

"""
GPX parser function.

This module parses a GPX file and converts each entry into a
track point object and then bundles it up into a Track object.
"""

def getGPX(filename: str) -> Track:
    """
    Docstring for getGPX

    Args:
        filename (str):
            Path to the GPX file to parse.

    Returns:
        Track:
            A track object containing all the parsed track points

    Raises:
        ValueError:
            If conversion fails for GPX point attributes
        xml.etree.ElementTree:
            If the XML structure is invalid or corrupted
        FileNotFoundError:
            If the specified file does not exist
    """

    try:
        with open(filename, "r", encoding="utf-8") as f:
            tree = ET.parse(filename)
            gpx = gpxpy.parse(f)
    except FileNotFoundError:
        print(f"File '{filename}' was not found.")

    length_2d = gpx.length_2d()         # float
    length_3d = gpx.length_3d()         # float
    moving_data = gpx.get_moving_data() # tuple (moving_time, stopped_time, moving_distance, stopped_distance, max_speed)
    avg_speed = moving_data.moving_distance / moving_data.moving_time # float    
    uphill = gpx.get_uphill_downhill() #tuple (uphill, downhill)
    time_bounds = gpx.get_time_bounds() # datetime (start, end)
    points = gpx.get_points_no() # int

    # Initialize the track with the filename as its name and include all
    # computed data
    filename_only = os.path.basename(filename)
    track = Track(filename_only, length_2d, length_3d, moving_data, 
                  avg_speed, uphill, time_bounds, points, filename, filename_only)
    
    

    root = tree.getroot()    
    # GPX namespace definition
    ns = {"gpx": "http://www.topografix.com/GPX/1/0"}    
    # Read each data and child of the gpx file
    for trkpt in root.findall(".//gpx:trkpt", ns):
        track_point = TrackPoint(float(trkpt.attrib['lat']),
                                 float(trkpt.attrib['lon']))
        
        for child in trkpt:
            tag = child.tag.split("}")[-1]
            text = child.text

            if tag == "time":
                track_point.addChild(tag, text)
            elif tag in {"ele", "course", "speed", "geoidheight", "hdop", "vdop", "pdop"}:
                track_point.addChild(tag, float(text))
            elif tag == "sat":
                track_point.addChild(tag, int(text))
            elif tag == "src":
                track_point.addChild(tag, str(text))
            
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

