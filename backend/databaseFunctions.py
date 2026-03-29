import sqlite3
import os
from backend.Track import Track
import json
from werkzeug.security import generate_password_hash, check_password_hash



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

    # Create tables and index
    cur.executescript("""

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
        gpx_version TEXT
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
    """)
    conn.commit()
    conn.close()

    return SUCCESS
#TODO update docstring
def insert_track(track : Track, user_id : int) -> int:
    """
    First checks if a track is already present,
    if not it adds to the database

    Args:
        track (Track): Takes in track object
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

def get_all_tracks() -> list[dict]:
    """Retrieve all rows from the track table."""
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM track")

        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def get_tracks(user_id: int) -> list[dict]:
    """Retrive all rows from the track table for a specified user"""
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()
        query = """SELECT * 
                    FROM user_tracks ut
                    JOIN track tr
                    ON ut.track_id = tr.id
                    WHERE user_id = (?) """
        
        cur.execute(query, (user_id,))

        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

   
def get_track_with_track_points_by_id(id: str) -> dict[str, list[dict]]:
    """
    Get a track with all related track_points by using the track id

    Args:
        id (str): The id of the track to get

    Returns:
        dict[str, list[dict]]: A dictionary containing:
            - "track": A list of dictionaries representing a track row (SINGLE ROW ALWAYS)
            - "track_points": A list of dictionaries representing track_point rows
    """
 
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()

        cur.execute("SELECT * FROM track WHERE id = ?", (id,))
        track_columns = [desc[0] for desc in cur.description]
        track_rows = [dict(zip(track_columns, row)) for row in cur.fetchall()]

        cur.execute("SELECT * FROM track_point WHERE track_id = ?", (id,))
        tp_columns = [desc[0] for desc in cur.description]
        track_point_rows = [dict(zip(tp_columns, row)) for row in cur.fetchall()]

        return {
            "track": track_rows,
            "track_points": track_point_rows
        }

def get_gps_points(id: str, user_id: str) -> dict[str, list[dict]]:
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

    
def get_trackpoints(id: str, track_point_column: str) -> list[dict] | str:
    """
    Retrieve values from a specific column of track_point rows
    associated with a given track ID.

    Returns:
        list[dict]: [{"column_name": value}, ...]
        str: Error message if column is invalid
    """

    legal_arguments = [
        "id", "track_id", "lat", "lon", "ele", "timestamp", "course",
        "speed", "geoidheight", "src", "sat", "hdop", "vdop", "pdop"
    ]

    if track_point_column not in legal_arguments:
        return f"Invalid column name: {track_point_column}"

    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()
        query = f"SELECT {track_point_column} FROM track_point WHERE track_id = ?"
        cur.execute(query, (id,))

        return [
            {track_point_column: row[0]}
            for row in cur.fetchall()
        ]


def get_totals() -> dict:
    """
    Retrieve all aggregate track statistics.

    Returns:
        dict: A dict of all aggregated values
    """
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                TOTAL(length_2d)        AS length_2d,
                TOTAL(length_3d)        AS length_3d,
                TOTAL(moving_time)      AS moving_time,
                TOTAL(stopped_time)     AS stopped_time,
                TOTAL(moving_distance)  AS moving_distance,
                TOTAL(stopped_distance) AS stopped_distance,
                TOTAL(uphill)           AS uphill,
                TOTAL(downhill)         AS downhill,
                TOTAL(points)           AS points,
                MAX(max_speed)          AS max_speed,
                AVG(avg_speed)          AS overall_avg_speed,
                SUM(CASE WHEN gpx_version = '1.0' THEN 1 ELSE 0 END) AS gpx_1_0_count,
                SUM(CASE WHEN gpx_version = '1.1' THEN 1 ELSE 0 END) AS gpx_1_1_count
            FROM track
        """)

        columns = [desc[0] for desc in cur.description]
        row = cur.fetchone()

        return dict(zip(columns, row)) if row else {}


def create_user(username, password):
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
    
def verify_user(username, password):
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT id, password_hash FROM user WHERE username = ?
            """, (username,))
        user = cur.fetchone()

    if user and check_password_hash(user[1], password):
        return user[0] # return user_id

    return False
