from backend import parser
from backend import databaseFunctions


daPoint = parser.getGPX("testGPX/1.0/20250926.gpx")


print(daPoint.speed)