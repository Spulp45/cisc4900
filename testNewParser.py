from backend import parser
from backend import databaseFunctions
from backend import createDatabase


createDatabase.startDatabase()

track1 = parser.getGPX("backend/20250612_Morning.gpx")
track2 = parser.getGPX("backend/20260205.gpx")

 
print(databaseFunctions.insert_track(track2))

