import parser
import databaseMethods


track = parser.getGPX("20250612_Morning.gpx")
track2 = parser.getGPX("20250613_Morning-MeanSeaLevel.gpx")
track3 = parser.getGPX("20260205.gpx")



databaseMethods.insert_track(track)
databaseMethods.insert_track(track2)
databaseMethods.insert_track(track3)