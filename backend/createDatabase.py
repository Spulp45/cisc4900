import sqlite3

conn = sqlite3.connect('test.db')
cur = conn.cursor()

# Enable foreign key support
conn.execute("PRAGMA foreign_keys = ON")

# Create tables and index
cur.executescript("""

CREATE TABLE IF NOT EXISTS track (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    track_hash TEXT NOT NULL UNIQUE
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
