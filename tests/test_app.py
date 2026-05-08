import io
import uuid
import os
from backend import databaseFunctions


def login(client, username, password):
    """Because most of our flask routes have @login_required decorator;
        we must login before doing any tests
    """
    client.post('/register', data={
        'username': username,
        'password': password
    })
    client.post('/login', data={
        'username': username,
        'password': password
    })


def test_login_page_loads(client):
    """Test if login page loads correctly"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data


def test_registration_and_login(client):
    """Test if registartion and login afterwards works"""
    username = f"user_{uuid.uuid4()}"
    password = "testPassword"

    # Register
    client.post('/register', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

    # Login
    response = client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

    assert "home" in response.request.path.lower()
    assert username.encode() in response.data


def test_login_required_middleware(client):
    """Test if non-authenticated ussers get redirected to login page"""
    response = client.get('/home', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location


def test_invalid_login(client):
    """Test if invalid login gets rejected"""
    username = f"user_{uuid.uuid4()}"

    client.post('/register', data={
        'username': username,
        'password': 'pw1'
    })

    response = client.post('/login', data={
        'username': username,
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert b"Invalid Credentials" in response.data


def test_upload_unauthorized(client):
    """Test if unauthorized users cannot upload"""
    data = {
        'files': (io.BytesIO(b"fake gpx content"), 'test.gpx')
    }

    response = client.post('/upload', data=data, follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.location
 
def test_upload_real_gpx(client, app):
    username = f"user_{uuid.uuid4()}"
    password = "pw"
    

    login(client, username, password)

    gpx_path = os.path.join("demoGPX", "20260307151338.gpx")

    with open(gpx_path, "rb") as f:
        data = {
            "files": (f, "20260307151338.gpx")
        }

        response = client.post(
        "/upload",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=True
        )

        assert response.status_code == 200
        assert b"Upload Results" in response.data
        assert b"was uploaded successfully" in response.data

        user_id = databaseFunctions.verify_user(
            username,
            password,
            app.config["DATABASE_PATH"]
        )
        
    tracks = databaseFunctions.get_tracks(user_id, app.config["DATABASE_PATH"])
    assert len(tracks) >= 1

    upload_dir = app.config["UPLOAD_DIRECTORY"]
    files = os.listdir(upload_dir)

    assert any(f.endswith(".gpx") for f in files)
    
def test_upload_duplicate(client, app):
    username = f"user_{uuid.uuid4}"
    password = "pw"
    
    login(client, username, password)
    
    gpx_path = os.path.join("demoGPX", "20260307151338.gpx")

    for _ in range(2):
        with open(gpx_path, "rb") as f:
            client.post(
                "/upload",
                data={"files": (f, "20260307151338.gpx")},
                content_type="multipart/form-data"
            )

    response = client.post(
        "/upload",
        data={"files": (open(gpx_path, "rb"), "20260307151338.gpx")},
        content_type="multipart/form-data"
    )

    assert b"already exists" in response.data

def test_upload_corrupted_gpx(client):
    username = f"user_{uuid.uuid4()}"
    password = "pw"

    login(client, username, password)

    bad_path = os.path.join("demoGPX", "corruptedFile.gpx")

    with open(bad_path, "rb") as f:
        response = client.post(
            "/upload",
            data={"files": (f, "corruptedFile.gpx")},
            content_type="multipart/form-data"
        )

    assert b"file is likely corrupted" in response.data
    

def login_and_get_user_id(client, app, username, password):
    # register
    client.post('/register', data={
        'username': username,
        'password': password
    })

    # login
    client.post('/login', data={
        'username': username,
        'password': password
    })

    # get real user_id from DB
    return databaseFunctions.verify_user(
        username,
        password,
        app.config["DATABASE_PATH"]
    )

def test_download_track_success(client, app):
    username = f"user_{uuid.uuid4()}"
    password = "pw"

    # login + get real user_id
    user_id = login_and_get_user_id(client, app, username, password)

    # upload GPX
    gpx_path = os.path.join("demoGPX", "20260307152413.gpx")

    with open(gpx_path, "rb") as f:
        client.post(
            "/upload",
            data={"files": (f, "20260307152413.gpx")},
            content_type="multipart/form-data",
            follow_redirects=True
        )

    # fetch tracks
    tracks = databaseFunctions.get_tracks(user_id, app.config['DATABASE_PATH'])

    assert len(tracks) > 0, "No tracks found for user"

    track_id = tracks[0]["id"]

    # download test
    response = client.get(f"/download/{track_id}", follow_redirects=True)

    assert response.status_code == 200
    assert response.data
    

def test_delete_track_success(client, app):
    username = "user1"
    password = "pw"

    user_id = login_and_get_user_id(client, app, username, password)

    # upload file first
    with open("demoGPX/20260307155153.gpx", "rb") as f:
        client.post("/upload", data={"files": (f, "20260307155153.gpx")},
                    content_type="multipart/form-data",
                    follow_redirects=True)

    tracks = databaseFunctions.get_tracks(user_id, app.config['DATABASE_PATH'])
    track_id = tracks[0]["id"]

    response = client.post(f"/delete/{track_id}", follow_redirects=True)

    assert response.status_code == 200

    # confirm deletion
    tracks_after = databaseFunctions.get_tracks(user_id, app.config['DATABASE_PATH'])
    assert len(tracks_after) == 0
    
    
    
def test_delete_track_db_error(client, monkeypatch):
    login(client, "user1", "pw")

    def fake_delete(*args, **kwargs):
        return databaseFunctions.DELETE_ERROR

    monkeypatch.setattr(databaseFunctions, "delete_track_by_id", fake_delete)

    response = client.post("/delete/1", follow_redirects=True)

    assert response.status_code == 200
    assert b"Could not delete track" in response.data
    
def test_delete_file_error(client, monkeypatch):
    login(client, "user2", "pw")

    def fake_delete(*args, **kwargs):
        return databaseFunctions.DELETE_FILE_ERROR

    monkeypatch.setattr(databaseFunctions, "delete_track_by_id", fake_delete)

    response = client.post("/delete/1", follow_redirects=True)

    assert response.status_code == 200
    assert b"Could not delete file associated" in response.data