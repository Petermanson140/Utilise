"""
Consolidated Recommendations Route
Orchestrates DB lookup, Live Weather fetching, and LLM Recommendation generation (Version A & Version B).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

# Database dependencies and models
from create_database import get_db, User, Bill

# External services and LLM generation functions
from live_weather import get_live_weather
from llm_engine import (
    get_recommendations_version_a,
    get_recommendations_version_b,
)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/{user_id}")
async def get_all_recommendations(user_id: int, db: Session = Depends(get_db)):
    """
    Unified endpoint:
    1. Fetches User Profile & Latest Bill from DB
    2. Fetches Live Weather for the User's Postcode
    3. Runs LLM Version A (Bill Data + RAG)
    4. Runs LLM Version B (Bill Data + Live Weather + RAG)
    5. Returns consolidated JSON payload with both versions
    """
    
    # ── 1. Fetch User from Database ─────────────────────────────
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=404, 
            detail=f"User with ID {user_id} not found."
        )

    # ── 2. Fetch Latest Submitted Bill ──────────────────────────
    latest_bill = db.scalar(
        select(Bill)
        .where(Bill.user_id == user_id)
        .order_by(Bill.id.desc())
    )
    if not latest_bill:
        raise HTTPException(
            status_code=404,
            detail=f"No bill records found for User ID {user_id}. Please submit a bill first."
        )

    # Format user profile dictionary
    user_profile = {
        "property_type": user.property_type,
        "tenure": user.tenure,
        "num_bedrooms": user.num_bedrooms,
        "num_occupants": user.num_occupants,
        "postcode": user.postcode,
    }

    # Format bill dictionary
    bills_data = {
        "electricity_kwh": latest_bill.electricity_kwh or 0.0,
        "electricity_cost": latest_bill.electricity_cost or 0.0,
        "gas_kwh": latest_bill.gas_kwh or 0.0,
        "gas_cost": latest_bill.gas_cost or 0.0,
        "water_litres": latest_bill.water_litres or 0.0,
        "water_cost": latest_bill.water_cost or 0.0,
    }

    # ── 3. Fetch Live Weather Data ──────────────────────────────
    weather_data = await get_live_weather(user.postcode)

    # ── 4. Generate LLM Recommendations ─────────────────────────
    recommendation_a = get_recommendations_version_a(user_profile, bills_data)
    recommendation_b = get_recommendations_version_b(user_profile, bills_data, weather_data)

    # ── 5. Return Unified Response ──────────────────────────────
    return {
        "status": "success",
        "user_id": user_id,
        "user_profile": user_profile,
        "latest_bill": bills_data,
        "weather_snapshot": weather_data,
        "recommendations": {
            "version_a": recommendation_a,
            "version_b": recommendation_b
        }
    }