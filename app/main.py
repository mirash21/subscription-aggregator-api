from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.database import engine, Base
from app.utils.logger import get_logger
from app.security import license_manager
import uvicorn
import os

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize logger
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Subscription Aggregation Service",
    description="REST API для агрегации данных об онлайн подписках пользователей",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Subscription Service...")
    
    # Проверка лицензии
    is_valid, reason = license_manager.validate_usage()
    license_info = license_manager.get_license_info()
    
    logger.info(f"License status: {reason}")
    logger.info(f"Installation ID: {license_info['installation_id']}")
    
    if not is_valid:
        logger.error(f"LICENSE VIOLATION: {reason}")
        logger.error("Commercial use requires paid license")
        # Можно добавить graceful degradation вместо остановки
    
    logger.info(f"Database connected: {engine.url}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Subscription Service...")

@app.get("/")
async def root():
    return {"message": "Subscription Aggregation Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/license-info")
async def license_info():
    """Получение информации о лицензии"""
    info = license_manager.get_license_info()
    return {
        "license_valid": info["valid"],
        "usage_reason": info["reason"],
        "development_mode": info["development_mode"],
        "trial_active": info["trial_active"],
        "installation_id": info["installation_id"]
    }

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=debug)