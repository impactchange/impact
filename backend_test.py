import requests
import unittest
import uuid
import time
import json
from datetime import datetime, timedelta

class IMPACTMethodologyAPITest(unittest.TestCase):
    """Test suite for the IMPACT Methodology API"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.base_url = "https://03ac140e-d2b8-4af7-a063-3734bf6aca8e.preview.emergentagent.com/api"
        # Use a fixed test user for consistent testing
        self.test_user = {
            "email": "testuser@impact.com",
            "password": "password123",
            "full_name": "Test User",
            "organization": "Test Organization",
            "role": "Team Member"
        }
        self.token = None
        self.user_id = None
        self.assessment_id = None
        self.project_id = None
        self.task_id = None
        self.deliverable_id = None
    
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
    
    def test_08_get_impact_phases(self):
        """Test getting IMPACT phases configuration"""
        response = requests.get(f"{self.base_url}/impact/phases")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("identify", data)
        self.assertIn("measure", data)
        self.assertIn("plan", data)
        self.assertIn("act", data)
        self.assertIn("control", data)
        self.assertIn("transform", data)
        print("✅ IMPACT phases retrieval successful")
        print(f"   - Found {len(data)} phases")
    
    def test_09_get_impact_phase_details(self):
        """Test getting specific IMPACT phase details"""
        response = requests.get(f"{self.base_url}/impact/phases/identify")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Identify")
        self.assertIn("description", data)
        self.assertIn("newton_law", data)
        self.assertIn("objectives", data)
        self.assertIn("key_activities", data)
        self.assertIn("deliverables", data)
        print("✅ IMPACT phase details retrieval successful")
        print(f"   - Phase: {data['name']}")
        print(f"   - Newton's Law: {data['newton_law']}")
    
    def test_10_get_dashboard_metrics(self):
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
    
    def test_11_create_project(self):
        """Test creating a project"""
        headers = {"Authorization": f"Bearer {self.token}"}
        project_data = {
            "name": "Test IMPACT Project",
            "description": "A test project for the IMPACT methodology",
            "target_completion_date": (datetime.utcnow() + timedelta(days=90)).isoformat(),
            "budget": 50000
        }
        
        response = requests.post(f"{self.base_url}/projects", json=project_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], project_data["name"])
        self.assertEqual(data["description"], project_data["description"])
        self.assertEqual(data["current_phase"], "identify")
        self.assertIn("tasks", data)
        self.assertIn("deliverables", data)
        self.assertIn("milestones", data)
        self.project_id = data["id"]
        
        # Save a task and deliverable ID for later tests
        if data["tasks"] and len(data["tasks"]) > 0:
            self.task_id = data["tasks"][0]["id"]
        if data["deliverables"] and len(data["deliverables"]) > 0:
            self.deliverable_id = data["deliverables"][0]["id"]
            
        print("✅ Project creation successful")
        print(f"   - Project ID: {self.project_id}")
        print(f"   - Initial phase: {data['current_phase']}")
        print(f"   - Tasks: {len(data['tasks'])}")
        print(f"   - Deliverables: {len(data['deliverables'])}")
    
    def test_12_create_project_from_assessment(self):
        """Test creating a project from assessment"""
        if not self.assessment_id:
            self.skipTest("No assessment ID available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        project_data = {
            "assessment_id": self.assessment_id,
            "project_name": "Project from Assessment",
            "description": "A project created from assessment results",
            "target_completion_date": (datetime.utcnow() + timedelta(days=120)).isoformat(),
            "budget": 75000
        }
        
        response = requests.post(f"{self.base_url}/projects/from-assessment", json=project_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], project_data["project_name"])
        self.assertEqual(data["description"], project_data["description"])
        self.assertEqual(data["assessment_id"], self.assessment_id)
        self.assertIn("newton_insights", data)
        print("✅ Project creation from assessment successful")
        print(f"   - Project ID: {data['id']}")
        print(f"   - Tasks: {len(data['tasks'])}")
        print(f"   - Deliverables: {len(data['deliverables'])}")
    
    def test_13_get_projects(self):
        """Test getting all projects"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/projects", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        print(f"✅ Retrieved {len(data)} projects")
    
    def test_14_get_project_by_id(self):
        """Test getting a specific project by ID"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/projects/{self.project_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.project_id)
        print("✅ Project retrieval by ID successful")
    
    def test_15_update_task(self):
        """Test updating a task"""
        if not self.project_id or not self.task_id:
            self.skipTest("No project ID or task ID available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        task_update = {
            "status": "in_progress",
            "notes": "Working on this task",
            "priority": "high"
        }
        
        response = requests.put(
            f"{self.base_url}/projects/{self.project_id}/tasks/{self.task_id}", 
            json=task_update, 
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Task updated successfully")
        print("✅ Task update successful")
    
    def test_16_update_deliverable(self):
        """Test updating a deliverable"""
        if not self.project_id or not self.deliverable_id:
            self.skipTest("No project ID or deliverable ID available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        deliverable_update = {
            "status": "in_progress",
            "content": "Initial draft of the deliverable",
            "approval_notes": "Pending review"
        }
        
        response = requests.put(
            f"{self.base_url}/projects/{self.project_id}/deliverables/{self.deliverable_id}", 
            json=deliverable_update, 
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Deliverable updated successfully")
        print("✅ Deliverable update successful")
    
    def test_17_get_advanced_analytics(self):
        """Test getting advanced analytics"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/analytics/advanced", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("trend_analysis", data)
        self.assertIn("newton_laws_data", data)
        self.assertIn("dimension_breakdown", data)
        print("✅ Advanced analytics retrieval successful")

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
    test_suite.addTest(IMPACTMethodologyAPITest('test_08_get_impact_phases'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_09_get_impact_phase_details'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_10_get_dashboard_metrics'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_11_create_project'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_12_create_project_from_assessment'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_13_get_projects'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_14_get_project_by_id'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_15_update_task'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_16_update_deliverable'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_17_get_advanced_analytics'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)

if __name__ == "__main__":
    run_tests()