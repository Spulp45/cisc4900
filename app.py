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
    
    data = databaseFunctions.get_track_with_track_points_by_id(track_id)

    if not data['track']:
        return f"No track found with ID {track_id}", 404
    
    track = data['track'][0] 
    track_points = data['track_points']

    track_dict = track._asdict()
    track_points_list = [pt._asdict() for pt in track_points]

    return render_template(
        'index.html',
        track=track_dict,
        map_points=track_points_list
    )

                           

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


