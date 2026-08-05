import sys
from pathlib import Path
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.database import SessionLocal
from app.services.auth_service import create_admin_if_not_exists
from app.routers import auth, account_management, create_camp, camp_doctor, register_patient, vitals_create,inventory, consultation, medicine


if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent.parent))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)



# Create FastAPI app
app = FastAPI(
    title="ERR-EMR Backend",
    description="Backend API for ERR-EMR Healthcare Management System",
    version="0.1.0",
    debug=True,
)


app.include_router(auth.router)
app.include_router(account_management.router)
app.include_router(create_camp.router)
app.include_router(camp_doctor.router)
app.include_router(register_patient.router)
app.include_router(vitals_create.router)
app.include_router(inventory.router)
app.include_router(consultation.router)
app.include_router(medicine.router)


# Add CORS middleware
# Configure CORS origins from settings if provided; otherwise allow all with a warning
origins = ["*"]
if settings.ALLOWED_ORIGINS:
    origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
    if not origins:
        origins = ["*"]

if origins == ["*"]:
    logger.warning("CORS configured to allow all origins. Set ALLOWED_ORIGINS to restrict this in production.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize database and create default admin"""

    try:
        # Validate essential settings
        missing = []
        if not settings.SECRET_KEY:
            missing.append("SECRET_KEY")
        if not settings.ALGORITHM:
            missing.append("ALGORITHM")
        if not settings.ACCESS_TOKEN_EXPIRE_MINUTES:
            missing.append("ACCESS_TOKEN_EXPIRE_MINUTES")
        if not settings.DATABASE_URL:
            missing.append("DATABASE_URL")

        if missing:
            logger.error(f"Missing required settings: {missing}")
            raise RuntimeError("Invalid configuration; check environment variables")

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")

        # Create default admin if it doesn't exist
        db = SessionLocal()
        try:
            create_admin_if_not_exists(db)
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        
    

@app.get("/")
async def root():
    return {
        "message": "ERR-EMR Backend is running",
        "app": "ERR-EMR Backend",
        "environment": "Development",
    }


if __name__ == "__main__":
        import uvicorn

        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
    )
