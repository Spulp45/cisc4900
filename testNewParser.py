from backend import parser
from backend import databaseFunctions

databaseFunctions.createDatabase()

track1 = parser.getGPX("testGPX/20250612_Morning.gpx")

track2 = parser.getGPX("testGPX/20260205.gpx")


databaseFunctions.insert_track(track1)
databaseFunctions.insert_track(track2)


# Get all tracks and track points
tracks = databaseFunctions.get_all_tracks()
track_points = databaseFunctions.get_all_track_points()

# Print track points for track_id = 2
for track_point in track_points:
    if track_point.track_id == 2:
        print("lat:", track_point.lat, "\tlon:", track_point.lon, "\tspeed:", track_point.speed)

# Print basic info about all tracks
for track in tracks:
    print("Name:", track.name, "\tHash:", track.track_hash)

# Show field names of a track point
field_names_list = tracks[0]._fields
print(field_names_list)
# Example output: ['id', 'track_id', 'lat', 'lon', 'ele', 'timestamp', 'course', 'speed', 'geoidheight', 'src', 'sat', 'hdop', 'vdop', 'pdop']

# Get a single track with its track points
data = databaseFunctions.get_track_with_track_points_by_id(1)

#Separate data because it comes as a dictionary
track = data['track'][0]           # only one because we only have one with ID 1
track_points2 = data['track_points']

# Print all track points for this track
for pt in track_points2:
    print("lat:", pt.lat, "\tlon:", pt.lon, "\tspeed:", pt.speed)

# Print basic info about the track itself
print("Name:", track.name, "\tStart Time:", track.start_time)


















