from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from app.services.environmental_data import environmental_data_service

router = APIRouter()

@router.get("/air-quality/{lat}/{lon}")
async def get_air_quality(lat: float, lon: float) -> Dict:
    """
    Get air quality data for a specific location
    """
    try:
        return await environmental_data_service.get_air_quality(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/heat-stress/{lat}/{lon}")
async def get_heat_stress(lat: float, lon: float) -> Dict:
    """
    Get heat stress data for a specific location
    """
    try:
        return await environmental_data_service.get_heat_stress(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/environmental/{lat}/{lon}")
async def get_environmental_data(lat: float, lon: float) -> Dict:
    """
    Get all environmental data for a specific location
    """
    try:
        return await environmental_data_service.get_environmental_data(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 