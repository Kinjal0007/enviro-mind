from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
from app.services.copernicus_service import CopernicusService
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()
copernicus_service = CopernicusService()

@router.get("/air-quality/{latitude}/{longitude}")
async def get_air_quality(
    latitude: float,
    longitude: float,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get air quality data and AQI for a specific location
    """
    try:
        # Get air quality data from Copernicus
        air_quality_data = await copernicus_service.get_air_quality_data(latitude, longitude)
        
        # Calculate AQI
        aqi_result = copernicus_service.calculate_aqi(air_quality_data)
        
        return {
            "status": "success",
            "data": {
                "air_quality": air_quality_data,
                "aqi": aqi_result
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather-warnings/{latitude}/{longitude}")
async def get_weather_warnings(
    latitude: float,
    longitude: float,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get weather warnings for a specific location
    """
    try:
        # Get weather data from Copernicus
        weather_data = await copernicus_service.get_weather_data(latitude, longitude)
        
        # Calculate weather warnings
        warnings = copernicus_service.calculate_weather_warnings(weather_data)
        
        return {
            "status": "success",
            "data": {
                "weather": weather_data,
                "warnings": warnings
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/environmental-status/{latitude}/{longitude}")
async def get_environmental_status(
    latitude: float,
    longitude: float,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get comprehensive environmental status including air quality and weather warnings
    """
    try:
        # Get both air quality and weather data
        air_quality_data = await copernicus_service.get_air_quality_data(latitude, longitude)
        weather_data = await copernicus_service.get_weather_data(latitude, longitude)
        
        # Calculate AQI and warnings
        aqi_result = copernicus_service.calculate_aqi(air_quality_data)
        warnings = copernicus_service.calculate_weather_warnings(weather_data)
        
        return {
            "status": "success",
            "data": {
                "air_quality": air_quality_data,
                "aqi": aqi_result,
                "weather": weather_data,
                "warnings": warnings,
                "timestamp": weather_data.get("timestamp")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 