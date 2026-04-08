from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
from backend import databaseFunctions
from backend import parser
from backend import units
from functools import wraps
import os
import json
import uuid



app = Flask(__name__)
app.secret_key = json.load(open("secret.json"))["SECRET_KEY"]
app.config['UPLOAD_DIRECTORY'] = json.load(open("config.json"))["UPLOAD_DIRECTORY"]
app.config['ALLOWED_EXTENSIONS'] = json.load(open("config.json"))["ALLOWED_EXTENSIONS"]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

#Temp redirect
@app.route('/')
def tempRedirect():
    if 'user_id' not in session:
            return redirect('/login')
    else:
        return redirect('/home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        result = databaseFunctions.create_user(username, password)

        if not result:
            return "Username already Exists"
        
        return redirect('/login')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        passowrd = request.form['password']

        user_id = databaseFunctions.verify_user(username, passowrd)

        if user_id is not False:
            session['user_id'] = user_id
            session['username'] = username
            return redirect('/home')
        
        return "Invalid Credentials"
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    print("CURRENTUSER: ",session.get('user_id'))
    all_rows = databaseFunctions.get_tracks(session.get('user_id'))
    return render_template('home.html', tracks=all_rows, username=session.get('username'))


@app.route('/trip/<int:track_id>')
@login_required
def trip_stats(track_id):

    data = databaseFunctions.get_gps_points(track_id,session.get('user_id'))

    return render_template(
        'trips.html',
        track=data['track'][0],
        track_points=data['track_points']
    )

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect('/home')

        file = request.files['file']

        if file.filename == "":
            return redirect('/home')

        extension = os.path.splitext(file.filename)[1].lower().lstrip('.')

        if extension not in app.config['ALLOWED_EXTENSIONS']:
            return "The file is not a valid GPX file"

        original_filename = secure_filename(file.filename)

        # Create temp file
        temp_filename = f"temp_{uuid.uuid4().hex}.{extension}"
        temp_filepath = os.path.join(app.config['UPLOAD_DIRECTORY'], temp_filename)
        original_filepath = os.path.join(app.config['UPLOAD_DIRECTORY'], file.filename)
        try:
            # Save temp file
            file.save(temp_filepath)

            # Parse file
            track = parser.getGPX(temp_filepath, original_filename, original_filepath)

            if track == parser.FILE_CORRUPTED:
                os.remove(temp_filepath)
                return f"Error processing '{original_filename}', file is likely corrupted"

            if track == parser.FILE_NOT_FOUND:
                os.remove(temp_filepath)
                return f"Error: {temp_filepath} was not found"

            # Compute hash
            track_hash = track.track_hash()

            new_filename = f"{track_hash}.{extension}"
            new_filepath = os.path.join(app.config['UPLOAD_DIRECTORY'], new_filename)

            # If file already exists, remove temp and skip rename
            if os.path.exists(new_filepath):
                os.remove(temp_filepath)
                return f"The file '{original_filename}' already exists"

            # Rename temp file to final name
            os.replace(temp_filepath, new_filepath)

            # Insert into DB also pass user_id
            result = databaseFunctions.insert_track(track, session.get('user_id'))

            if result == databaseFunctions.DUPLICATE_ERROR:
                os.remove(new_filepath)
                return f"The file '{original_filename}' already exists in the database"

            elif result == databaseFunctions.INTEGRITY_ERROR:
                os.remove(new_filepath)
                return f"Track integrity check failed for '{original_filename}'"

        except Exception as e:
            # Cleanup temp file
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
            return f"Error saving the file: {e}"

        return redirect('/home')


@app.route('/delete/<int:track_id>', methods=['POST'])
@login_required
def delete_track(track_id):

    result = databaseFunctions.delete_track_by_id(track_id, session.get('user_id'))

    if result == databaseFunctions.DELETE_ERROR:
        return f"Could not delete track {track_id}", 400
    if result == databaseFunctions.DELETE_FILE_ERROR:
        return f"Could not delete file associated with track with id: {track_id}"

    return redirect('/home')

@app.route('/allTrip')
@login_required
def all_trips():
    totals = databaseFunctions.get_totals(session.get('user_id'))

    if not totals:
        return "No data found to calculate totals", 404
    
    
    return render_template('all_trips.html', totals=totals)


# Unit toggle route
@app.route('/set_units/<unit>')
def set_units(unit):
    if unit in ['metric', 'imperial', 'raw']:
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
    unit_setting = session.get("units", "metric")
    return units.format_time(value, unit_setting)


# For running the app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)