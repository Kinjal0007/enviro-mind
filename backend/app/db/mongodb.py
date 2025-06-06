from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.user import User
from app.models.environmental import EnvironmentalData

async def init_db():
    # Create Motor client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Initialize beanie with the document classes
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[User, EnvironmentalData]
    ) 