import os

DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
API_KEY = os.environ.get("API_KEY")

def connect():
    return f"Connecting with {DATABASE_PASSWORD}"