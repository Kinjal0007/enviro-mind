from typing import Optional, List, Dict
from beanie import Document, Indexed
from pydantic import EmailStr, BaseModel

class User(Document):
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    is_active: bool = True
    
    # User preferences and health data
    location: Optional[Dict[str, float]] = None  # {lat: float, lon: float}
    health_conditions: Optional[List[str]] = None
    sensitivities: Optional[Dict[str, int]] = None  # {condition: sensitivity_level}
    alert_preferences: Optional[Dict[str, float]] = None  # {alert_type: threshold}
    
    # Environmental data
    last_environmental_data: Optional[Dict] = None
    last_alert: Optional[Dict] = None

    class Settings:
        name = "users"
        indexes = [
            "email",  # Index for email field
        ] 