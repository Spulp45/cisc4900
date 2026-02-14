import parser
import databaseFunctions

# track = parser.getGPX("20250612_Morning.gpx")
# track2 = parser.getGPX("20250613_Morning-MeanSeaLevel.gpx")
# track3 = parser.getGPX("20260205.gpx")


track = parser.getGPX("20260205.gpx")

databaseFunctions.insert_track(track)

hash = track.track_hash()

# databaseFunctions.delete_track_by_hash(hash)