from typing import Optional, Dict, List
from datetime import datetime
from beanie import Document, Indexed
from pydantic import BaseModel

class EnvironmentalData(Document):
    location: Dict[str, float]  # {lat: float, lon: float}
    timestamp: datetime
    air_quality: Optional[Dict[str, float]] = None  # {pollutant: value}
    weather: Optional[Dict[str, float]] = None  # {temperature, humidity, etc.}
    pollen: Optional[Dict[str, float]] = None  # {pollen_type: concentration}
    uv_index: Optional[float] = None
    air_pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    precipitation: Optional[float] = None

    class Settings:
        name = "environmental_data"
        indexes = [
            "location",  # Index for location queries
            "timestamp",  # Index for time-based queries
        ]

class EnvironmentalDataCreate(BaseModel):
    location: Dict[str, float]
    air_quality: Optional[Dict[str, float]] = None
    weather: Optional[Dict[str, float]] = None
    pollen: Optional[Dict[str, float]] = None
    uv_index: Optional[float] = None
    air_pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    precipitation: Optional[float] = None 