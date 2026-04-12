import sqlite3
import os
from backend.Track import Track
import json
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy



# Error Codes #
SUCCESS = 0
DUPLICATE_ERROR = 1
INTEGRITY_ERROR = 2
DATABASE_EXISTS = 3
DELETE_FILE_ERROR = 4
DELETE_ERROR = 5

# Directories #
DatabasePath = json.load(open("config.json"))["DATABASE_PATH"]
UploadDirectory = json.load(open("config.json"))["UPLOAD_DIRECTORY"]

def createDatabase() -> int:
    """
    Creates a SQLite3 Database, if one is already present returns 3
    Returns:
        (int): 0 for SUCCESS, 3 for Database already exists
        
    """
    if os.path.exists(DatabasePath):
        return DATABASE_EXISTS
    
    conn = sqlite3.connect(DatabasePath)
    cur = conn.cursor()

    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON")

    createDB="""

    CREATE TABLE IF NOT EXISTS track (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        track_hash TEXT NOT NULL UNIQUE,
        length_2d REAL,
        length_3d REAL,
        moving_time REAL,
        stopped_time REAL,
        moving_distance REAL,
        stopped_distance REAL,
        max_speed REAL,
        avg_speed REAL,
        uphill REAL,
        downhill REAL,
        start_time TEXT,
        end_time TEXT,
        points INTEGER,
        filepath TEXT NOT NULL,
        filename TEXT NOT NULL,
        gpx_version TEXT,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS track_point (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_id INTEGER NOT NULL,
        lat REAL NOT NULL,
        lon REAL NOT NULL,
        ele REAL,
        timestamp TEXT NOT NULL,
        course REAL,
        speed REAL,
        geoidheight REAL,
        src TEXT,
        sat INTEGER,
        hdop REAL,
        vdop REAL,
        pdop REAL,
        
        FOREIGN KEY (track_id) REFERENCES track(id)
            ON DELETE CASCADE
    );
                      
    CREATE TABLE IF NOT EXISTS user (
        id  INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    );
                      
    CREATE TABLE IF NOT EXISTS user_tracks (
        user_id INT NOT NULL,
        track_id NOT NULL,
                      
        FOREIGN KEY (track_id) REFERENCES track(id)
        FOREIGN KEY (user_id) REFERENCES user(id)
                      
        PRIMARY KEY(user_id, track_id)
    );

    CREATE INDEX idx_track_point_track_id 
    ON track_point(track_id);

    CREATE INDEX idx_user_tracks_track_id 
    ON user_tracks(track_id);

    CREATE INDEX idx_track_point_timestamp 
    ON track_point(timestamp);
    """

    # Create tables and index
    cur.executescript(createDB)
    conn.commit()
    conn.close()

    return SUCCESS


