# backend/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uvicorn
from datetime import datetime

# Import routers
from routers import auth as auth_router
from routers import assessments as assessments_router
from routers import projects as projects_router
from routers import admin as admin_router

# Load environment variables
load_dotenv()

# FastAPI app instantiation
app = FastAPI(title="IMPACT Methodology API", version="1.0.0")

# --- THIS IS THE SECTION TO REPLACE ---
# Define the allowed origins
origins = [
    "http://54.85.142.227",
    "https://5d518271-577f-499a-b42d-258b110b5820.preview.emergentagent.com",
    "http://localhost:3000",  # For local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- END OF REPLACEMENT SECTION ---

# Database configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "impact_methodology")

# MongoDB client
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Include routers
app.include_router(auth_router.router)
app.include_router(assessments_router.router)
app.include_router(projects_router.router)
app.include_router(admin_router.router)

# Basic health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Main execution block
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
