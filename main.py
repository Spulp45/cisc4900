import parser

track = parser.getGPX("20260205.gpx")

print(track.name)
print(track.track_hash())