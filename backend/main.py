from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base
from . import models

# Create all database tables on application startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This event handler will run when the application starts
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    yield


# Initialize the FastAPI application
app = FastAPI(lifespan=lifespan)


# Configure CORS middleware to allow all origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the TRACE API"}