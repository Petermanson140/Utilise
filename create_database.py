from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Column, ForeignKey, String, Float, DateTime, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship, Mapped, mapped_column
from sqlalchemy.sql import func

# Create SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./utilize.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Needed for SQLite in multi-threaded apps (like FastAPI)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# UPDATED: Modern SQLAlchemy 2.0 Base style
class Base(DeclarativeBase):
    pass

# User household profile table
class User(Base):
    __tablename__ = "users"

    # UPDATED: Fully compliant 2.0 type-hinted columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String)
    postcode: Mapped[Optional[str]] = mapped_column(String)
    property_type: Mapped[Optional[str]] = mapped_column(String)  # flat, house, terraced etc
    num_bedrooms: Mapped[Optional[int]] = mapped_column(Integer)
    num_occupants: Mapped[Optional[int]] = mapped_column(Integer)
    tenure: Mapped[Optional[str]] = mapped_column(String)  # rented or owned
    
    # UPDATED: Secure, timezone-aware default timestamp using database time
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # UPDATED: Type-hinted modern relationship mapping
    bills: Mapped[List["Bill"]] = relationship("Bill", back_populates="user", cascade="all, delete-orphan")
    recommendations: Mapped[List["Recommendation"]] = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")


#Bill data table
class Bill(Base):
    __tablename__ = "bills"

    # UPDATED: Fully compliant 2.0 type-hinted columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    month: Mapped[Optional[str]] = mapped_column(String)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    electricity_kwh: Mapped[Optional[float]] = mapped_column(Float)
    electricity_cost: Mapped[Optional[float]] = mapped_column(Float)
    gas_kwh: Mapped[Optional[float]] = mapped_column(Float)
    gas_cost: Mapped[Optional[float]] = mapped_column(Float)
    water_litres: Mapped[Optional[float]] = mapped_column(Float)
    water_cost: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Connects back to the parent User object
    user: Mapped["User"] = relationship("User", back_populates="bills")


# Recommendations table
class Recommendation(Base):
    __tablename__ = "recommendations"

    # UPDATED: Fully compliant 2.0 type-hinted columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    version: Mapped[Optional[str]] = mapped_column(String)  # A or B
    recommendation_text: Mapped[Optional[str]] = mapped_column(String)
    estimated_saving: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Connects back to the parent User object
    user: Mapped["User"] = relationship("User", back_populates="recommendations")

    #Live weather table
class Weather(Base):
    __tablename__ = "live_weather"

    id = Column(Integer, primary_key=True, index=True)
    postcode = Column(String)
    current_temp = Column(Float)
    conditions = Column(String)
    forecast = Column(String)
    hdd_current = Column(Float)
    hdd_average = Column(Float)
    hdd_comparison = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    #Monthly forecasting table
class Forecast(Base):
    __tablename__ = "monthly_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    month = Column(String)
    year = Column(Integer)
    predicted_electricity_cost = Column(Float)
    predicted_gas_cost = Column(Float)
    predicted_water_cost = Column(Float)
    predicted_total_cost = Column(Float)
    is_most_expensive = Column(String)
    is_least_expensive = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

#Creating all tables
def create_tables():
    Base.metadata.create_all(bind=engine)


#Receiving the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
