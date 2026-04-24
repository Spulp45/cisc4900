from flask import Flask, render_template, request, redirect, session, url_for, jsonify, send_from_directory, flash
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from backend import databaseFunctions
from backend import parser
from backend import units
from functools import wraps
import os
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone, timedelta



db = SQLAlchemy()


app = Flask(__name__)
app.secret_key = json.load(open("secret.json"))["SECRET_KEY"]
app.config['UPLOAD_DIRECTORY'] = json.load(open("config.json"))["UPLOAD_DIRECTORY"]
app.config['ALLOWED_EXTENSIONS'] = json.load(open("config.json"))["ALLOWED_EXTENSIONS"]
app.config['DATABASE_PATH'] = json.load(open("config.json"))["DATABASE_PATH"]

# This is to add database into frontend
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, app.config['DATABASE_PATH'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

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

    data = databaseFunctions.get_gpx_points(track_id,session.get('user_id'))

    return render_template(
        'trips.html',
        track=data['track'][0],
        track_points=data['track_points']
    )

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    
    errors = []
    success = []
    if request.method == 'POST':
        if 'files' not in request.files:
            return redirect('/home')

        files = request.files.getlist('files')

        if not files or files[0].filename == "":
            return redirect('/home')

        for file in files:
            if file.filename == "":
                continue

            extension = os.path.splitext(file.filename)[1].lower().lstrip('.')

            if extension not in app.config['ALLOWED_EXTENSIONS']:
                errors.append(f"{file.filename}The file is not a valid GPX file")
                continue

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
                    errors.append(f"Error processing '{original_filename}', file is likely corrupted")
                    continue

                if track == parser.FILE_NOT_FOUND:
                    os.remove(temp_filepath)
                    errors.append(f"Error: {temp_filepath} was not found original_filename:{original_filename}")
                    continue

                # Compute hash
                track_hash = track.track_hash()

                new_filename = f"{track_hash}.{extension}"
                new_filepath = os.path.join(app.config['UPLOAD_DIRECTORY'], new_filename)

                # If file already exists, remove temp and skip rename
               # if os.path.exists(new_filepath):
                #    os.remove(temp_filepath)
                 #   errors.append(f"{original_filename} already exists")
                  #  continue

                # Rename temp file to final name
                os.replace(temp_filepath, new_filepath)

                # Insert into DB also pass user_id
                result = databaseFunctions.insert_track(track, session.get('user_id'))

                if result == databaseFunctions.SUCCESS:
                    success.append(f"{track.name} was uploaded successfully")
                    continue

                if result == databaseFunctions.DUPLICATE_ERROR:
                    os.remove(new_filepath)
                    errors.append(f"{original_filename} already exists")
                    continue

                if result == databaseFunctions.INTEGRITY_ERROR:
                    os.remove(new_filepath)
                    errors.append(f"Track integrity check failed for '{original_filename}'")
                    continue

            except Exception as e:
                # Cleanup temp file
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                errors.append(f"Error saving the file: {e}")

        return render_template("upload_results.html",
                        errors=errors,
                        success=success)

@app.route('/download/<int:track_id>')
@login_required
def download_track(track_id):
    data = databaseFunctions.get_track(track_id, session.get('user_id'))
    
    if not data:
        return "Track not found", 404
    
    track = data[0]
    
    # Get track hash
    hash_value = track.get("track_hash")
    # Get original filename
    original_filename = track.get("filename")
    
    # Get the extension
    extension = Path(original_filename).suffix

    # Re-construct the filename + extension
    stored_file = f"{hash_value}{extension}"

    # Double check if the path exists
    if not os.path.exists(os.path.join(app.config['UPLOAD_DIRECTORY'],stored_file)):
            return f"{stored_file} File not found", 404

    return send_from_directory(
        app.config['UPLOAD_DIRECTORY'],
        stored_file,
        as_attachment= True,
        download_name= original_filename
    )
@app.route('/search')
@login_required
def search():
    try:
        q = request.args.get("q", "")
        # Pass the user_id from the session
        search_results = databaseFunctions.search_tracks_by_name(db, q, session.get('user_id'))
        return render_template("search_results.html", track=search_results)
    except Exception as e:
        print(f"!!! SEARCH ERROR: {e}")
        return str(e), 500
    
@app.route('/search_only')
@login_required
def search_only():
    try:
        q = request.args.get("q", "")
        # Pass the user_id from the session
        search_results = databaseFunctions.search_tracks_by_name(db, q, session.get('user_id'))
        return render_template("search_only.html", track=search_results)
    except Exception as e:
        print(f"!!! SEARCH ERROR: {e}")
        return str(e), 500




@app.route('/delete/<int:track_id>', methods=['POST'])
@login_required
def delete_track(track_id):

    result = databaseFunctions.delete_track_by_id(track_id, session.get('user_id'))

    if result == databaseFunctions.DELETE_ERROR:
        return f"Could not delete track {track_id}", 400
    if result == databaseFunctions.DELETE_FILE_ERROR:
        return f"Could not delete file associated with track with id: {track_id}"

    return redirect(request.referrer or '/')

@app.route('/update_description/<int:track_id>', methods=['POST'])
@login_required
def update_description(track_id):
    data = request.get_json()

    new_description = data.get('description')

    databaseFunctions.update_description(track_id, session.get('user_id'), new_description)

    return jsonify({"success": True})


@app.route('/allTrip')
@login_required
def all_trips():
    totals = databaseFunctions.get_totals(session.get('user_id'))

    if not totals:
        return "No data found to calculate totals", 404
    
    
    return render_template('all_trips.html', totals=totals)


##          COMPARISON              ##
@app.route("/compare", methods=["GET"])
@login_required
def compare_select():
    tracks = databaseFunctions.get_tracks(session.get('user_id'))
    return render_template("compare_select.html", tracks=tracks)

@app.route("/compare", methods=["POST"])
@login_required
def compare_submit():
    selected = request.form.getlist("track_ids")

    if len(selected) != 2:
        return "Please select exactly 2 tracks", 400

    return redirect(url_for(
        "compare_view",
        track1_id=selected[0],
        track2_id=selected[1]
    ))



@app.route("/compare/view")
@login_required
def compare_view():
    track1_id = request.args.get("track1_id")
    track2_id = request.args.get("track2_id")
    track1 = databaseFunctions.get_gpx_points(track1_id, session.get('user_id'))
    track2 = databaseFunctions.get_gpx_points(track2_id, session.get('user_id'))

    
    return render_template(
        "compare_view.html",
        track1=track1['track'][0],
         track2=track2['track'][0]
    )

@app.route("/stats/select")
@login_required
def stats_select():
    return render_template("stats_select.html")

##          COMPARISON  END         ##

@app.route("/stats")
@login_required
def stats():
    days = request.args.get("days", type=int)

    if days:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        tracks = databaseFunctions.get_track_w_datecutoff(session.get('user_id'), cutoff_date)
        track_ids = [track["id"] for track in tracks]

        totals_filtered = databaseFunctions.get_totals_filtered(
            session.get('user_id'),
            track_ids
        )

        return render_template(
            "stats_result.html",
            tracks=tracks,
            totals=totals_filtered,
            days=days
        )

    return redirect(url_for("stats_select"))


@app.route('/account_settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    user_id = session.get('user_id')
    user_db = databaseFunctions.get_user_by_id(user_id)[0]
    username = session.get('username')
    password_hash = user_db['password_hash']
    
    if request.method == 'POST':
        
        current_password = request.form['currentPassword']
        new_password = request.form['newPassword']
        confirm_password = request.form['confirmPassword']    

        if not check_password_hash(password_hash, current_password):
             return render_template('account_settings.html', username=username, error="Current password is incorrect")

        if new_password != confirm_password:
            return render_template('account_settings.html', username=username, error="New password does not match")
     
        result = databaseFunctions.update_user_password(user_id, new_password)

        if not result:
            return render_template('account_settings.html', username=username, error="Failed to update password, database error")
        
        return render_template('account_settings.html', username=username, error=None, success="Password updated Successfully")

    return render_template('account_settings.html', username=username, error=None, success=None)


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
    app.run(debug=True, use_reloader=True)