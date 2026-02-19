import sqlite3 
from backend.Track import Track
from datetime import datetime

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
        return "Failed to insert, data integrity for track failed"
    
    try:
        with sqlite3.connect("backend/test.db") as conn:
            cur = conn.cursor()
            cur.execute(
            "INSERT INTO track (name, track_hash) VALUES (?, ?)",
            (track.name, track.track_hash()))
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

        
def avg_speed(track_hash: str) -> float:
    """
    Get average speed from a track

    Args:
        track_hash (str): The hash value of the track
    Returns:
        float: Represents the average speed
    """
    with sqlite3.connect("backend/test.db") as conn:
        cur = conn.cursor()

        cur.execute("""SELECT AVG (speed) 
                    FROM track_point
                    WHERE track_id = (SELECT id FROM track WHERE track_hash = ?)
                    AND speed > 0.0
                    """, (track_hash,))
        
        row = cur.fetchone()

        if row and row[0] is not None:
            return row[0]
        else:
            return 0.0
        
def duration (id: str):
    
    timestamps = get_trackpoints(id,"timestamp")


    dt_objects = [datetime.fromisoformat(ts[0]) for ts in timestamps]
    
    duration = max(dt_objects) - min(dt_objects)

    total_seconds = int(duration.total_seconds())

    return total_seconds

 
    
def get_all_tracks() -> list[tuple]:
    """
    Retrieve all rows from the track table.

    Returns:
        list[tuple]: A list of tuples in the following order:
            (id, name, track_hash)
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
    
def get_trackpoints(id : str, track_point_collumn: str) -> list | str:
    """
    Retrieve values from a specific collumn of track_point rows
    associated with a given track ID.

    Args:
        id (str): The ID of the track.
        track_point_collumn (str): The collumn name to retrieve from
            the track_point table.

    Returns:
        list[tuple]: A list of tuples containing the requested collumn
            values for all matching track_point rows. \n
        str: An error message if the collumn name is invalid.
    """
    legal_arguments = ["id", "track_id", "lat", "lon", "ele", "timestamp", "course", "speed",
                       "geoidheight", "src", "sat", "hdop", "vdop", "pdop"]
    
    match track_point_collumn:
        case track_point_collumn if track_point_collumn in legal_arguments:
            with sqlite3.connect("backend/test.db") as conn:
                cur = conn.cursor()
                cur.execute(
                f"SELECT {track_point_collumn} FROM track_point WHERE track_id = ?",
                (id,))
                rows = cur.fetchall()
                return rows
        case _:
            return "Invalid Collumn name for track_point"

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



