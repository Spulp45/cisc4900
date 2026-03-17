import generate_secret
from backend import databaseFunctions
import leafletInstall

## First Time Tests
generateKeyResult = generate_secret.generate()

if generateKeyResult == generate_secret.SUCCESS:
    print("Successfully Created Random Key")
elif generateKeyResult == generate_secret.KEY_EXISTS:
    print("Key already exists. Skipping this step...")


databaseResult = databaseFunctions.createDatabase()
if databaseResult == databaseFunctions.DATABASE_EXISTS:
    print("Database already exists, skipping create database..")
elif databaseResult == databaseFunctions.SUCCESS:
    print("Database creation success!")
else:
    print("Failed to create database, unknown error. Exiting Program")
    exit()

leafletResult = leafletInstall.download_leaflet()

if leafletResult == leafletInstall.SUCCESS:
    print("Leaflet downloaded successfully")
else:
    print("Leaflet was not downloaded correctly")
# Import flask only after checking if everything is ok

from app import app 

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)