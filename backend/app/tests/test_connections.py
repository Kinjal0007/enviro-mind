import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.copernicus_data_service import CopernicusDataService

async def test_mongodb():
    try:
        print("\nTesting MongoDB connection...")
        client = AsyncIOMotorClient(os.getenv("DATABASE_URL"))
        db = client.get_default_database()
        collections = await db.list_collection_names()
        print("Successfully connected to MongoDB!")
        print(f"Available collections: {collections}")
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        return False

async def test_copernicus():
    try:
        print("\nTesting Copernicus API connection...")
        service = CopernicusDataService()
        
        # Test coordinates (New York City)
        latitude = 40.7128
        longitude = -74.0060
        
        # Use a date we know is available (5 days ago)
        weather = await service.get_weather_data(latitude, longitude)
        
        print("\nWeather Data:")
        print(f"Temperature: {weather['temperature']:.1f}°C" if weather['temperature'] is not None else "Temperature: N/A")
        print(f"Humidity: {weather['humidity']:.1f}%" if weather['humidity'] is not None else "Humidity: N/A")
        print(f"Precipitation: {weather['precipitation']:.1f} mm" if weather['precipitation'] is not None else "Precipitation: N/A")
        print(f"UV Index: {weather['uv_index']:.1f}" if weather['uv_index'] is not None else "UV Index: N/A")
        print(f"Timestamp: {weather['timestamp']}")
        
        return True
    except Exception as e:
        print(f"Error testing Copernicus API: {str(e)}")
        return False

async def run_tests():
    # Load environment variables
    load_dotenv()
    
    print("Starting connection tests...")
    
    # Test MongoDB
    mongo_success = await test_mongodb()
    
    # Test Copernicus
    copernicus_success = await test_copernicus()
    
    # Print summary
    print("\nTest Summary:")
    print(f"MongoDB Connection: {'✅ Success' if mongo_success else '❌ Failed'}")
    print(f"Copernicus API: {'✅ Success' if copernicus_success else '❌ Failed'}")
    
    return mongo_success and copernicus_success

if __name__ == "__main__":
    asyncio.run(run_tests()) 