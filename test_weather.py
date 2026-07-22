import asyncio
from live_weather import get_coordinates_from_postcode, get_live_weather

async def verify_weather():
    # Test postcodes across different parts of London
    test_postcodes = ["SW1A 1AA", "N6 6ND", "E1 6AN", "W1A 0AA", "SE1 7PB"]
    
    print("=" * 60)
    print("TESTING LIVE WEATHER ACCURACY")
    print("=" * 60)

    for postcode in test_postcodes:
        lat, lon = await get_coordinates_from_postcode(postcode)
        weather = await get_live_weather(postcode)
        
        print(f"Postcode: {postcode}")
        print(f"   ├─ Coordinates: Lat {lat}, Lon {lon}")
        print(f"   ├─ Live Data Flag: {weather.get('is_live_data')}")
        print(f"   ├─ Current Temp:  {weather.get('temperature_c')}°C (Feels like {weather.get('feels_like_c')}°C)")
        print(f"   ├─ Daily Range:   Low {weather.get('temp_min_c')}°C / High {weather.get('temp_max_c')}°C")
        print(f"   └─ Conditions:    Humidity {weather.get('humidity_pct')}%, Rain {weather.get('precipitation_mm')}mm")

if __name__ == "__main__":
    asyncio.run(verify_weather())