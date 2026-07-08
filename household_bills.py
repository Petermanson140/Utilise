#Importing all the necessary libraries
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from create_database import get_db, Bill, User
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# What a user profile looks like
class UserCreate(BaseModel):
    name: str
    postcode: str
    property_type: str
    num_bedrooms: int
    num_occupants: int
    tenure: str

# What bill data looks like
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

# Create a new user profile
@router.post("/users/create")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        name=user.name,
        postcode=user.postcode,
        property_type=user.property_type,
        num_bedrooms=user.num_bedrooms,
        num_occupants=user.num_occupants,
        tenure=user.tenure
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "message": "User created successfully",
        "user_id": new_user.id,
        "name": new_user.name
    }

# Get a user profile
@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

#Submit bill data
@router.post("/bills/submit")
def submit_bill(bill: BillCreate, db: Session = Depends(get_db)):
    new_bill = Bill(
        user_id=bill.user_id,
        month=bill.month,
        year=bill.year,
        electricity_kwh=bill.electricity_kwh,
        electricity_cost=bill.electricity_cost,
        gas_kwh=bill.gas_kwh,
        gas_cost=bill.gas_cost,
        water_litres=bill.water_litres,
        water_cost=bill.water_cost
    )
    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)
    return {
        "message": "Bill submitted successfully",
        "bill_id": new_bill.id
    }

# Get all bills for a user
@router.get("/bills/{user_id}")
def get_bills(user_id: int, db: Session = Depends(get_db)):
    bills = db.query(Bill).filter(Bill.user_id == user_id).all()
    if not bills:
        raise HTTPException(status_code=404, detail="No bills found for this user")
    return bills

# Get total spending for a user
@router.get("/bills/{user_id}/total")
def get_total_spending(user_id: int, db: Session = Depends(get_db)):
    bills = db.query(Bill).filter(Bill.user_id == user_id).all()
    if not bills:
        raise HTTPException(status_code=404, detail="No bills found")
    
    total_electricity = sum(b.electricity_cost for b in bills)
    total_gas = sum(b.gas_cost for b in bills)
    total_water = sum(b.water_cost for b in bills)
    total = total_electricity + total_gas + total_water

    return {
        "user_id": user_id,
        "total_electricity": round(total_electricity, 2),
        "total_gas": round(total_gas, 2),
        "total_water": round(total_water, 2),
        "total_spending": round(total, 2)
    }
