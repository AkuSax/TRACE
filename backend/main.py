import os
import shutil
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import List

from fastapi import (
    FastAPI, Depends, HTTPException, status, APIRouter,
    UploadFile, File
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models, schemas, security
from .database import engine, Base, get_db

# --- Lifespan and App Initialization ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables...")
    os.makedirs("uploads", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper Function (Now only used for registration/login) ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


# --- Authentication Router ---
auth_router = APIRouter(
    tags=["Authentication"]
)

@auth_router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
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
    # This is now much cleaner! The dependency does all the work.
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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_job = models.AnalysisJob(
        owner_id=current_user.id,
        status="pending",
        results=f"File '{file.filename}' uploaded successfully."
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return db_job

@analysis_router.get("/", response_model=List[schemas.AnalysisJob])
def get_user_analysis_jobs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    return db.query(models.AnalysisJob).filter(models.AnalysisJob.owner_id == current_user.id).all()


# --- Main App Configuration ---
app.include_router(auth_router)
app.include_router(analysis_router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the TRACE API"}