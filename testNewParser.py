from backend import parser
from backend import databaseFunctions
from backend import createDatabase


createDatabase.startDatabase()

track1 = parser.getGPX("testGPX/20250612_Morning.gpx")

track2 = parser.getGPX("testGPX/20260205.gpx")


databaseFunctions.insert_track(track1)


tracks = databaseFunctions.get_all_tracks()



