import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import uuid
from datetime import datetime

# --- Configuration ---
# Ensure this matches your .env file EXACTLY
MONGO_URL = "mongodb://myAdminUser:P#Yc41c6hV0!@127.0.0.1:27017/impact_methodology?authSource=admin"
DB_NAME = "impact_methodology"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

async def seed_database():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    print(f"Checking and creating collections in '{DB_NAME}'...")

    required_collections = [
        "users", 
        "projects", 
        "assessments", 
        "admin_notifications", 
        "user_activities", 
        "phase_transitions"
    ]

    for coll in required_collections:
        try:
            await db.create_collection(coll)
            print(f"  - Created collection: '{coll}'")
        except Exception:
            print(f"  - Collection '{coll}' already exists.")

    # --- Create an initial admin user ---
    admin_email = "admin@impact.com"
    admin_user = await db.users.find_one({"email": admin_email})

    if not admin_user:
        print(f"\nCreating initial admin user...")
        user_id = str(uuid.uuid4())
        admin_user_data = {
            "id": user_id,
            "username": "admin",
            "email": admin_email,
            "hashed_password": hash_password("password"), # Default password is "password"
            "full_name": "Admin User",
            "organization": "IMPACT Corp",
            "role": "Super Administrator",
            "status": "approved",
            "is_admin": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "approved_at": datetime.utcnow(),
            "approved_by": "system_seed"
        }
        await db.users.insert_one(admin_user_data)
        print("Admin user created successfully!")
        print("---")
        print("You can now log in with these credentials:")
        print(f"  Email: {admin_email}")
        print("  Password: password")
        print("---")
    else:
        print(f"\nAdmin user '{admin_email}' already exists. No new user created.")

    client.close()
    print("\nDatabase seeding process complete.")

if __name__ == "__main__":
    asyncio.run(seed_database())
