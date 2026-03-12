import os
import json

SECRET_FILE = "secret.json"
SUCCESS = 0
KEY_EXISTS = 1

default_config = {
    "SECRET_KEY": None
}

def generate() -> int:
    """Generate a persistent secret key for flask, returns different error codes if something goes wrong"""
    
    # Create file if it doesn't exist
    if not os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, "w") as f:
            json.dump(default_config, f, indent=4)
        print(f"{SECRET_FILE} created with default values.")

    # Load config
    with open(SECRET_FILE, "r") as f:
        config = json.load(f)

    # Generate key if missing
    if not config.get("SECRET_KEY"):
        print("No key found, generating a new random one...")
        config["SECRET_KEY"] = os.urandom(32).hex()
        with open(SECRET_FILE, "w") as f:
            json.dump(config, f, indent=4)
        print(f"Generated new secret key and updated {SECRET_FILE}")
        return SUCCESS, bytes.fromhex(config["SECRET_KEY"])

    
    return KEY_EXISTS