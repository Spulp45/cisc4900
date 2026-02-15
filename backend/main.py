import parser
import databaseFunctions

track = parser.getGPX("backend/20250612_Morning.gpx")
track2 = parser.getGPX("backend/20250613_Morning-MeanSeaLevel.gpx")
track3 = parser.getGPX("backend/20260205.gpx")


test1 = databaseFunctions.get_all_track_points()

test2 = databaseFunctions.get_all_tracks()


test3 = databaseFunctions.get_track_with_track_points_by_id('1')


# This is the one you probably gonna use the most to get info
test4 = databaseFunctions.get_trackpoints('1', 'speed')

for current in test4:
    print("Speed: ", current, "m/s")