def insert_track(track : Track, user_id : int) -> int:
    """
    First checks if a track is already present,
    if not it adds to the database

    Args:
        track (Track): Takes in track object
        user_id (int): The current user_id
    Returns:
        (int):  0: Success
                1: Duplicate exists in database
                2: Track Integrity Check Failed
    Raises:
        sqlite3.IntegrityError: If the track already exists in database
        
    """
    if(not track.integrityCheck()):
        return INTEGRITY_ERROR
    track_hash = track.track_hash()
    hashedFilePath = os.path.join(UploadDirectory, track_hash) + ".gpx" #TODO Might Break in the Future
    try:
        with sqlite3.connect(DatabasePath) as conn:
            cur = conn.cursor()
            cur.execute(
            """INSERT INTO track (name, 
                                 track_hash,
                                 length_2d,
                                 length_3d,
                                 moving_time,
                                 stopped_time,
                                 moving_distance,
                                 stopped_distance,
                                 max_speed,
                                 avg_speed,
                                 uphill,
                                 downhill,
                                 start_time,
                                 end_time,
                                 points,
                                 filepath,
                                 filename,
                                 gpx_version) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (track.name,
                                 track.track_hash(),
                                 track.length_2d,
                                 track.length_3d,
                                 track.moving_data.moving_time,
                                 track.moving_data.stopped_time,
                                 track.moving_data.moving_distance,
                                 track.moving_data.stopped_distance,
                                 track.moving_data.max_speed,
                                 track.avg_speed,
                                 track.uphill.uphill,
                                 track.uphill.downhill,
                                 track.time_bounds.start_time,
                                 track.time_bounds.end_time,
                                 track.points,
                                 hashedFilePath,
                                 track.filename,
                                 track.gpxVersion,))
           
            track_id = cur.lastrowid
            data = [
            (
                track_id,
                lat,
                lon,
                ele,
                time.isoformat() if time else None,
                course,
                speed,
                geoidheight,
                src,
                sat,
                hdop,
                vdop,
                pdop
            )
            for lat, lon, ele, time, course, speed,
                geoidheight, src, sat, hdop, vdop, pdop
            in zip(
                track.lat,
                track.lon,
                track.ele,
                track.time,
                track.course,
                track.speed,
                track.geoidheight,
                track.src,
                track.sat,
                track.hdop,
                track.vdop,
                track.pdop
            )
        ]
            cur.executemany("""
            INSERT INTO track_point (
                track_id, lat, lon, ele, timestamp, course,
                speed, geoidheight, src, sat,
                hdop, vdop, pdop
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)

            cur.execute("""
                INSERT INTO user_tracks (
                    user_id,
                    track_id
                )
                VALUES (?, ?);""", (user_id, track_id))

    except sqlite3.IntegrityError:
        return DUPLICATE_ERROR
    
    return SUCCESS


def delete_track_by_id(id: str, user_id: str) -> bool | int:
    """
    Deletes a track by id of the track
    and CASCADE DELETE all related track points 
    from the track_point table
    
    Args:
        id (str): id of the track
    Returns:
        bool: True if deleted sucessfully
        int: A error code if something bad happened
    """
    try:
        int_id = int(id)  # convert id to int
    except ValueError:
        return False
    
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()

        cur.execute("SELECT filepath, track_hash FROM track WHERE id = ?", (int_id,))
        row = cur.fetchone()

        if not row:
            return DELETE_ERROR  # track does not exist

        filepath, track_hash = row
        pathOnly = filepath.rsplit('/', 1)[0]
        hashFilePath = os.path.join(pathOnly, track_hash) + ".gpx" #TODO Might Break in the Future

        cur.execute("DELETE FROM track_point WHERE track_id = ?", (int_id,))
        cur.execute("DELETE FROM track WHERE id = ?", (int_id,))

        cur.execute("DELETE FROM user_tracks WHERE track_id = ? AND user_id = ?",(id,user_id,))
        
    try: 
        if filepath and os.path.exists(hashFilePath):
            os.remove(hashFilePath)
    except:
        return DELETE_FILE_ERROR
        
    return True


def get_tracks(user_id: int) -> list[dict]:
    """Retrive all rows from the track table for a specified user"""
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()
        query = """SELECT tr.* 
                    FROM user_tracks ut
                    JOIN track tr
                    ON ut.track_id = tr.id
                    WHERE user_id = (?) """
        
        cur.execute(query, (user_id,))

        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
    

def get_gpx_points(id: str, user_id: str) -> dict[str, list[dict]]:
    """
    Get data from track table and track_point table based on user_id
    Args:
        id(str): The id of the track
        user_id(str): The current user id in the session
    Returns:
        dict[str, list[dict]]: A dictionary containing:
            - "track": A list of dictionaries representing a track row (SINGLE ROW ALWAYS)
            - "track_points": A list of dictionaries representing track_point rows
    """
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()

        getTrackInfo = """
            SELECT t.*
            FROM user_tracks ut
            JOIN track t ON ut.track_id = t.id
            WHERE ut.user_id = ?
            AND t.id = ?
        """
        cur.execute(getTrackInfo, (user_id, id),)
        track_columns = [desc[0] for desc in cur.description]
        track_rows = [dict(zip(track_columns, row)) for row in cur.fetchall()]

        getTrackPointInfo = """
            SELECT tp.*
            FROM user_tracks ut
            JOIN track t ON ut.track_id = t.id
            JOIN track_point tp ON t.id = tp.track_id
            WHERE ut.user_id = ?
            AND t.id = ?
        """
        cur.execute(getTrackPointInfo, (user_id, id),)
        tp_columns = [desc[0] for desc in cur.description]
        track_point_rows = [dict(zip(tp_columns, row)) for row in cur.fetchall()]

        return {
            "track": track_rows,
            "track_points": track_point_rows
        }


def get_totals(user_id: str) -> dict:
    """
    Retrieve all aggregate track statistics.
    """
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT
                TOTAL(t.length_2d)        AS length_2d,
                TOTAL(t.length_3d)        AS length_3d,
                TOTAL(t.moving_time)      AS moving_time,
                TOTAL(t.stopped_time)     AS stopped_time,
                TOTAL(t.moving_distance)  AS moving_distance,
                TOTAL(t.stopped_distance) AS stopped_distance,
                TOTAL(t.uphill)           AS uphill,
                TOTAL(t.downhill)         AS downhill,
                TOTAL(t.points)           AS points,
                AVG(t.avg_speed)          AS overall_avg_speed,
                SUM(CASE WHEN t.gpx_version = '1.0' THEN 1 ELSE 0 END) AS gpx_1_0_count,
                SUM(CASE WHEN t.gpx_version = '1.1' THEN 1 ELSE 0 END) AS gpx_1_1_count        
            FROM user_tracks ut
            JOIN track t ON ut.track_id = t.id
            WHERE ut.user_id = ?
        """, (user_id,))

        row = cur.fetchone()

        # Convert to dict
        columns = [col[0] for col in cur.description]
        return dict(zip(columns, row))

def get_totals_filtered(user_id: str, track_ids: list[int]) -> dict:
    """
    Retrieve aggregate track statistics for a user filtered by track IDs.
    """

    if not track_ids:
        return {}
    
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()

        placeholders = ",".join(["?"] * len(track_ids))

        cur.execute(f"""
            SELECT
                TOTAL(t.length_2d)        AS length_2d,
                TOTAL(t.length_3d)        AS length_3d,
                TOTAL(t.moving_time)      AS moving_time,
                TOTAL(t.stopped_time)     AS stopped_time,
                TOTAL(t.moving_distance)  AS moving_distance,
                TOTAL(t.stopped_distance) AS stopped_distance,
                TOTAL(t.uphill)           AS uphill,
                TOTAL(t.downhill)         AS downhill,
                TOTAL(t.points)           AS points,
                AVG(t.avg_speed)          AS overall_avg_speed,
                SUM(CASE WHEN t.gpx_version = '1.0' THEN 1 ELSE 0 END) AS gpx_1_0_count,
                SUM(CASE WHEN t.gpx_version = '1.1' THEN 1 ELSE 0 END) AS gpx_1_1_count
            FROM user_tracks ut
            JOIN track t ON ut.track_id = t.id
            WHERE ut.user_id = ?
              AND ut.track_id IN ({placeholders})
        """, (user_id, *track_ids))

        row = cur.fetchone()

        if not row:
            return {}

        columns = [col[0] for col in cur.description]
        return dict(zip(columns, row))
    
def get_track(track_id: str, user_id: str) -> list[dict]:
    """
    Retrieve a specific track info given its id and user_id
    Args:
        track_id(str): The id of the track
        user_id(str): The user_id
    Returns:
        list[dict]: A list of dict containing all of the track info
    """
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()

        getTrackInfo = """
            SELECT t.*
            FROM user_tracks ut
            JOIN track t ON ut.track_id = t.id
            WHERE ut.user_id = ?
            AND t.id = ?
        """
        cur.execute(getTrackInfo, (user_id, track_id),)
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def get_track_w_datecutoff(user_id: str, cutoff_date: str) -> list[dict]:
    """
    Gets all track info given a user_id and cut-off date
    Args:
        user_id(str): The user_id
        cutoff(str): The date from where to stop
    Returns:
     list[dict]: A list of dict containing all of the track info
    """
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()

        getTrackInfo = """
            SELECT t.*
            FROM user_tracks ut
            JOIN track t ON ut.track_id = t.id
            WHERE ut.user_id = ?
            AND start_time >= ?
        """
        cur.execute(getTrackInfo, (user_id, cutoff_date),)
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def update_description(track_id: int, user_id: int, description: str) -> bool:
    """
    Update a track description
    Arguments:
        track_id (int): The id of the track
        user_id (int): The id of the user
        description (str): The new description text
    Returns:
        bool: True if success false otherwise
    """

    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT 1 FROM user_tracks
            WHERE track_id = ? AND user_id = ?
        """, (track_id, user_id))

        if cur.fetchone() is None:
            return False  
        cur.execute("""
            UPDATE track
            SET description = ?
            WHERE id = ?
        """, (description, track_id))

        conn.commit()
        return True
    return False

