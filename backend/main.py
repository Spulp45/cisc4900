import parser
import databaseFunctions

#python .\.venv\Scripts\gpxinfo your_file.gpx
#track = parser.getGPX("backend/20250612_Morning.gpx")
#track2 = parser.getGPX("backend/20250613_Morning-MeanSeaLevel.gpx")
track3 = parser.getGPX("20260205.gpx")


test1 = databaseFunctions.get_all_track_points()

test2 = databaseFunctions.get_all_tracks()


test3 = databaseFunctions.get_track_with_track_points_by_id('1')


# This is the one you probably gonna use the most to get info
test4 = databaseFunctions.get_trackpoints('2', 'speed')

hash =  track3.track_hash()
# for current in test4:
#     print("Speed: ", current, "m/s")

print("speed: " + str(databaseFunctions.avg_speed(hash)))