import sqlite3 
import parser
from Track import Track

def insert_track(track : Track):    
    conn = sqlite3.connect('test.db')
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

    conn.commit()
    conn.close()


