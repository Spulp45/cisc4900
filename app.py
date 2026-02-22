from flask import Flask, render_template,request, redirect
import sqlite3
from backend import databaseFunctions
from backend import parser


app = Flask(__name__) 

@app.route('/')
def home():
    all_rows = databaseFunctions.get_all_tracks()
    return render_template('home.html', tracks=all_rows)

@app.route('/trip/<int:track_id>')
def trip_stats(track_id):
    #track = parser.getGPX("testGPX/20260205.gpx")
    test_id = track_id

    avg = databaseFunctions.avg_speed(track_id)

    total_seconds = databaseFunctions.duration(track_id)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        dur = f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        dur = f"{minutes}:{seconds:02d}"

    lats_raw = databaseFunctions.get_trackpoints(track_id, "lat")
    lons_raw = databaseFunctions.get_trackpoints(track_id, "lon")

    coords = []
    if isinstance(lats_raw, list) and isinstance(lons_raw, list):
        coords = [[lat[0], lon[0]] for lat, lon in zip(lats_raw, lons_raw)]

    return render_template('index.html', 
                           avg_speed=round(avg, track_id) if avg else 0.0,
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


