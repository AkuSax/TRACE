# backend/init_db.py
import os
from backend.database import Base, engine
from backend import models # Import models to ensure SQLAlchemy knows about your tables

def init_db():
    print("Attempting to create database tables via init-db service...")
    # This will create tables if they don't exist
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created or already exist.")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        # Optionally, re-raise the exception if you want the container to fail on db init error
        # raise

if __name__ == "__main__":
    init_db()