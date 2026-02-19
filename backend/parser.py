import gpxpy
import xml.etree.ElementTree as ET
from datetime import datetime
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
            gpx = gpxpy.parse(f)
    except FileNotFoundError:
        print(f"File '{filename}' was not found.")
        return []
    
    # GPX namespace definition
    ns = {"gpx": "http://www.topografix.com/GPX/1/0"}

    filename_only = os.path.basename(filename)
    #Initialize Track object using the filename as its name
    track = Track(filename_only)
    tree = ET.parse(filename)
    root = tree.getroot()
    
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

def getGPXWeb(filename: str) -> Track:
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
       
            gpx = gpxpy.parse(filename)

            filename.seek(0)

            tree = ET.parse(filename)
            root = tree.getroot()
            
    except Exception as e:
        print(f"Error parsing GPX file: {e}")
        return None
    # GPX namespace definition
    ns = {"gpx": "http://www.topografix.com/GPX/1/0"}


    # Initialize Track object using the filename as its name
    track = Track(filename.filename)
    
    # Read each data and child of the gpx file
    for trkpt in root.findall(".//gpx:trkpt", ns):
        data = {
            "lat": float(trkpt.attrib["lat"]),
            "lon": float(trkpt.attrib["lon"]),
        }

        for child in trkpt:
            tag = child.tag.split("}")[-1]
            text = child.text

            if tag == "time":
                data[tag] = datetime.fromisoformat(text.replace("Z", "+00:00"))
            elif tag in {"ele", "course", "speed", "geoidheight", "hdop", "vdop", "pdop"}:
                data[tag] = float(text)
            elif tag == "sat":
                data[tag] = int(text)
            else:
                data[tag] = text
        
        # Add each parsed point to the track object
        track.add_point(
                lat=data.get("lat"),
                lon=data.get("lon"),
                ele=data.get("ele"),
                time=data.get("time"),
                course=data.get("course"),
                speed=data.get("speed"),
                geoidheight=data.get("geoidheight"),
                src=data.get("src"),
                sat=data.get("sat"),
                hdop=data.get("hdop"),
                vdop=data.get("vdop"),
                pdop=data.get("pdop"), 
                )

    return track
