from flask import Flask, render_template, jsonify
import sqlite3
from backend import databaseFunctions
from backend import parser

app = Flask(__name__) 

@app.route('/')
def test_page():
    track = parser.getGPX("20260205.gpx")
    test_hash = track.track_hash()

    avg = databaseFunctions.avg_speed(test_hash)

    lats_raw = databaseFunctions.get_trackpoints(2, "lat")
    lons_raw = databaseFunctions.get_trackpoints(2, "lon")

    coords = []
    if isinstance(lats_raw, list) and isinstance(lons_raw, list):
        coords = [[lat[0], lon[0]] for lat, lon in zip(lats_raw, lons_raw)]

    return render_template('index.html', 
                           avg_speed=round(avg, 2) if avg else 0.0,
                           map_points=coords)


if __name__ == '__main__':
    app.run(debug=True)


