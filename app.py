from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename
from backend import databaseFunctions
from backend import parser
import os
import units


random_data = os.urandom(32)

app = Flask(__name__)
app.secret_key = random_data
app.config['UPLOAD_DIRECTORY'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = ['.gpx']


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
def upload():
    if 'file' not in request.files:
        return redirect('/')

    file = request.files['file']

    if file.filename == "":
        return redirect('/')

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in app.config['ALLOWED_EXTENSIONS']:
        return 'The file is not .gpx format'

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_DIRECTORY'], filename)
    file.save(filepath)

    track = parser.getGPX(filepath)
    
    if track == parser.FILE_CORRUPTED:
            # Try to Delete Corrupted File
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            return f"Error processing the file \'{filename}\', file is likely corrupted"

    if track == parser.FILE_NOT_FOUND:
        return f"Error {filepath} was not found."        
    
    result = databaseFunctions.insert_track(track)
        
    if result == databaseFunctions.DUPLICATE_ERROR:
           return f"The file \'{track.filename}\' already exists on the database"
    elif result == databaseFunctions.INTEGRITY_ERROR:
            return f"Track integrity check failed"
        
    return redirect('/')


@app.route('/delete/<int:track_id>', methods=['POST'])
def delete_track(track_id):
    success = databaseFunctions.delete_track_by_id(track_id)

    if not success:
        return f"Could not delete track {track_id}", 400

    return redirect('/')

@app.route('/allTrip')
def all_trips():
    totals = databaseFunctions.get_totals()

    if not totals:
        return "No data found to calculate totals", 404
    
    
    return render_template('all_trips.html', totals=totals)


# Unit toggle route
@app.route('/set_units/<unit>')
def set_units(unit):
    if unit in ['metric', 'imperial']:
        session['units'] = unit
    return redirect(request.referrer or '/')


# Template filters
@app.template_filter("speed")
def speed_filter(value):
    unit_setting = session.get("units", "metric")
    return units.format_speed(value, unit_setting)


@app.template_filter("distance")
def distance_filter(value):
    unit_setting = session.get("units", "metric")
    return units.format_distance(value, unit_setting)


@app.template_filter("elevation")
def elevation_filter(value):
    unit_setting = session.get("units", "metric")
    return units.format_elevation(value, unit_setting)

@app.template_filter("time")
def time_filter(value):
    return units.format_time(value)


# For running the app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)