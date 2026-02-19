from backend import parser
from backend import databaseFunctions
from backend import createDatabase

#python .\.venv\Scripts\gpxinfo your_file.gpx

#track = parser.getGPX("backend/20250612_Morning.gpx")
track2 = parser.getGPX("20250612_Afternoon.gpx")
#track3 = parser.getGPX("20260205.gpx")

track = parser.getGPX("backend/20250612_Morning.gpx")
track2 = parser.getGPX("backend/20250613_Morning-MeanSeaLevel.gpx")
track3 = parser.getGPX("backend/20260205.gpx")



test1 = databaseFunctions.get_all_track_points()

test2 = databaseFunctions.get_all_tracks()

test3 = databaseFunctions.get_track_with_track_points_by_id('1')


# This is the one you probably gonna use the most to get info
#test4 = databaseFunctions.get_trackpoints('2', 'speed')


hash =  track2.track_hash()
# for current in test4:
#     print("Speed: ", current, "m/s")

#print(databaseFunctions.get_trackpoints(2,"timestamp")) 
print(databaseFunctions.duration(2)) 

databaseFunctions.delete_track_by_hash(hash)

#hash =  track3.track_hash()
# for current in test4:
#     print("Speed: ", current, "m/s")

#print("speed: " + str(databaseFunctions.avg_speed(hash)))

rows = databaseFunctions.get_track_by_name("20260205.gpx")

print(rows)

