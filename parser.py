import gpxpy
import xml.etree.ElementTree as ET
from datetime import datetime
from trackPoint import trackPoint

def read_GPX(filename):
    try:
        with open(filename, 'r') as file:
            gpx_file = open(filename)
            gpx = gpxpy.parse(gpx_file)
            xml = gpx.to_xml()
        with open("output.gpx", 'w') as f:
            f.write(xml)
            
    except FileNotFoundError:
        print(f"File '{filename}' was not found.")

def process_GPX(filename):
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







