import sqlite3

conn = sqlite3.connect('test.db')
c = conn.cursor()

# Enable foreign key support
c.execute("PRAGMA foreign_keys = ON;")

# Create tables and index
c.executescript("""
CREATE TABLE IF NOT EXISTS track (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    track_hash TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS gps_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id INTEGER NOT NULL,
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
    FOREIGN KEY (track_id) REFERENCES track(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS id_gps_trip_time
ON gps_data (track_id, timestamp);
""")

conn.commit()
conn.close()
