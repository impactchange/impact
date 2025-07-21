import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "impact_methodology")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt-impact-methodology-2024")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "demo-key")

def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
