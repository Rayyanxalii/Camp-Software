import sys
from pathlib import Path
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Settings
from app.database import Base, engine
from app.database import SessionLocal
from app.services.auth_service import create_admin_if_not_exists
from app.routers import auth, account_create


settings = Settings()

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
app.include_router(account_create.router)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize database and create default admin"""

    try:
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
