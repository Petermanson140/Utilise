import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from create_database import create_tables
from household_bills import router as household_bills_router
from recommendations import router as recommendations_router


# Load environment variables from .env file
load_dotenv()


# UPDATED: Modern lifespan context manager to replace the deprecated @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Actions to run on startup
    create_tables()
    print("Database tables verified and created successfully.")
    print("Utilise Backend is up and running.")
    yield
    # Actions to run on shutdown (if needed) can be placed here
    print("Shutting down Utilise Backend.")


# Create the FastAPI app with lifespan management
app = FastAPI(
    title="Utilize",
    description="AI-Driven Household Bill Savings Advisor for London Households",
    version="1.0.0",
    lifespan=lifespan
)

# Allow the React frontend to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test route
@app.get("/")
def home():
    return {
        "message": "Welcome to Utilize API",
        "status": "running",
        "version": "1.0.0"
    }

# Health check route
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": "Utilize"
    }

# Include bill routes under the global API prefix
app.include_router(household_bills_router, prefix="/api", tags=["Household Bills"])
app.include_router(recommendations_router, prefix="/api", tags=["Recommendations"])
