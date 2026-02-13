import sqlite3 
from Track import Track

def insert_track(track : Track):
    """
    Inserts a track to the database

    Args:
        track (Track): Takes in track object
    Raises:
        Database exception if the track already exists (TODO)
    """
    with sqlite3.connect("test.db") as conn:
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
        
def delete_track_by_id(id: str):
    """
    Deletes a track by id of the track
    and CASCADE DELETE all related track points 
    from the track_point table
    
    Args:
        id (str): id of the track    
    """
    with sqlite3.connect("test.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM track WHERE id = ?",
            (id,)
        )
        cur.execute(
            "DELETE FROM track_point WHERE track_id = ?",
            (id,)
        )

def delete_track_by_hash(track_hash: str):
    

    with sqlite3.connect("test.db") as conn:
        cur = conn.cursor()
        
        cur.execute(
            "DELETE FROM track WHERE track_hash = ? ",
            (track_hash,)
        )
        cur.execute(
            "DELETE from track_"
        )
        