import sqlite3 
from backend.Track import Track
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

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
        points INTEGER
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
            REFERENCES track (id)
            ON DELETE CASCADE
    );
    """)
    conn.commit()
    conn.close()

def insert_track(track : Track) -> str | sqlite3.IntegrityError :
    """
    First checks if a track is already present,
    if not it adds to the database

    Args:
        track (Track): Takes in track object
    Returns:
        (str): If integrity check for track failed
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
                                 points) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                                 track.points,))
           
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
        
def delete_track_by_id(id: str):
    """
    Deletes a track by id of the track
    and CASCADE DELETE all related track points 
    from the track_point table
    
    Args:
        id (str): id of the track
    Returns:
        True if deleted sucessfully 
    """
    with sqlite3.connect("backend/test.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM track WHERE id = ?",
            (id,)
        )
        cur.execute(
            "DELETE FROM track_point WHERE track_id = ?",
            (id,)
        )
    return True

def delete_track_by_hash(track_hash: str):
    """
    Deletes a track by hash value
    and CASCADE DELETE 
    all related track points 
    from the track_point table
    
    Args:
        track_hash (str): hash value
    Returns:
        True if deleted sucessfully 
    
    """
    with sqlite3.connect("backend/test.db") as conn:
        cur = conn.cursor()

        # Get track id
        cur.execute("SELECT id FROM track WHERE track_hash = ?", (track_hash,))
        row = cur.fetchone()

        if row is None:
            return False

        track_id = row[0]

       
        cur.execute(
            "DELETE FROM track_point WHERE track_id = ?",
            (track_id,)
        )
        # delete track
        cur.execute(
            "DELETE FROM track WHERE id = ?",
            (track_id,)
        )
        conn.commit()
        return True

def get_all_tracks() -> list[tuple]:
    """
    Retrieve all rows from the track table.

    Returns:
        list[tuple]: A list of tuples
            (
    """
    with sqlite3.connect("backend/test.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM track")
        rows = cur.fetchall()
        return rows

def get_all_track_points() -> list[tuple]:
    """
    Retrieve all rows from the track_point table.

    Returns:
        list[tuple]: A list of tuples in the following order:
            (id, track_id, lat, lon, ele, timestamp, course, speed, geoidheight, src, sat, hdop, vdop, pdop)
    """
    with sqlite3.connect("backend/test.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * from track_point")
        rows = cur.fetchall()
        return rows

def get_track_with_track_points_by_id(id: str) -> dict[str, list[tuple]]:
    """
    Get a track with all related track_points by using an id
    
    Args:
        id(str): The id of the track

    Returns:
        dict[str, list[tuple]]: A dictionary containing:
            - "track": Tuples in the order of: (id, name, track_hash)
            - "track_points": Tuples in the order of:
            (id, track_id, lat, lon, ele, timestamp, course, speed, geoidheight, src, sat, hdop, vdop, pdop)
    """
    with sqlite3.connect("backend/test.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * from track WHERE id = ?",(id,))
        track_rows = cur.fetchall()

        cur.execute("SELECT * from track_point WHERE track_id = ? ",(id,))
        track_point_rows = cur.fetchall()
        
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
        list[tuple]: A list of tuples containing the requested column
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

