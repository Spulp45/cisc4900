from flask import Flask, render_template, request, redirect, session, url_for, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy
from backend import databaseFunctions
from backend import parser
from backend import units
from functools import wraps
import zipfile
import io
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
app.config['TEMP_FOLDER'] = json.load(open("config.json"))['TEMP_FOLDER']

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

# Redirect to login if the user is not in session
@app.route('/')
def notLoggedIn():
    if 'user_id' not in session:
            return redirect('/login')
    else:
        return redirect('/home')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        result = databaseFunctions.create_user(username, password, app.config['DATABASE_PATH'])

        if not result:
            return render_template('show_msg.html',
                                    msg="Username already exists")
        
        return redirect('/login')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        passowrd = request.form['password']

        user_id = databaseFunctions.verify_user(username, passowrd, app.config['DATABASE_PATH'])

        if user_id is not False:
            session['user_id'] = user_id
            session['username'] = username
            return redirect('/home')
        
        return render_template('show_msg.html',
                               msg="Invalid Credentials")
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    all_rows = databaseFunctions.get_tracks(session.get('user_id'), app.config['DATABASE_PATH'])
    return render_template('home.html', tracks=all_rows, username=session.get('username'))


@app.route('/trip/<int:track_id>')
@login_required
def trip_stats(track_id):

    data = databaseFunctions.get_gpx_points(track_id,session.get('user_id'), app.config['DATABASE_PATH'])

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
            original_filepath = os.path.join(app.config['UPLOAD_DIRECTORY'], original_filename)

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
                result = databaseFunctions.insert_track(track, session.get('user_id'), app.config['DATABASE_PATH'], app.config['UPLOAD_DIRECTORY'])
                
                # As we process the uploaded data, log all errros                
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

        return render_template("transfer_results.html",
                        errors=errors,
                        success=success,
                        transfer_type='Upload')

@app.route('/download/<int:track_id>')
@login_required
def download_track(track_id):
    data = databaseFunctions.get_track(track_id, session.get('user_id'), app.config['DATABASE_PATH'])
    
    if not data:
        return render_template('show_msg.html',
                               msg='No Tracks Found To download')
    
    track = data[0]
    file_path, original_filename = get_track_file_info(data[0])
    
    if not os.path.exists(file_path):
        return render_template('show_msg.html',
                               msg=f"File'{file_path}' with original filename '{original_filename}' not found on server")
    
    return send_file(file_path, 
                     as_attachment=True,
                     download_name=original_filename)
@app.route('/search')
@login_required
def search():
    try:
        q = request.args.get("q", "")
        # Pass the user_id from the session
        search_results = databaseFunctions.search_tracks_by_name(db, q, session.get('user_id'), app.config['DATABASE_PATH'])
        return render_template("search_results.html", track=search_results)
    except Exception as e:
        print(f"!!! SEARCH ERROR: {e}")
        return render_template('msg.html',
                               msg="Search Error")
    
@app.route('/search_only')
@login_required
def search_only():
    try:
        q = request.args.get("q", "")
        # Pass the user_id from the session
        search_results = databaseFunctions.search_tracks_by_name(db, q, session.get('user_id'), app.config['DATABASE_PATH'])
        return render_template("search_only.html", track=search_results)
    except Exception as e:
        print(f"!!! SEARCH ERROR: {e}")
        return render_template('msg.html',
                               msg="Search Error")


@app.route('/delete/<int:track_id>', methods=['POST'])
@login_required
def delete_track(track_id):

    result = databaseFunctions.delete_track_by_id(track_id, session.get('user_id'), app.config['DATABASE_PATH'])

    if result == databaseFunctions.DELETE_ERROR:
        return render_template('show_msg.html',
                               msg=f"Could not delete track {track_id}")
    if result == databaseFunctions.DELETE_FILE_ERROR:
        return render_template('show_msg.html',
                           msg=f"Could not delete file associated with track with id: {track_id}")
    return redirect(request.referrer or '/')

@app.route('/update_description/<int:track_id>', methods=['POST'])
@login_required
def update_description(track_id):
    data = request.get_json()

    new_description = data.get('description')

    databaseFunctions.update_description(track_id, session.get('user_id'), new_description, app.config['DATABASE_PATH'])

    return jsonify({"success": True})


@app.route('/allTrip')
@login_required
def all_trips():
    totals = databaseFunctions.get_totals(session.get('user_id'), app.config['DATABASE_PATH'])

    if not totals:
        return render_template("show_msg.html",
                               msg="No data found to calculate totals"), 404
    
    
    return render_template('all_trips.html', totals=totals)


##          COMPARISON              ##
@app.route("/compare", methods=["GET"])
@login_required
def compare_select():
    tracks = databaseFunctions.get_tracks(session.get('user_id'), app.config['DATABASE_PATH'])
    return render_template("compare_select.html", tracks=tracks)

