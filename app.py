from flask import Flask, render_template, jsonify, request, redirect
import gpxpy
import sqlite3
from backend import databaseFunctions
from backend import parser
from werkzeug.utils import secure_filename

app = Flask(__name__) 

@app.route('/')
def test_page():
    track = parser.getGPX("20260205.gpx")
    test_hash = track.track_hash()

    avg = databaseFunctions.avg_speed(test_hash)

    total_seconds = databaseFunctions.duration(2)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        dur = f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        dur = f"{minutes}:{seconds:02d}"

    lats_raw = databaseFunctions.get_trackpoints(2, "lat")
    lons_raw = databaseFunctions.get_trackpoints(2, "lon")

    coords = []
    if isinstance(lats_raw, list) and isinstance(lons_raw, list):
        coords = [[lat[0], lon[0]] for lat, lon in zip(lats_raw, lons_raw)]

    return render_template('index.html', 
                           avg_speed=round(avg, 2) if avg else 0.0,
                           map_points=coords,
                           duration = dur)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if file:
        # 1. Parse the GPX data directly from the uploaded file stream
        track_obj = parser.getGPXWeb(file)
        print(f"DEBUG: Generated Hash: {track_obj.track_hash()}")
        print(f"DEBUG: Number of points parsed: {len(track_obj.lat)}")

        try:
            databaseFunctions.insert_track(track_obj)
            return redirect('/')
        except sqlite3.IntegrityError:
            # Instead of crashing, tell the user the file already exists
            return "This track has already been uploaded.", 400
                    
                            

if __name__ == '__main__':
    app.run(debug=True)


