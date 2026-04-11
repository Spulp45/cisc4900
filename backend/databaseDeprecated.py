# Deprecated functions had been copied here just in case we need them in the future,
# Used before multi user support in the app


def get_all_tracks() -> list[dict]:
    """Retrieve all rows from the track table."""
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM track")

        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
    
def get_track_with_track_points_by_id(id: str) -> dict[str, list[dict]]:
    """
    Get a track with all related track_points by using the track id

    Args:
        id (str): The id of the track to get

    Returns:
        dict[str, list[dict]]: A dictionary containing:
            - "track": A list of dictionaries representing a track row (SINGLE ROW ALWAYS)
            - "track_points": A list of dictionaries representing track_point rows
    """
 
    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()

        cur.execute("SELECT * FROM track WHERE id = ?", (id,))
        track_columns = [desc[0] for desc in cur.description]
        track_rows = [dict(zip(track_columns, row)) for row in cur.fetchall()]

        cur.execute("SELECT * FROM track_point WHERE track_id = ?", (id,))
        tp_columns = [desc[0] for desc in cur.description]
        track_point_rows = [dict(zip(tp_columns, row)) for row in cur.fetchall()]

        return {
            "track": track_rows,
            "track_points": track_point_rows
        }
    
def get_trackpoints(id: str, track_point_column: str) -> list[dict] | str:
    """
    Retrieve values from a specific column of track_point rows
    associated with a given track ID.

    Returns:
        list[dict]: [{"column_name": value}, ...]
        str: Error message if column is invalid
    """

    legal_arguments = [
        "id", "track_id", "lat", "lon", "ele", "timestamp", "course",
        "speed", "geoidheight", "src", "sat", "hdop", "vdop", "pdop"
    ]

    if track_point_column not in legal_arguments:
        return f"Invalid column name: {track_point_column}"

    with sqlite3.connect(DatabasePath) as conn:
        cur = conn.cursor()
        query = f"SELECT {track_point_column} FROM track_point WHERE track_id = ?"
        cur.execute(query, (id,))

        return [
            {track_point_column: row[0]}
            for row in cur.fetchall()
        ]