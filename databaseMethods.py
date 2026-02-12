import sqlite3 
import parser
from Track import Track
conn = sqlite3.connect('test.db')
cur = conn.cursor()

track = parser.getGPX("20260205.gpx")

print(len(track.lat))
print(len(track.lon))
print(len(track.ele))
print(len(track.time))
print(len(track.course))
print(len(track.speed))
print(len(track.geoidheight))
print(len(track.src))
print(len(track.sat))
print(len(track.hdop))
print(len(track.vdop))
print(len(track.pdop))




#cur.execute("INSERT INTO track (name, track_hash) VALUES (?, ?)", (track.name, track.track_hash()))

#cur.execute("INSERT INTO gps_data ")

def insert_track(track : Track):    
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()

    currentName = track.name
    currentHash = track.track_hash()

    print(currentName)
    print(currentHash)

