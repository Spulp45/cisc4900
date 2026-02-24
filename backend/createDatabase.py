import sqlite3

def startDatabase():
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
