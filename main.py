import parser

list = parser.getGPX('20250612_Morning.gpx')

import matplotlib.pyplot as plt

lats = [p.lat for p in list]
lons = [p.lon for p in list]
alt = [p.geoidheight for p in list]
speeds = [p.speed for p in list]

plt.figure(figsize=(8, 8))
plt.plot(lons, lats, "-o", markersize=2)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("GPS Track")
plt.axis("equal")
plt.grid(True)
plt.show()

plt.figure(figsize=(8, 8))
plt.scatter(lons, lats, c=speeds, s=5, cmap="viridis")
plt.colorbar(label="Speed (m/s)")
plt.axis("equal")
plt.title("Track Colored by Speed")
plt.show()

