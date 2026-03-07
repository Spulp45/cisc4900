import sqlite3
import os
from backend.Track import Track
from collections import namedtuple

def createDatabase():
    """
    Creates a SQLite3 Database, if one is already present
    it does nothing
    """
    conn = sqlite3.connect('backend/test.db')
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
        filename TEXT NOT NULL
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

def insert_track(track : Track) -> str | bool | sqlite3.IntegrityError :
    """
    First checks if a track is already present,
    if not it adds to the database

    Args:
        track (Track): Takes in track object
    Returns:
        (str): If integrity check for track failed
        (bool): True if insert is successful
    Raises:
        sqlite3.IntegrityError: If the track already exists in database
        
    """
    if(not track.integrityCheck()):
        return f"Failed to insert, data integrity for track '{track.name}' failed"
    
    try:
        with sqlite3.connect("backend/test.db") as conn:
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
                                 points, filepath,
                                 filename) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                                 track.filename,))
           
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
        print(f"'{track.name}' Already exists in the database")
    return True
        
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
    
    with sqlite3.connect("backend/test.db") as conn:
        cur = conn.cursor()

        cur.execute("SELECT filepath FROM track WHERE id = ?", (int_id,))
        row = cur.fetchone()

        if not row:
            return False  # track does not exist

        filepath = row[0]
        print(filepath)

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
    with sqlite3.connect("backend/test.db") as conn:
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
    with sqlite3.connect("backend/test.db") as conn:
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
    with sqlite3.connect("backend/test.db") as conn:
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
        with sqlite3.connect("backend/test.db") as conn:
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
    with sqlite3.connect("backend/test.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT id from track where name = ?", (name,),)
        rows = cur.fetchall()
        return rows
    
def get_sql_total_only() -> namedtuple:
    with sqlite3.connect("backend/test.db") as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Build NamedTuple structure
        cur.execute("SELECT * FROM track LIMIT 0")
        column_names = [desc[0] for desc in cur.description]
        TrackRow = namedtuple("TrackRow", column_names)

        cur.execute("""
            SELECT 0 as id, 'TOTAL' as name, '' as track_hash, 
                   SUM(length_2d) as length_2d, SUM(length_3d) as length_3d,
                   SUM(moving_time) as moving_time, SUM(stopped_time) as stopped_time,
                   SUM(moving_distance) as moving_distance, SUM(stopped_distance) as stopped_distance,
                   MAX(max_speed) as max_speed, AVG(avg_speed) as avg_speed, 
                   SUM(uphill) as uphill, SUM(downhill) as downhill,
                   '' as start_time, '' as end_time, SUM(points) as points,
                    filepath, filename
            FROM track
        """)

        total_data = cur.fetchone()

        # Detect empty table
        if total_data["points"] is None:
            return None

        return TrackRow(*total_data)
