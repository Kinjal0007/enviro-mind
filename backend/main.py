from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import auth, environmental
from app.db.session import engine
from app.models.user import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EnviroMind API",
    description="API for personalized environmental health alerts",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(environmental.router, prefix="/api/v1/environmental", tags=["environmental"])

@app.get("/")
async def root():
    return {"message": "Welcome to EnviroMind API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 