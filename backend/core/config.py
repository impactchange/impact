import os
from dotenv import load_dotenv

# Load environment variables from a .env file at the root of your project
load_dotenv()

# --- Secret Key for JWT Token Encryption ---
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt-impact-methodology-2024")

# --- Database Connection Details ---
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "impact_methodology")

# --- Third-Party API Keys ---
# It's a good practice to return None or raise an error if a critical key is missing
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")