@app.route("/compare", methods=["POST"])
@login_required
def compare_submit():
    selected = request.form.getlist("track_ids")

    if len(selected) != 2:
        return render_template('show_msg.html',
                               msg="Please select only 2 tracks"), 400

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
    track1 = databaseFunctions.get_gpx_points(track1_id, session.get('user_id'), app.config['DATABASE_PATH'])
    track2 = databaseFunctions.get_gpx_points(track2_id, session.get('user_id'), app.config['DATABASE_PATH'])

    
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

        tracks = databaseFunctions.get_track_w_datecutoff(session.get('user_id'), cutoff_date, app.config['DATABASE_PATH'])
        track_ids = [track["id"] for track in tracks]

        totals_filtered = databaseFunctions.get_totals_filtered(
            session.get('user_id'),
            track_ids,
            app.config['DATABASE_PATH']
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
    user_db = databaseFunctions.get_user_by_id(user_id, app.config['DATABASE_PATH'])[0]
    username = session.get('username')
    password_hash = user_db['password_hash']
    
    if request.method == 'POST':
        
        current_password = request.form['currentPassword']
        new_password = request.form['newPassword']
        confirm_password = request.form['confirmPassword']    

        if not check_password_hash(password_hash, current_password):
             return render_template('account_settings.html',
                                    username=username,
                                    user_id=user_id,
                                    error="Current password is incorrect")

        if new_password != confirm_password:
            return render_template('account_settings.html',
                                   username=username,
                                   user_id=user_id,
                                   error="New password does not match")
     
        result = databaseFunctions.update_user_password(user_id, new_password, app.config['DATABASE_PATH'])

        if not result:
            return render_template('account_settings.html',
                                   user_id=user_id,
                                   username=username,
                                   error="Failed to update password, database error")
        
        return render_template('account_settings.html',
                               username=username,
                               user_id=user_id,
                               error=None, 
                               success="Password updated Successfully")

    return render_template('account_settings.html',
                           username=username,
                           user_id=user_id,
                           error=None,
                           success=None)

@app.route('/download_all_tracks', methods=['GET', 'POST'])
@login_required
def download_all_tracks():
    user_id = session.get('user_id')
    username = session.get('username')
        
    all_tracks = databaseFunctions.get_tracks(user_id, app.config['DATABASE_PATH'])
    if not all_tracks:
        return render_template("show_msg.html",
                               msg="No tracks found to download"), 404
    
    
    log_content = f"Download Report for {username}\n"
    log_content += "="*30 + "\n\n"
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for track in all_tracks:
            file_path, original_filename = get_track_file_info(track)
            
            if os.path.exists(file_path):
                zf.write(file_path, arcname=original_filename)
                log_content += f"[SUCCESS] {original_filename} filepath: {file_path} \n"
            else:
                log_content += f"[ERROR]   {original_filename} filepath: {file_path} - File missing on server\n"
        zf.writestr('download_log.txt', log_content)
    memory_file.seek(0)
    
        
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'{username}_gpx_files.zip'
    )

## USER DELETE PROCESS ##

@app.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():

    step = 1
    message = None

    if request.method == 'POST':
        step = int(request.form.get('step', 1))

       
        if step == 1:
            step = 2

        
        elif step == 2:
            username = request.form.get('username')
            password = request.form.get('password')

            # must match logged-in user
            # otherwise anyone with the user's credentials
            # can just delete the user
            if username != session.get('username'):
                message = "Username is incorrect"
                step = 2

            # verify password using db verify_user
            elif not databaseFunctions.verify_user(username, password, app.config['DATABASE_PATH']):
                message = "Password is incorrect"
                step = 2

            else:
                # user deletion is pending
                session['pending_delete_user'] = username
                step = 3

        # delete process 
        elif step == 3:
            username = session.pop('pending_delete_user', None)

            if username:
                databaseFunctions.delete_user_by_id(session.get('user_id'), app.config['DATABASE_PATH'], app.config['TEMP_FOLDER'] )
                
                session.clear()

                return redirect(url_for('home'))

    return render_template('delete_account.html', step=step, message=message)


