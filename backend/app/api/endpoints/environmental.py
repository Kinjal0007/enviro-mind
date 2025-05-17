from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.models.environmental import EnvironmentalData, EnvironmentalDataCreate
from app.services.environmental import (
    create_environmental_data,
    get_environmental_data_by_location,
    get_latest_environmental_data,
    update_environmental_data
)
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=EnvironmentalData)
async def create_data(
    data: EnvironmentalDataCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create new environmental data entry"""
    return await create_environmental_data(data)

@router.get("/location", response_model=List[EnvironmentalData])
async def get_data_by_location(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(5.0, description="Radius in kilometers"),
    hours: int = Query(24, description="Hours of historical data"),
    current_user: User = Depends(get_current_active_user)
):
    """Get environmental data for a location"""
    return await get_environmental_data_by_location(lat, lon, radius_km, hours)

@router.get("/latest", response_model=Optional[EnvironmentalData])
async def get_latest_data(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    current_user: User = Depends(get_current_active_user)
):
    """Get latest environmental data for a location"""
    data = await get_latest_environmental_data(lat, lon)
    if not data:
        raise HTTPException(status_code=404, detail="No data found for this location")
    return data

@router.put("/{data_id}", response_model=EnvironmentalData)
async def update_data(
    data_id: str,
    update_data: EnvironmentalDataCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Update environmental data"""
    data = await update_environmental_data(data_id, update_data.dict())
    if not data:
        raise HTTPException(status_code=404, detail="Data not found")
    return data 