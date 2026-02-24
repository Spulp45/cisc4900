import sqlite3 
from backend.Track import Track
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

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

        
def avg_speed(id: str) -> float:
    """
    Get average speed from a track

    Args:
        track_hash (str): The hash value of the track
    Returns:
        float: Represents the average speed
    """
    with sqlite3.connect("backend/test.db") as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT AVG(speed) 
            FROM track_point 
            WHERE track_id = ? 
            AND speed > 0.0
            """, (id,))
        
        row = cur.fetchone()

        if row and row[0] is not None:
            return row[0]
        else:
            return 0.0
        
def duration (id: str) -> int:
    """
    Calculate the total duration of a track in seconds.

    It is computed by subtracting between the earliest and latest timestamp
    """
    timestamps = get_trackpoints(id, "timestamp")

    dt_objects = [datetime.fromisoformat(ts[0]) for ts in timestamps]

    duration = max(dt_objects) - min(dt_objects)

    total_seconds = int(duration.total_seconds())

    return total_seconds

def calculate_elevation_stats(track_id):
    ele_rows = get_trackpoints(track_id, "ele")
    if not ele_rows or len(ele_rows) < 2:
        return 0.0, 0.0

    uphill = 0.0
    downhill = 0.0
    threshold = 0.75 # Ignore changes smaller than 50cm

    for i in range(len(ele_rows) - 1):
        diff = ele_rows[i+1][0] - ele_rows[i][0]
        
        if diff > threshold:
            uphill += diff
        elif diff < -threshold:
            downhill += abs(diff)

    return uphill, downhill

def calculate_total_distance(track_id):
    # 1. Get your coordinates
    lats = get_trackpoints(track_id, "lat")
    lons = get_trackpoints(track_id, "lon")
    
    if not lats or not lons:
        return 0.0

    total_dist = 0.0
    # 2. Loop through points and calculate distance between point i and i+1
    for i in range(len(lats) - 1):
        lat1, lon1 = lats[i][0], lons[i][0]
        lat2, lon2 = lats[i+1][0], lons[i+1][0]
        
        # Convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # Haversine formula
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        km = 6371 * c
        meters = (6371 * c) * 1000
        total_dist += meters

    return total_dist # Now returns total distance in meters
 
    
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