@app.route('/faq')
def faq():
    faq_data = [
        {
            "section": "General",
            "questions": [
                {"q": "Where are all uploaded files uploaded to?", "a": "They are all in the uploads folder"},
                {"q": "Can I upload more than one GPX file?", "a": "Yes you can upload more than one file at a time!"},
                {"q": "What type of GPX files are supported?", "a": "GPX 1.0 and GPX 1.1"},
                {"q": "What is the difference between GPX 1.0 and 1.1?", "a": """The speed attribute is missing in GPX 1.1 
                but we are still able to get it back through GPX 1.1 extensions. Bearing is also missing in 1.1"""},
                {"q": "What happens when I delete my account?", "a": """After account deletion all user information is deleted,
                 then all the deleted users files are moved to the "temp" folder where they can be recovered one last time"""},
            ]
        },
        {
            "section": "Limitations of GPS data",
            "questions": [
                {"q": "Why is my max speed an absurd amount like 5000 mph?", "a": "This is due to GPS jumps, we try to filter out the most we can"},
                {"q": "GPS Drift", "a": """This means when the GPS device reports that is moving but actually is just stationary,
                                        a high stopped distance may indicate a poor recording"""},
                {"q": "GPS Jump", "a": "Can be caused when a GPS signal is weak, so the calculations for (speed, distance and others) may be entirely incorrect"}
            ]
        },
        {
            "section": "Understanding GPS data types",
            "questions": [
                {"q": "How do I view my tracks?", "a": "Go to the home page."},
                {"q": "Can I delete a track?", "a": "Yes, use the delete button. Deleting a track would also delete the file"}
            ]
        }
    ]
    
    # TODO ADD in gps limitations GPS Drift, GPS JUMP FAQ
    types = [
        {
            "section": "Track",
            "trackTypes": [
                {"k": "Filename", "v": "Name of the track"},
                {"k": "Filepath", "v": "Path of where a track is saved on disk"},
                {"k": "Description", "v": "Custom field, you can write whatever you want here"},
                {"k": "Average Moving Speed", "v": "Average Speed when you were moving"},
                {"k": "Total Distance 2D", "v": "Total distance traveled in 2 Dimensions (Altitude & Longitude)"},
                {"k": "Total Distance 3D", "v": "Total distance traveled in 3 Dimensions (Altitude, Longitude & Elevation)"},
                {"k": "Moving Time", "v": "Time spent moving"},
                {"k": "Stopped Time", "v": "Time spent NOT moving"},
                {"k": "Stopped Distance", "v": "Should always be 0, if not then GPS Drift happened (see GPS limitations -> GPS Drift)"},
                {"k": "Max Speed", "v": "Maximum speed reached in a trip, can sometimes be incorrect (see GPS limitations -> GPS Jump)"},
                {"k": "Average Speed", "v": "Average speed throughout the entire trip"},
                {"k": "Uphill", "v": "Total elevation increase during the trip"},
                {"k": "Downhill", "v": "Total elevation decrease during the trip"},
                {"k": "Start Time", "v": "Time where the trip started"},
                {"k": "End Time", "v": "Time where the trip ended"},
                {"k": "Points", "v": "Total number of track points (GPS data points) recorded on the trip"},
                {"k": "GPX Version","v": "Version of the GPX file for a trip"}
            ]
        },
        {
            "section": "Track Points",
            "trackTypes": [
                  {"k": "Latitude", "v": "A geographic coordinate"},
                  {"k": "Longitude", "v": "A geographic coordinate"},
                  # Optional data
                  {"k": "Elevation", "v": "Height at that trackpoint"},
                  {"k": "Time", "v": "Time when the track point was recorded"},
                  {"k": "Course", "v": "Angle of the device when the point was recorded"},
                  {"k": "Speed", "v": "Speed at that point"},
                  #{"k": "Geoidheight", "v": ""},
                  {"k": "Source", "v": "What did the device use to record the point Eg. Cell towers, Satellites"},
                  {"k": "Satellites", "v": "Count of how many satellites where in sight during the recording"},
                  {"k": "HDOP", "v": "Horizontal dilution of precision (lower values mean more accurate data)"},
                  {"k": "VDOP", "v": "Vertical dilution of precision (lower values mean more accurate data)"},
                  {"k": "PDOP", "v": "Position dilution of precision (lower values mean more accurate data)"},
                  
            ]
        }
    ]

    return render_template('faq.html', title="Frequently Asked Questions", faq_data=faq_data, types=types)

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


def get_track_file_info(track):
    """
    Resolves the physical storage path and original name of a track file.

    Args:
        track (dict): A track record containing at least 'track_hash' 
            and 'filename'.

    Returns:
        tuple: A pair containing:
            - file_path (str): The absolute path to the file on the server.
            - original_filename (str): The original name of the uploaded file.
    """
    # Get track hash
    hash_value = track.get("track_hash")
    # Get original filename
    original_filename = track.get("filename")
    # Get the extension
    extension = Path(original_filename).suffix
    # Re-construct the filename + extension
    stored_file = f"{hash_value}{extension}"
    
    file_path = os.path.join(app.config['UPLOAD_DIRECTORY'], stored_file)
    
    return file_path, original_filename

@app.route('/leaderboard', methods=['GET', 'POST'])
@login_required
def leaderboard():

    field = request.args.get('field', 'length_2d')

    leaderboard_users = databaseFunctions.get_leaderboard(field, app.config['DATABASE_PATH'])

    if request.headers.get('HX-Request'):
        return render_template('components/leaderboard_table.html', leaderboard_users=leaderboard_users, field=field)
    
    return render_template('leaderboard.html', leaderboard_users=leaderboard_users, field=field)


# For running the app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)    
