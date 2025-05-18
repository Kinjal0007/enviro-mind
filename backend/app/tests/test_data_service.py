import asyncio
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.copernicus_data_service import CopernicusDataService

async def test_data_service():
    try:
        print("Initializing Copernicus Data Service...")
        service = CopernicusDataService()
        
        # Test coordinates (New York City)
        latitude = 40.7128
        longitude = -74.0060
        
        print("\nFetching weather data...")
        weather = await service.get_weather_data(latitude, longitude)
        
        print("\nWeather Data:")
        print(f"Temperature: {weather['temperature']:.1f}°C")
        print(f"Humidity: {weather['humidity']:.1f}%")
        print(f"Precipitation: {weather['precipitation']:.1f} mm")
        print(f"UV Index: {weather['uv_index']:.1f}")
        print(f"Timestamp: {weather['timestamp']}")
            
        return True
        
    except Exception as e:
        print(f"Error testing data service: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting Copernicus Data Service test...")
    asyncio.run(test_data_service()) 