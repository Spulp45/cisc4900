from backend import databaseFunctions
from app import app

result = databaseFunctions.createDatabase()

if(result == databaseFunctions.DATABASE_EXISTS):
    print("Database already exists, skipping create database..")
    pass
if(result == 0):
    print("Database creation success!")

if __name__ == "__main__":
    app.run(debug=True, port=5000)