def create_user(username: str, password: str) -> bool:
    """
    Create a user
    Arguments:
        username (str): The username
        password (str): The hashed password value
    Returns:
        bool: True if success insert of user, false if username already exists
    """
    try:
        with sqlite3.connect(DatabasePath) as conn:
            cur = conn.cursor()

            password_hash = generate_password_hash(password)

            cur.execute("""
                INSERT INTO user (username, password_hash)
                VALUES (?, ?)""", (username, password_hash))

        return True # username & hash password added

    except sqlite3.IntegrityError:
        return False  # username already exists
    
def verify_user(username, password) -> int | bool:
    """
    Authenticate the user
    Arguments:
        username (str): The username
        password (str): The hashed password value
    Returns:
        int | bool: Return the user_id if authenticated False if fail to authenticate
    """
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT id, password_hash FROM user WHERE username = ?
            """, (username,))
        user = cur.fetchone()

    if user and check_password_hash(user[1], password):
        return user[0] # return user_id

    return False

from sqlalchemy import text

def search_tracks_by_name(db: SQLAlchemy, query_text: str, user_id: str) -> list[dict]:
    """
    Returns a list of the searched elements in the database
    Note: Returns everything if the query is empty.
    Arguments:
        db (SQLAlchemy): The database to be queried
        query_text (str): The thing being queried
        user_id (str): The current logged in user id
    Returns:
    list[dict]: List of tracks as dictionaries
    """
    if not query_text:
        sql = text("""
            SELECT tr.*
            FROM track tr
            JOIN user_tracks ut ON ut.track_id = tr.id
            WHERE ut.user_id = :user_id
        """)
        result = db.session.execute(sql, {
            "user_id": user_id
        })
    else:
        sql = text("""
            SELECT tr.*
            FROM track tr
            JOIN user_tracks ut ON ut.track_id = tr.id
            WHERE ut.user_id = :user_id
            AND LOWER(tr.name) LIKE LOWER(:name)
        """)
        result = db.session.execute(sql, {
            "user_id": user_id,
            "name": f"%{query_text}%"
        })  
    return result.fetchall()
