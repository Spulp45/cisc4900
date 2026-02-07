import gpxpy
import xml.etree.ElementTree as ET
from datetime import datetime
from trackPoint import trackPoint

def getGPX(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)
            
    except FileNotFoundError:
        print(f"File '{filename}' was not found.")
        return []

    ns = {"gpx": "http://www.topografix.com/GPX/1/0"}

    tree = ET.parse(filename)
    root = tree.getroot()

    trackPoints = []

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

        trackPoints.append(trackPoint(**data))
    return trackPoints
