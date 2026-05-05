import pytest
import os
import shutil


from app import app as flask_app
from backend import databaseFunctions


@pytest.fixture(scope="session")
def app():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    test_config = {
        "SECRET_KEY": "test_secret",
        "UPLOAD_DIRECTORY": os.path.join(BASE_DIR, "test_uploads"),
        "TEMP_FOLDER": os.path.join(BASE_DIR, "test_temp"),
        "DATABASE_PATH": os.path.join(BASE_DIR, "test_database.db"),
        "ALLOWED_EXTENSIONS": ['gpx'],
        "TESTING": True
    }
    flask_app.config.update(test_config)
    flask_app.secret_key = test_config["SECRET_KEY"]

    os.makedirs(test_config["UPLOAD_DIRECTORY"], exist_ok=True)
    os.makedirs(test_config["TEMP_FOLDER"], exist_ok=True)

    if not os.path.exists(test_config["DATABASE_PATH"]):
        databaseFunctions.createDatabase(test_config["DATABASE_PATH"])

    yield flask_app

    # delete database
    if os.path.exists(test_config['DATABASE_PATH']):
        os.remove(test_config['DATABASE_PATH'])

    # delete uploaded files
    if os.path.exists(test_config['UPLOAD_DIRECTORY']):
        shutil.rmtree(test_config['UPLOAD_DIRECTORY'])

    # delete temp files
    if os.path.exists(test_config['UPLOAD_DIRECTORY']):
        shutil.rmtree(test_config['UPLOAD_DIRECTORY'])
      
    # delete temp_folder  
    if os.path.exists(test_config['TEMP_FOLDER']):
        shutil.rmtree(test_config['TEMP_FOLDER'])

@pytest.fixture
def client(app):
    return app.test_client()