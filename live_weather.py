"""
Live Weather Service for Version B Recommendations
Uses postcodes.io (UK Postcode Lookup) + Open-Meteo (Free Live Weather API)
"""

import httpx
from typing import Dict, Any, Tuple, Optional

# Default fallback coordinates: Central London
DEFAULT_LAT = 51.5074
DEFAULT_LON = -0.1278


async def get_coordinates_from_postcode(postcode: str) -> Tuple[float, float]:
    """Converts a UK postcode (e.g. 'SW1A 1AA') to latitude/longitude."""
    clean_postcode = postcode.replace(" ", "").strip().upper()
    url = f"https://api.postcodes.io/postcodes/{clean_postcode}"
    
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json().get("result", {})
                lat = data.get("latitude", DEFAULT_LAT)
                lon = data.get("longitude", DEFAULT_LON)
                return lat, lon
    except Exception as exc:
        print(f"⚠️ Postcode lookup failed ({exc}), falling back to Central London coordinates.")
        
    return DEFAULT_LAT, DEFAULT_LON


async def get_live_weather(postcode: Optional[str] = None) -> Dict[str, Any]:
    """Fetches real-time weather data for a given UK postcode or default London location."""
    if postcode:
        lat, lon = await get_coordinates_from_postcode(postcode)
    else:
        lat, lon = DEFAULT_LAT, DEFAULT_LON

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "Europe/London"
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                daily = data.get("daily", {})

                return {
                    "temperature_c": round(current.get("temperature_2m", 15.0), 1),
                    "feels_like_c": round(current.get("apparent_temperature", 14.0), 1),
                    "humidity_pct": current.get("relative_humidity_2m", 70),
                    "wind_speed_kmh": round(current.get("wind_speed_10m", 10.0), 1),
                    "precipitation_mm": current.get("precipitation", 0.0),
                    "temp_max_c": round(daily.get("temperature_2m_max", [18.0])[0], 1),
                    "temp_min_c": round(daily.get("temperature_2m_min", [10.0])[0], 1),
                    "is_live_data": True,
                    "location_lat_lon": (lat, lon)
                }
    except Exception as exc:
        print(f"⚠️ Weather API fetch failed ({exc}), returning fallback baseline.")

    # Fallback response if the API call fails or times out
    return {
        "temperature_c": 14.0,
        "feels_like_c": 13.0,
        "humidity_pct": 75,
        "wind_speed_kmh": 12.0,
        "precipitation_mm": 0.0,
        "temp_max_c": 17.0,
        "temp_min_c": 9.0,
        "is_live_data": False,
        "location_lat_lon": (DEFAULT_LAT, DEFAULT_LON)
    }