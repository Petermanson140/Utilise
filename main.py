from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from create_database import create_tables
import os

# Load environment variables from .env file
load_dotenv()

# Create the FastAPI app
app = FastAPI(
    title="Utilize",
    description="AI-Powered Household Bill Savings Advisor for London Households",
    version="1.0.0"
)

# Allow the React frontend to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables when the app starts
@app.on_event("startup")
def startup():
    create_tables()
    print("Database tables created")
    print("Utilize is running")

# Test route
@app.get("/")
def home():
    return {
        "message": "Utilize",
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
