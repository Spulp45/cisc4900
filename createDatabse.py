import sqlite3

conn = sqlite3.connect('test.db')
c = conn.cursor()

c.execute("PRAGMA foreign_keys = ON;")

c.executescript("""
CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS gps_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    ele REAL,
    timestamp TEXT NOT NULL,
    course REAL,
    speed REAL,
    geoid_height REAL,
    src TEXT,
    sat INTEGER,
    hdop REAL,
    vdop REAL,
    pdop REAL,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS id_gps_trip_time
ON gps_data (trip_id, timestamp);
""")

conn.commit()
conn.close()
