from flask import Flask, render_template,request, redirect
from werkzeug.utils import secure_filename
from backend import databaseFunctions
from backend import parser
import os


app = Flask(__name__)
app.config['UPLOAD_DIRECTORY'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = ['.gpx']

@app.route('/')
def home():
    databaseFunctions.createDatabase() # Remove this later
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

    databaseFunctions.insert_track(parser.getGPX(filepath))

    return redirect('/')

@app.route('/delete/<int:track_id>', methods=['POST'])
def delete_track(track_id):
    success = databaseFunctions.delete_track_by_id(track_id)

    if not success:
        return f"Could not delete track {track_id}", 400

    return redirect('/')

@app.route('/allTrip')
def all_trips():
    # Fetch just the one total row
    summary_row = databaseFunctions.get_sql_total_only()

    if not summary_row:
        return "No data found to calculate totals", 404
    
    # Send the single row to the HTML
    return render_template('all_trips.html', track=summary_row)


#this is for hupper the user_reloader
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)



