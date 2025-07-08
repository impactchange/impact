import requests
import unittest
import uuid
import time
from datetime import datetime

class IMPACTMethodologyAPITest(unittest.TestCase):
    """Test suite for the IMPACT Methodology API"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.base_url = "https://03ac140e-d2b8-4af7-a063-3734bf6aca8e.preview.emergentagent.com/api"
        self.test_user = {
            "email": f"test_{uuid.uuid4()}@example.com",
            "password": "Test@123456",
            "full_name": "Test User",
            "organization": "Test Organization",
            "role": "Team Member"
        }
        self.token = None
        self.user_id = None
        self.assessment_id = None
    
    def test_01_health_check(self):
        """Test the health check endpoint"""
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
        print("✅ Health check endpoint is working")
    
    def test_02_user_registration(self):
        """Test user registration"""
        response = requests.post(f"{self.base_url}/auth/register", json=self.test_user)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["email"], self.test_user["email"])
        self.assertEqual(data["user"]["full_name"], self.test_user["full_name"])
        self.assertEqual(data["user"]["organization"], self.test_user["organization"])
        self.assertEqual(data["user"]["role"], self.test_user["role"])
        self.token = data["token"]
        self.user_id = data["user"]["id"]
        print(f"✅ User registration successful with email: {self.test_user['email']}")
    
    def test_03_user_login(self):
        """Test user login"""
        login_data = {
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        }
        response = requests.post(f"{self.base_url}/auth/login", json=login_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["email"], self.test_user["email"])
        self.token = data["token"]
        print("✅ User login successful")
    
    def test_04_get_user_profile(self):
        """Test getting user profile"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/user/profile", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], self.test_user["email"])
        self.assertEqual(data["full_name"], self.test_user["full_name"])
        print("✅ User profile retrieval successful")
    
    def test_05_create_assessment(self):
        """Test creating a change readiness assessment"""
        headers = {"Authorization": f"Bearer {self.token}"}
        assessment_data = {
            "project_name": "Test Project",
            "change_management_maturity": {"name": "Change Management Maturity", "score": 4, "notes": "Good processes"},
            "communication_effectiveness": {"name": "Communication Effectiveness", "score": 3, "notes": "Average communication"},
            "leadership_support": {"name": "Leadership Support", "score": 5, "notes": "Strong leadership"},
            "workforce_adaptability": {"name": "Workforce Adaptability", "score": 2, "notes": "Needs improvement"},
            "resource_adequacy": {"name": "Resource Adequacy", "score": 4, "notes": "Adequate resources"}
        }
        
        response = requests.post(f"{self.base_url}/assessments", json=assessment_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["project_name"], assessment_data["project_name"])
        self.assertEqual(data["change_management_maturity"]["score"], assessment_data["change_management_maturity"]["score"])
        self.assertIn("overall_score", data)
        self.assertIn("ai_analysis", data)
        self.assertIn("recommendations", data)
        self.assertIn("success_probability", data)
        self.assessment_id = data["id"]
        print("✅ Assessment creation successful")
        print(f"   - Overall Score: {data['overall_score']}")
        print(f"   - Success Probability: {data['success_probability']}%")
        print(f"   - AI Analysis: {data['ai_analysis'][:100]}...")
    
    def test_06_get_assessments(self):
        """Test getting all assessments"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/assessments", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        print(f"✅ Retrieved {len(data)} assessments")
    
    def test_07_get_assessment_by_id(self):
        """Test getting a specific assessment by ID"""
        if not self.assessment_id:
            self.skipTest("No assessment ID available")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/assessments/{self.assessment_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.assessment_id)
        print("✅ Assessment retrieval by ID successful")
    
    def test_08_get_dashboard_metrics(self):
        """Test getting dashboard metrics"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/dashboard/metrics", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_assessments", data)
        self.assertIn("total_projects", data)
        self.assertIn("average_readiness_score", data)
        self.assertIn("average_success_probability", data)
        print("✅ Dashboard metrics retrieval successful")
        print(f"   - Total Assessments: {data['total_assessments']}")
        print(f"   - Average Readiness Score: {data['average_readiness_score']}")
        print(f"   - Average Success Probability: {data['average_success_probability']}%")
    
    def test_09_create_project(self):
        """Test creating a project"""
        headers = {"Authorization": f"Bearer {self.token}"}
        project_data = {
            "name": "Test Project",
            "description": "A test project for the IMPACT methodology",
            "phase": "Identify"
        }
        
        response = requests.post(f"{self.base_url}/projects", json=project_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], project_data["name"])
        self.assertEqual(data["description"], project_data["description"])
        print("✅ Project creation successful")
    
    def test_10_get_projects(self):
        """Test getting all projects"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/projects", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        print(f"✅ Retrieved {len(data)} projects")

def run_tests():
    """Run all tests in order"""
    test_suite = unittest.TestSuite()
    test_suite.addTest(IMPACTMethodologyAPITest('test_01_health_check'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_02_user_registration'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_03_user_login'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_04_get_user_profile'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_05_create_assessment'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_06_get_assessments'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_07_get_assessment_by_id'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_08_get_dashboard_metrics'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_09_create_project'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_10_get_projects'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)

if __name__ == "__main__":
    run_tests()