from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    try:
        # Create a new client
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        # Ping the server
        await client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
    finally:
        client.close() 