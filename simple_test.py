import requests
import json

# Base URL
base_url = "https://c3752e5e-dc16-4912-8914-647db3792b4d.preview.emergentagent.com/api"

# Test user
test_user = {
    "email": "testuser@impact.com",
    "password": "password123",
    "full_name": "Test User",
    "organization": "Demo Organization",
    "role": "Team Member"
}

# Test 1: Health Check
print("Test 1: Health Check")
response = requests.get(f"{base_url}/health")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
print()

# Test 2: User Login
print("Test 2: User Login")
login_data = {
    "email": test_user["email"],
    "password": test_user["password"]
}
response = requests.post(f"{base_url}/auth/login", json=login_data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
token = response.json().get("token")
print(f"Token: {token}")
print()

# Test 3: User Profile
print("Test 3: User Profile")
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{base_url}/user/profile", headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json() if response.status_code == 200 else response.text}")
print()

# Test 4: Dashboard Metrics
print("Test 4: Dashboard Metrics")
response = requests.get(f"{base_url}/dashboard/metrics", headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json() if response.status_code == 200 else response.text}")
print()

# Test 5: Create Assessment
print("Test 5: Create Assessment")
assessment_data = {
    "project_name": "Test Project",
    "change_management_maturity": {"name": "Change Management Maturity", "score": 4, "notes": "Good processes"},
    "communication_effectiveness": {"name": "Communication Effectiveness", "score": 3, "notes": "Average communication"},
    "leadership_support": {"name": "Leadership Support", "score": 5, "notes": "Strong leadership"},
    "workforce_adaptability": {"name": "Workforce Adaptability", "score": 2, "notes": "Needs improvement"},
    "resource_adequacy": {"name": "Resource Adequacy", "score": 4, "notes": "Adequate resources"}
}
response = requests.post(f"{base_url}/assessments", json=assessment_data, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json() if response.status_code == 200 else response.text}")