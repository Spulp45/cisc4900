import sqlite3
import os
from backend.Track import Track
from collections import namedtuple
import json



# Error Codes #
SUCCESS = 0
DUPLICATE_ERROR = 1
INTEGRITY_ERROR = 2
DATABASE_EXISTS = 3

# Directories #
DatabasePath = json.load(open("config.json"))["DATABASE_PATH"]

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
        name TEXT NOT NULL UNIQUE,
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
        
        FOREIGN KEY (track_id)
            REFERENCES track(id)
            ON DELETE CASCADE
    );
    """)
    conn.commit()
    conn.close()

    return SUCCESS

def insert_track(track : Track) -> int:
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
                                 track.filepath,
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
    
    except sqlite3.IntegrityError:
        return DUPLICATE_ERROR
    
    return SUCCESS
        
def delete_track_by_id(id: str) -> bool:
    """
    Deletes a track by id of the track
    and CASCADE DELETE all related track points 
    from the track_point table
    
    Args:
        id (str): id of the track
    Returns:
        True if deleted sucessfully 
    """
    try:
        int_id = int(id)  # convert id to int
    except ValueError:
        return False
    
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()

        cur.execute("SELECT filepath FROM track WHERE id = ?", (int_id,))
        row = cur.fetchone()

        if not row:
            return False  # track does not exist

        filepath = row[0]

        if filepath and os.path.exists(filepath):
            os.remove(filepath)

        cur.execute("DELETE FROM track_point WHERE track_id = ?", (int_id,))
        cur.execute("DELETE FROM track WHERE id = ?", (int_id,))

    return True

def get_all_tracks() -> list[namedtuple]:
    """
    Retrieve all rows from the track table.

    Returns:
        list[namedtuple]: The name of each tuple represents the column name in the database.
                            Refer to the database column names to know the names of the tuples
    """
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM track")
        # cur.description is a list of metadata for each column retrieved from the execution of the script
        # The first element is the column name
        column_names = [desc[0] for desc in cur.description]

        TrackRow = namedtuple("TrackRow", column_names)

        rows = [TrackRow(*row) for row in cur.fetchall()]

        return rows
    
def get_all_track_points() -> list[namedtuple]:
    """
    Retrieve all rows from the track_point table.

    Returns:
        list[namedtuple]: The name of each tuple represents the column name in the database.
                            Refer to the database column names to know the names of the tuples
    """
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * from track_point")
        # cur.description is a list of metadata for each column retrieved from the execution of the script
        # The first element is the column name
        column_names = [desc[0] for desc in cur.description]

        TrackPointRow = namedtuple("TrackPointRow", column_names)

        rows = [TrackPointRow(*row) for row in cur.fetchall()]

        return rows

    # TODO This function below is kinda too much should we drop it?
def get_track_with_track_points_by_id(id: str) -> dict[str, list[namedtuple]]:
    """
    Get a track with all related track_points by using the track id

    Args:
        id(str): The id of the track to get

    Returns:
        dict[str, list[namedtuple]]: A dictionary containing:
            - "track": A list of namedtuples of type TrackRow. They are in the following order:
                (id, name, track_hash, length_2d, length_3d, moving_time, stopped_time, 
                moving_distance, stopped_distance, max_speed, avg_speed, uphill, downhill, 
                start_time, end_time, points)
            - "track_point": A list of namedtuples representing all track_points associated with that track.
                They are in the following order:
                (id, track_id, lat, lon, ele, timestamp, course, speed, geoidheight, src, 
                sat, hdop, vdop, pdop)
    """
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * from track WHERE id = ?",(id,))
        
        track_column_names = [desc[0] for desc in cur.description]

        TrackRow = namedtuple("TrackRow", track_column_names)

        track_rows = [TrackRow(*row) for row in cur.fetchall()]

        cur.execute("SELECT * from track_point WHERE track_id = ? ",(id,))

        track_point_column_names = [desc[0] for desc in cur.description]

        TrackPointRow = namedtuple("TrackPointRows", track_point_column_names)

        track_point_rows = [TrackPointRow(*row) for row in cur.fetchall()]
        
        return {'track': track_rows, 'track_points' : track_point_rows}
    
def get_trackpoints(id : str, track_point_column: str) -> list | str:
    """
    Retrieve values from a specific column of track_point rows
    associated with a given track ID.

    Args:
        id (str): The ID of the track.
        track_point_column (str): The column name to retrieve from
            the track_point table.

    Returns:
        list[]: A list containing the requested column
            values for all matching track_point rows. \n
        str: An error message if the column name is invalid.
    """
    legal_arguments = [
    "id", "track_id", "lat", "lon", "ele", "timestamp", "course",
    "speed", "geoidheight", "src", "sat", "hdop", "vdop", "pdop"]

    if track_point_column in legal_arguments:
        with sqlite3.connect(DatabasePath) as conn:
            cur = conn.cursor()
            query = f"SELECT {track_point_column} FROM track_point WHERE track_id = ?"
            cur.execute(query, (id,))
            rows = cur.fetchall()
            return rows
    # TODO Change this to exception maybe?
    else:
        return "Invalid column name for track_point"

def get_track_by_name(name: str) -> list:
    """
    Gets a list of all tracks with the same name
    Args:
        name (str): provide a name to search
    Returns:
        list: Of all tracks matching the name
    """
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id from track where name = ?", (name,),)
        rows = cur.fetchall()
        return rows
    
def get_totals_OTHER() -> dict:
    """
    Retreive all data that can be summed up as a total
    
    Returns:
        dict: Each entry in the dict represents the total for each category
    """
    
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * from track")

        column_names = [desc[0] for desc in cur.description]

        TrackPointRow = namedtuple("TrackpointRow",column_names)

        rows = [TrackPointRow(*row) for row in cur.fetchall()]

        totals = {
            "length_2d":        0,
            "length_3d":        0,
            "moving_time":      0,
            "stopped_time":     0,
            "moving_distance":  0,
            "stopped_distance": 0,
            "uphill":           0,
            "downhill":         0,
            "points":           0,
        }

        for row in rows:
            totals["length_2d"] += row.length_2d
            totals["length_3d"] += row.length_3d
            totals["moving_time"] += row.moving_time
            totals["stopped_time"] += row.stopped_time
            totals["moving_distance"] += row.moving_distance
            totals["stopped_distance"] += row.stopped_distance
            totals["uphill"] += row.uphill
            totals["downhill"] += row.downhill
            totals["points"] += row.points
    return totals


def get_totals() -> list[namedtuple]:
    """
    Retreive all data that can be summed up as a total
    
    Returns:
        list[namedtuple]: Each name represents a column name
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

        column_names = ['length_2d', 'length_3d', 'moving_time', 'stopped_time',
                        'moving_distance', 'stopped_distance', 'uphill', 'downhill',
                        'points', 'max_speed', 'overall_avg_speed','gpx_1_0_count', 'gpx_1_1_count']

        TrackTotals = namedtuple("TrackTotals", column_names)

        rows = [TrackTotals(*row) for row in cur.fetchall()]

        return rows