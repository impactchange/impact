# backend/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uvicorn

# Import routers
from routers import auth as auth_router
from routers import assessments as assessments_router
from routers import projects as projects_router
from routers import admin as admin_router # New admin router

# Load environment variables
load_dotenv()

# FastAPI app instantiation
app = FastAPI(title="IMPACT Methodology API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "impact_methodology")

# MongoDB client
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Include routers
app.include_router(auth_router.router, prefix="/api")
app.include_router(assessments_router.router, prefix="/api")
app.include_router(projects_router.router, prefix="/api")
app.include_router(admin_router.router, prefix="/api")


# Basic health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()} # Import datetime if needed

# Main execution block
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)