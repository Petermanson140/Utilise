from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./utilize.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# User household profile table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    postcode = Column(String)
    property_type = Column(String)  # flat, house, terraced etc
    num_bedrooms = Column(Integer)
    num_occupants = Column(Integer)
    tenure = Column(String)  # rented or owned
    created_at = Column(DateTime, default=datetime.utcnow)

# Bill data table
class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    month = Column(String)
    year = Column(Integer)
    electricity_kwh = Column(Float)
    electricity_cost = Column(Float)
    gas_kwh = Column(Float)
    gas_cost = Column(Float)
    water_litres = Column(Float)
    water_cost = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

# Recommendations table
class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    version = Column(String)  # A or B
    recommendation_text = Column(String)
    estimated_saving = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
