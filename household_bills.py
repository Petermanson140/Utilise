# Importing all the necessary libraries
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from create_database import get_db, Bill, User
from pydantic import BaseModel

# Import weather service and recommendation generators
from live_weather import get_live_weather
from llm_engine import (
    get_recommendations_version_a,
    get_recommendations_version_b,
)

router = APIRouter()


# Pydantic Schemas
class UserCreate(BaseModel):
    name: str
    postcode: str
    property_type: str
    num_bedrooms: int
    num_occupants: int
    tenure: str


class BillCreate(BaseModel):
    user_id: int
    month: str
    year: int
    electricity_kwh: float
    electricity_cost: float
    gas_kwh: float
    gas_cost: float
    water_litres: float
    water_cost: float


#Helper Utilities
def _build_user_dict(user: User) -> Dict[str, Any]:
    return {
        "property_type": user.property_type,
        "tenure": user.tenure,
        "num_bedrooms": user.num_bedrooms,
        "num_occupants": user.num_occupants,
        "postcode": user.postcode,
    }


def _build_latest_bill_dict(user_id: int, db: Session) -> Dict[str, Any]:
    bills = db.scalars(
        select(Bill).where(Bill.user_id == user_id).order_by(Bill.id.desc())
    ).all()
    
    if not bills:
        raise HTTPException(
            status_code=404,
            detail=f"No bill records found for user ID {user_id}. Please submit a bill first.",
        )
    
    latest_bill = bills[0]
    return {
        "electricity_kwh": latest_bill.electricity_kwh or 0.0,
        "electricity_cost": latest_bill.electricity_cost or 0.0,
        "gas_kwh": latest_bill.gas_kwh or 0.0,
        "gas_cost": latest_bill.gas_cost or 0.0,
        "water_litres": latest_bill.water_litres or 0.0,
        "water_cost": latest_bill.water_cost or 0.0,
    }


#User Endpoints 
@router.post("/users/create")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        name=user.name,
        postcode=user.postcode,
        property_type=user.property_type,
        num_bedrooms=user.num_bedrooms,
        num_occupants=user.num_occupants,
        tenure=user.tenure,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "message": "User created successfully",
        "user_id": new_user.id,
        "name": new_user.name,
    }


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


#Bill Endpoints
@router.post("/bills/submit")
def submit_bill(bill: BillCreate, db: Session = Depends(get_db)):
    user_exists = db.scalar(select(User).where(User.id == bill.user_id))
    if not user_exists:
        raise HTTPException(
            status_code=404,
            detail=f"Cannot submit bill. User ID {bill.user_id} does not exist.",
        )

    new_bill = Bill(
        user_id=bill.user_id,
        month=bill.month,
        year=bill.year,
        electricity_kwh=bill.electricity_kwh,
        electricity_cost=bill.electricity_cost,
        gas_kwh=bill.gas_kwh,
        gas_cost=bill.gas_cost,
        water_litres=bill.water_litres,
        water_cost=bill.water_cost,
    )
    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)
    return {"message": "Bill submitted successfully", "bill_id": new_bill.id}


@router.get("/bills/{user_id}")
def get_bills(user_id: int, db: Session = Depends(get_db)):
    bills = db.scalars(select(Bill).where(Bill.user_id == user_id)).all()
    if not bills:
        raise HTTPException(status_code=404, detail="No bills found for this user")
    return bills


@router.get("/bills/{user_id}/total")
def get_total_spending(user_id: int, db: Session = Depends(get_db)):
    bills = db.scalars(select(Bill).where(Bill.user_id == user_id)).all()
    if not bills:
        raise HTTPException(status_code=404, detail="No bills found for this user")

    total_electricity = sum(b.electricity_cost for b in bills if b.electricity_cost)
    total_gas = sum(b.gas_cost for b in bills if b.gas_cost)
    total_water = sum(b.water_cost for b in bills if b.water_cost)
    total = total_electricity + total_gas + total_water

    return {
        "user_id": user_id,
        "total_electricity": round(total_electricity, 2),
        "total_gas": round(total_gas, 2),
        "total_water": round(total_water, 2),
        "total_spending": round(total, 2),
    }


#Recommendation Endpoints
@router.get("/recommendations/{user_id}/version-a")
def get_version_a_recommendations(user_id: int, db: Session = Depends(get_db)):
    """Version A: Bill data + RAG guidance context only."""
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_profile = _build_user_dict(user)
    latest_bill = _build_latest_bill_dict(user.id, db)

    recommendations_text = get_recommendations_version_a(user_profile, latest_bill)

    return {
        "user_id": user_id,
        "version": "A",
        "recommendations": recommendations_text,
    }


@router.get("/recommendations/{user_id}/version-b")
async def get_version_b_recommendations(user_id: int, db: Session = Depends(get_db)):
    """Version B: Bill data + RAG guidance context + Live Weather integration."""
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_profile = _build_user_dict(user)
    latest_bill = _build_latest_bill_dict(user.id, db)

    #Live weather lookup through the user's postcode
    live_weather = await get_live_weather(user.postcode)

    recommendations_text = get_recommendations_version_b(
        user_profile, latest_bill, live_weather
    )

    return {
        "user_id": user_id,
        "version": "B",
        "postcode": user.postcode,
        "weather_snapshot": live_weather,
        "recommendations": recommendations_text,
    }
