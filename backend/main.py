from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models, schemas, security
from .database import engine, Base, get_db

# --- Lifespan and App Initialization ---

# Create all database tables on application startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    yield

# Initialize the FastAPI application
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Helper Function to Get User by Email ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


# --- Authentication Router ---
auth_router = APIRouter()

@auth_router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint for user registration.
    """
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
    """
    Endpoint for user login. Returns a JWT access token.
    Takes form data with 'username' (which is the email) and 'password'.
    """
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

# Include the auth router in the main app
app.include_router(auth_router)


# --- Root Endpoint ---
@app.get("/")
def read_root():
    """
    Root endpoint for the TRACE API.
    """
    return {"message": "Welcome to the TRACE API"}

# --- Dependency to get current user (for protected routes later) ---
@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(token_data: security.TokenData = Depends(security.get_current_user), db: Session = Depends(get_db)):
    """
    Example of a protected endpoint.
    It uses the get_current_user dependency to ensure the user is authenticated.
    """
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user