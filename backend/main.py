import os
import uuid
import shutil
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import List, Union

from fastapi import (
    FastAPI, Depends, HTTPException, status, APIRouter,
    UploadFile, File
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from celery.result import AsyncResult

# --- Local Imports ---
from . import models, schemas, security
from .database import engine, Base, get_db
from .worker import run_trace_pipeline, add_numbers  # Import Celery tasks

# --- Lifespan and App Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes the application, creating database tables and upload directories."""
    print("Creating database tables...")
    os.makedirs("uploads", exist_ok=True)
    yield

app = FastAPI(lifespan=lifespan)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper Function ---
def get_user_by_email(db: Session, email: str):
    """Fetches a user by their email address."""
    return db.query(models.User).filter(models.User.email == email).first()

# --- Authentication Router ---
auth_router = APIRouter(
    tags=["Authentication"]
)

@auth_router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Creates a new user in the database."""
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@auth_router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticates a user and returns a JWT access token."""
    user = get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(security.get_current_user)):
    """Returns the details of the currently authenticated user."""
    return current_user

# --- Analysis Job Router ---
analysis_router = APIRouter(
    prefix="/analyses",
    tags=["Analyses"],
    dependencies=[Depends(security.get_current_user)]
)

@analysis_router.post("/", response_model=schemas.AnalysisJob, status_code=status.HTTP_201_CREATED)
async def create_analysis_job(
    file: UploadFile = File(...),
    # A simple way to get data type from the user. Could be a form field.
    data_type: str = "WGS", 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Handles file uploads, creates an analysis job record, and triggers the pipeline.
    """
    # Sanitize filename and create a unique ID for this run
    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in ('.', '_', '-')).strip()
    unique_id = str(uuid.uuid4().hex)[:8]
    sample_id = f"{os.path.splitext(safe_filename)[0]}_{unique_id}"
    
    file_path = os.path.join("uploads", f"{sample_id}_{safe_filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_job = models.AnalysisJob(
        owner_id=current_user.id,
        status="pending",
        results=f"File '{file.filename}' uploaded. Job is queued."
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    # Trigger the bioinformatics pipeline via Celery
    run_trace_pipeline.delay(
        job_id=db_job.id, 
        input_file_path=file_path,
        sample_id=sample_id,
        data_type=data_type
    )
    
    return db_job

@analysis_router.get("/", response_model=List[schemas.AnalysisJob])
def get_user_analysis_jobs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """Retrieves all analysis jobs for the current user."""
    return db.query(models.AnalysisJob).filter(models.AnalysisJob.owner_id == current_user.id).all()

@analysis_router.delete("/{job_id}", status_code=status.HTTP_200_OK)
def delete_analysis_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Deletes an analysis job by its ID.
    """
    # First, find the job in the database
    db_job = db.query(models.AnalysisJob).filter(models.AnalysisJob.id == job_id).first()

    # If the job doesn't exist, raise a 404 error
    if db_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    # CRUCIAL: Verify that the user deleting the job is the one who owns it
    if db_job.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this job")

    # If all checks pass, delete the job and commit the change
    db.delete(db_job)
    db.commit()

    return {"message": f"Successfully deleted job {job_id}"}

# --- NEW: Celery Task Router ---
task_router = APIRouter(
    prefix="/tasks",
    tags=["Celery Tasks"]
)

class TaskResponse(BaseModel):
    task_id: str

@task_router.post("/test-task/", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
def run_test_task():
    """
    Triggers the simple 'add_numbers' background task.
    
    This is an example endpoint to demonstrate Celery integration.
    """
    task = add_numbers.delay(5, 10)
    return {"task_id": task.id}

class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: Union[int, None] = None

@task_router.get("/status/{task_id}", response_model=TaskStatus)
def get_task_status(task_id: str):
    """
    Retrieves the status and result of a Celery task by its ID.
    """
    task_result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }

# --- Main App Configuration ---
# Include all the routers in the main FastAPI application
app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(task_router) # Add the new task router

@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint for the TRACE API."""
    return {"message": "Welcome to the TRACE API"}