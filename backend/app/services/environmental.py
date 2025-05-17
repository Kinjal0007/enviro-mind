from datetime import datetime, timedelta
from typing import List, Optional, Dict
from app.models.environmental import EnvironmentalData, EnvironmentalDataCreate

async def create_environmental_data(data: EnvironmentalDataCreate) -> EnvironmentalData:
    """Create a new environmental data entry"""
    environmental_data = EnvironmentalData(
        **data.dict(),
        timestamp=datetime.utcnow()
    )
    await environmental_data.insert()
    return environmental_data

async def get_environmental_data_by_location(
    lat: float,
    lon: float,
    radius_km: float = 5.0,
    hours: int = 24
) -> List[EnvironmentalData]:
    """Get environmental data for a location within a radius and time range"""
    # Calculate time range
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # Find data within the time range
    data = await EnvironmentalData.find(
        EnvironmentalData.timestamp >= start_time
    ).to_list()
    
    # Filter by location (simple distance calculation)
    # In a production environment, you'd want to use proper geospatial queries
    filtered_data = []
    for entry in data:
        if entry.location:
            # Simple distance calculation (Haversine formula would be better)
            lat_diff = abs(entry.location.get('lat', 0) - lat)
            lon_diff = abs(entry.location.get('lon', 0) - lon)
            if lat_diff <= radius_km/111.32 and lon_diff <= radius_km/(111.32 * abs(lat)):
                filtered_data.append(entry)
    
    return filtered_data

async def get_latest_environmental_data(lat: float, lon: float) -> Optional[EnvironmentalData]:
    """Get the most recent environmental data for a location"""
    data = await EnvironmentalData.find(
        EnvironmentalData.location == {"lat": lat, "lon": lon}
    ).sort(-EnvironmentalData.timestamp).first_or_none()
    return data

async def update_environmental_data(
    data_id: str,
    update_data: Dict
) -> Optional[EnvironmentalData]:
    """Update environmental data by ID"""
    data = await EnvironmentalData.get(data_id)
    if data:
        for key, value in update_data.items():
            setattr(data, key, value)
        await data.save()
    return data 