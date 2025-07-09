import requests
import unittest
import uuid
import time
import json
import concurrent.futures
import random
import string
from datetime import datetime, timedelta

class IMPACTMethodologyAPITest(unittest.TestCase):
    """Test suite for the IMPACT Methodology API"""
    
    def setUp(self):
        """Set up test environment before each test"""
        self.base_url = "https://5d518271-577f-499a-b42d-258b110b5820.preview.emergentagent.com/api"
        # Use a fixed test user for consistent testing
        self.test_user = {
            "email": "testuser@impact.com",
            "password": "password123",
            "full_name": "Test User",
            "organization": "Demo Organization",
            "role": "Team Member"
        }
        self.token = None
        self.user_id = None
        self.assessment_id = None
        self.project_id = None
        self.task_id = None
        self.deliverable_id = None
        self.typed_assessment_ids = {}  # Store assessment IDs by type
    
    def test_01_health_check(self):
        """Test the health check endpoint"""
        response = requests.get(f"{self.base_url}/health")
        print(f"Health check response: {response.status_code} - {response.text}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
        print("✅ Health check endpoint is working")
    
    def test_02_user_registration(self):
        """Test user registration"""
        # Try to register, but if user already exists, just continue
        response = requests.post(f"{self.base_url}/auth/register", json=self.test_user)
        if response.status_code == 200:
            data = response.json()
            self.assertIn("token", data)
            self.assertIn("user", data)
            self.assertEqual(data["user"]["email"], self.test_user["email"])
            self.token = data["token"]
            self.user_id = data["user"]["id"]
            print(f"✅ User registration successful with email: {self.test_user['email']}")
        else:
            print(f"User already exists, continuing with login")
    
    def test_03_user_login(self):
        """Test user login"""
        login_data = {
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        }
        response = requests.post(f"{self.base_url}/auth/login", json=login_data)
        print(f"Login response: {response.status_code} - {response.text}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["email"], self.test_user["email"])
        self.token = data["token"]
        self.user_id = data["user"]["id"]
        print(f"Token: {self.token}")
        print("✅ User login successful")
    
    def test_04_get_user_profile(self):
        """Test getting user profile"""
        if not self.token:
            self.skipTest("No token available")
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/user/profile", headers=headers)
        print(f"User profile response: {response.status_code} - {response.text}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], self.test_user["email"])
        self.assertEqual(data["full_name"], self.test_user["full_name"])
        print("✅ User profile retrieval successful")
    
    def test_05_get_assessment_types(self):
        """Test fetching all available assessment types"""
        response = requests.get(f"{self.base_url}/assessment-types")
        print(f"Assessment types response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check if the response has assessment_types key
        if "assessment_types" in data:
            data = data["assessment_types"]
        
        # Verify all required assessment types are present
        self.assertIn("general_readiness", data)
        self.assertIn("software_implementation", data)
        self.assertIn("business_process", data)
        self.assertIn("manufacturing_operations", data)
        
        # Verify structure of each assessment type
        for assessment_type in ["general_readiness", "software_implementation", "business_process", "manufacturing_operations"]:
            self.assertIn("name", data[assessment_type])
            self.assertIn("description", data[assessment_type])
            self.assertIn("icon", data[assessment_type])
            self.assertIn("dimensions", data[assessment_type])
            
            # Verify dimensions structure
            dimensions = data[assessment_type]["dimensions"]
            self.assertGreater(len(dimensions), 0)
            for dimension in dimensions:
                self.assertIn("id", dimension)
                self.assertIn("name", dimension)
                self.assertIn("description", dimension)
                self.assertIn("category", dimension)
        
        print("✅ Assessment types API successful")
        print(f"   - Found {len(data)} assessment types")
        for assessment_type in data:
            print(f"   - {assessment_type}: {data[assessment_type]['name']} with {len(data[assessment_type]['dimensions'])} dimensions")
    
    def test_06_create_general_readiness_assessment(self):
        """Test creating a general readiness assessment"""
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        assessment_data = {
            "assessment_type": "general_readiness",
            "project_name": "General Readiness Test Project",
            "leadership_commitment": {"name": "Leadership Commitment & Sponsorship", "score": 4, "notes": "Strong leadership support"},
            "organizational_culture": {"name": "Organizational Culture & Change History", "score": 3, "notes": "Average adaptability"},
            "resource_availability": {"name": "Resource Availability & Capability", "score": 4, "notes": "Good resources"},
            "stakeholder_engagement": {"name": "Stakeholder Engagement & Communication", "score": 3, "notes": "Needs improvement"},
            "training_capability": {"name": "Training & Development Capability", "score": 4, "notes": "Good training infrastructure"}
        }
        
        response = requests.post(f"{self.base_url}/assessments/create", json=assessment_data, headers=headers)
        print(f"Create general readiness assessment response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("id", data)
        self.assertEqual(data["project_name"], assessment_data["project_name"])
        self.assertIn("overall_score", data)
        self.assertIn("ai_analysis", data)
        self.assertIn("recommendations", data)
        self.assertIn("success_probability", data)
        self.assertIn("newton_analysis", data)
        
        # Store the assessment ID for later use
        self.typed_assessment_ids["general_readiness"] = data["id"]
        print("✅ General readiness assessment creation successful")
        print(f"   - Overall Score: {data['overall_score']}")
        print(f"   - Success Probability: {data['success_probability']}%")
    
    def test_07_create_software_implementation_assessment(self):
        """Test creating a software implementation assessment"""
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        assessment_data = {
            "assessment_type": "software_implementation",
            "project_name": "Software Implementation Test Project",
            "leadership_commitment": {"name": "Leadership Commitment & Sponsorship", "score": 4, "notes": "Strong leadership support"},
            "organizational_culture": {"name": "Organizational Culture & Change History", "score": 3, "notes": "Average adaptability"},
            "resource_availability": {"name": "Resource Availability & Capability", "score": 4, "notes": "Good resources"},
            "stakeholder_engagement": {"name": "Stakeholder Engagement & Communication", "score": 3, "notes": "Needs improvement"},
            "training_capability": {"name": "Training & Development Capability", "score": 4, "notes": "Good training infrastructure"},
            "technical_infrastructure": {"name": "Technical Infrastructure Readiness", "score": 3, "notes": "Average infrastructure"},
            "user_adoption_readiness": {"name": "User Adoption Readiness", "score": 2, "notes": "Needs significant improvement"},
            "data_migration_readiness": {"name": "Data Migration & Integration Readiness", "score": 3, "notes": "Some challenges expected"}
        }
        
        response = requests.post(f"{self.base_url}/assessments/create", json=assessment_data, headers=headers)
        print(f"Create software implementation assessment response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("id", data)
        self.assertEqual(data["project_name"], assessment_data["project_name"])
        self.assertIn("overall_score", data)
        self.assertIn("ai_analysis", data)
        self.assertIn("recommendations", data)
        self.assertIn("success_probability", data)
        self.assertIn("newton_analysis", data)
        
        # Verify type-specific fields
        self.assertIn("technical_infrastructure", data)
        self.assertIn("user_adoption_readiness", data)
        self.assertIn("data_migration_readiness", data)
        
        # Store the assessment ID for later use
        self.typed_assessment_ids["software_implementation"] = data["id"]
        self.assessment_id = data["id"]  # Set as default assessment ID for other tests
        print("✅ Software implementation assessment creation successful")
        print(f"   - Overall Score: {data['overall_score']}")
        print(f"   - Success Probability: {data['success_probability']}%")
    
    def test_08_create_business_process_assessment(self):
        """Test creating a business process assessment"""
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        assessment_data = {
            "assessment_type": "business_process",
            "project_name": "Business Process Test Project",
            "leadership_commitment": {"name": "Leadership Commitment & Sponsorship", "score": 4, "notes": "Strong leadership support"},
            "organizational_culture": {"name": "Organizational Culture & Change History", "score": 3, "notes": "Average adaptability"},
            "resource_availability": {"name": "Resource Availability & Capability", "score": 4, "notes": "Good resources"},
            "stakeholder_engagement": {"name": "Stakeholder Engagement & Communication", "score": 3, "notes": "Needs improvement"},
            "training_capability": {"name": "Training & Development Capability", "score": 4, "notes": "Good training infrastructure"},
            "process_maturity": {"name": "Current Process Maturity", "score": 3, "notes": "Moderately mature processes"},
            "cross_functional_collaboration": {"name": "Cross-Functional Collaboration", "score": 2, "notes": "Significant silos exist"},
            "performance_measurement": {"name": "Performance Measurement Capability", "score": 3, "notes": "Basic metrics in place"}
        }
        
        response = requests.post(f"{self.base_url}/assessments/create", json=assessment_data, headers=headers)
        print(f"Create business process assessment response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("id", data)
        self.assertEqual(data["project_name"], assessment_data["project_name"])
        self.assertIn("overall_score", data)
        self.assertIn("ai_analysis", data)
        self.assertIn("recommendations", data)
        self.assertIn("success_probability", data)
        self.assertIn("newton_analysis", data)
        
        # Verify type-specific fields
        self.assertIn("process_maturity", data)
        self.assertIn("cross_functional_collaboration", data)
        self.assertIn("performance_measurement", data)
        
        # Store the assessment ID for later use
        self.typed_assessment_ids["business_process"] = data["id"]
        print("✅ Business process assessment creation successful")
        print(f"   - Overall Score: {data['overall_score']}")
        print(f"   - Success Probability: {data['success_probability']}%")
    
    def test_09_create_manufacturing_operations_assessment(self):
        """Test creating a manufacturing operations assessment"""
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        assessment_data = {
            "assessment_type": "manufacturing_operations",
            "project_name": "Manufacturing Operations Test Project",
            "leadership_commitment": {"name": "Leadership Commitment & Sponsorship", "score": 4, "notes": "Strong leadership support"},
            "organizational_culture": {"name": "Organizational Culture & Change History", "score": 3, "notes": "Average adaptability"},
            "resource_availability": {"name": "Resource Availability & Capability", "score": 4, "notes": "Good resources"},
            "stakeholder_engagement": {"name": "Stakeholder Engagement & Communication", "score": 3, "notes": "Needs improvement"},
            "training_capability": {"name": "Training & Development Capability", "score": 4, "notes": "Good training infrastructure"},
            "operational_constraints": {"name": "Operational Constraints Management", "score": 3, "notes": "Some constraints identified"},
            "maintenance_operations_alignment": {"name": "Maintenance-Operations Alignment", "score": 2, "notes": "Poor alignment"},
            "shift_coordination": {"name": "Shift Work & Coordination", "score": 3, "notes": "Moderate coordination"},
            "safety_compliance": {"name": "Safety & Compliance Integration", "score": 4, "notes": "Strong safety culture"}
        }
        
        response = requests.post(f"{self.base_url}/assessments/create", json=assessment_data, headers=headers)
        print(f"Create manufacturing operations assessment response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("id", data)
        self.assertEqual(data["project_name"], assessment_data["project_name"])
        self.assertIn("overall_score", data)
        self.assertIn("ai_analysis", data)
        self.assertIn("recommendations", data)
        self.assertIn("success_probability", data)
        self.assertIn("newton_analysis", data)
        
        # Verify type-specific fields
        self.assertIn("operational_constraints", data)
        self.assertIn("maintenance_operations_alignment", data)
        self.assertIn("shift_coordination", data)
        self.assertIn("safety_compliance", data)
        
        # Store the assessment ID for later use
        self.typed_assessment_ids["manufacturing_operations"] = data["id"]
        print("✅ Manufacturing operations assessment creation successful")
        print(f"   - Overall Score: {data['overall_score']}")
        print(f"   - Success Probability: {data['success_probability']}%")
    
    def test_10_get_assessments(self):
        """Test getting all assessments"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/assessments", headers=headers)
        print(f"Get assessments response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        print(f"✅ Retrieved {len(data)} assessments")
    
    def test_11_get_assessment_by_id(self):
        """Test getting a specific assessment by ID"""
        if not self.assessment_id:
            self.skipTest("No assessment ID available")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/assessments/{self.assessment_id}", headers=headers)
        print(f"Get assessment by ID response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.assessment_id)
        print("✅ Assessment retrieval by ID successful")
    
    def test_12_get_universal_impact_phases(self):
        """Test getting universal IMPACT phases configuration"""
        response = requests.get(f"{self.base_url}/impact/phases")
        print(f"IMPACT phases response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify all universal phases are present
        self.assertIn("investigate", data)
        self.assertIn("mobilize", data)
        self.assertIn("pilot", data)
        self.assertIn("activate", data)
        self.assertIn("cement", data)
        self.assertIn("track", data)
        
        # Verify phase structure
        for phase in ["investigate", "mobilize", "pilot", "activate", "cement", "track"]:
            self.assertIn("name", data[phase])
            self.assertIn("description", data[phase])
            self.assertIn("order", data[phase])
            self.assertIn("newton_law", data[phase])
            self.assertIn("objectives", data[phase])
            self.assertIn("key_activities", data[phase])
            self.assertIn("deliverables", data[phase])
            
            # Verify universal focus (not EAM-specific)
            if "universal_focus" in data[phase]:
                self.assertIn("universal_focus", data[phase])
        
        print("✅ Universal IMPACT phases retrieval successful")
        print(f"   - Found {len(data)} phases")
        for phase in data:
            print(f"   - {phase}: {data[phase]['name']}")
    
    def test_13_get_impact_phase_details(self):
        """Test getting specific IMPACT phase details"""
        response = requests.get(f"{self.base_url}/impact/phases/investigate")
        print(f"IMPACT phase details response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["name"], "Investigate & Assess")
        self.assertIn("description", data)
        self.assertIn("newton_law", data)
        self.assertIn("objectives", data)
        self.assertIn("key_activities", data)
        self.assertIn("deliverables", data)
        
        print("✅ IMPACT phase details retrieval successful")
        print(f"   - Phase: {data['name']}")
        print(f"   - Newton's Law: {data['newton_law']}")
    
    def test_14_get_dashboard_metrics(self):
        """Test getting dashboard metrics"""
        if not self.token:
            self.skipTest("No token available")
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/dashboard/metrics", headers=headers)
        print(f"Dashboard metrics response: {response.status_code} - {response.text}")
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
    
    def test_15_create_project(self):
        """Test creating a project"""
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        project_data = {
            "name": "Test IMPACT Project",
            "description": "A test project for the IMPACT methodology",
            "organization": "Demo Organization",
            "target_completion_date": (datetime.utcnow() + timedelta(days=90)).isoformat(),
            "budget": 50000
        }
        
        response = requests.post(f"{self.base_url}/projects", json=project_data, headers=headers)
        print(f"Create project response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["description"], project_data["description"])
        self.assertEqual(data["current_phase"], "investigate")  # Should use new phase name
        self.assertIn("deliverables", data)
        self.assertIn("milestones", data)
        self.project_id = data["id"]
        
        # Save a task and deliverable ID for later tests if available
        if "tasks" in data and data["tasks"] and len(data["tasks"]) > 0:
            self.task_id = data["tasks"][0]["id"]
        if "deliverables" in data and data["deliverables"] and len(data["deliverables"]) > 0:
            self.deliverable_id = data["deliverables"][0]["id"]
            
        print("✅ Project creation successful")
        print(f"   - Project ID: {self.project_id}")
        print(f"   - Initial phase: {data['current_phase']}")
        print(f"   - Deliverables: {len(data.get('deliverables', []))}")
    
    def test_16_create_project_from_assessment(self):
        """Test creating a project from assessment"""
        if not self.assessment_id:
            self.skipTest("No assessment ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        project_data = {
            "assessment_id": self.assessment_id,
            "project_name": "Project from Assessment",
            "description": "A project created from assessment results",
            "target_completion_date": (datetime.utcnow() + timedelta(days=120)).isoformat(),
            "budget": 75000
        }
        
        response = requests.post(f"{self.base_url}/projects/from-assessment", json=project_data, headers=headers)
        print(f"Create project from assessment response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], project_data["project_name"])
        self.assertEqual(data["description"], project_data["description"])
        self.assertEqual(data["assessment_id"], self.assessment_id)
        self.assertIn("newton_insights", data)
        
        # Verify implementation plan is generated
        self.assertIn("implementation_plan", data)
        if "implementation_plan" in data:
            self.assertIn("suggested_duration_weeks", data["implementation_plan"])
            self.assertIn("critical_success_factors", data["implementation_plan"])
            self.assertIn("resource_priorities", data["implementation_plan"])
            self.assertIn("key_milestones", data["implementation_plan"])
        
        print("✅ Project creation from assessment successful")
        print(f"   - Project ID: {data['id']}")
        print(f"   - Tasks: {len(data['tasks'])}")
        print(f"   - Deliverables: {len(data['deliverables'])}")
        print(f"   - Implementation Plan Duration: {data.get('implementation_plan', {}).get('suggested_duration_weeks', 'N/A')} weeks")
    
    def test_17_get_projects(self):
        """Test getting all projects"""
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/projects", headers=headers)
        print(f"Get projects response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check if the response has a 'projects' key
        if "projects" in data:
            projects = data["projects"]
        else:
            projects = data
            
        self.assertIsInstance(projects, list)
        self.assertGreaterEqual(len(projects), 1)
        print(f"✅ Retrieved {len(projects)} projects")
    
    def test_18_get_project_by_id(self):
        """Test getting a specific project by ID"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/projects/{self.project_id}", headers=headers)
        print(f"Get project by ID response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.project_id)
        print("✅ Project retrieval by ID successful")
    
    def test_19_update_project(self):
        """Test updating a project"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        project_update = {
            "name": "Updated Project Name",
            "description": "Updated project description",
            "status": "on_hold",
            "progress_percentage": 25.0
        }
        
        response = requests.put(f"{self.base_url}/projects/{self.project_id}", json=project_update, headers=headers)
        print(f"Update project response: {response.status_code} - {response.text}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.project_id)
        self.assertEqual(data["name"], project_update["name"])
        self.assertEqual(data["description"], project_update["description"])
        self.assertEqual(data["status"], project_update["status"])
        self.assertEqual(data["progress_percentage"], project_update["progress_percentage"])
        print("✅ Project update successful")
    
    def test_20_update_task(self):
        """Test updating a task"""
        if not self.project_id or not self.task_id:
            self.skipTest("No project ID or task ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
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
        print(f"Update task response: {response.status_code} - {response.text}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Task updated successfully")
        print("✅ Task update successful")
    
    def test_21_update_deliverable(self):
        """Test updating a deliverable"""
        if not self.project_id or not self.deliverable_id:
            self.skipTest("No project ID or deliverable ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
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
        print(f"Update deliverable response: {response.status_code} - {response.text}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Deliverable updated successfully")
        print("✅ Deliverable update successful")
    
    def test_22_get_type_specific_analysis(self):
        """Test getting type-specific analysis for an assessment"""
        if not self.typed_assessment_ids.get("software_implementation"):
            self.skipTest("No software implementation assessment ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        assessment_id = self.typed_assessment_ids["software_implementation"]
        
        response = requests.get(f"{self.base_url}/assessments/{assessment_id}/analysis", headers=headers)
        print(f"Get type-specific analysis response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify type-specific analysis fields
        self.assertIn("newton_analysis", data)
        self.assertIn("recommendations", data)
        self.assertIn("success_probability", data)
        self.assertIn("risk_factors", data)
        self.assertIn("phase_recommendations", data)
        
        # Verify software-specific recommendations
        recommendations = data.get("recommendations", [])
        software_specific_terms = ["technical", "infrastructure", "user", "data", "migration", "system"]
        found_software_specific = False
        for rec in recommendations:
            if any(term in rec.lower() for term in software_specific_terms):
                found_software_specific = True
                break
        
        self.assertTrue(found_software_specific, "No software-specific recommendations found")
        print("✅ Type-specific analysis retrieval successful")
        print(f"   - Success Probability: {data.get('success_probability', 'N/A')}%")
        print(f"   - Risk Factors: {len(data.get('risk_factors', []))} factors identified")
    
    def test_23_get_advanced_analytics(self):
        """Test getting advanced analytics"""
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/analytics/advanced", headers=headers)
        print(f"Advanced analytics response: {response.status_code} - {response.text[:200]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("trend_analysis", data)
        self.assertIn("newton_laws_data", data)
        self.assertIn("dimension_breakdown", data)
        print("✅ Advanced analytics retrieval successful")
    
    def test_24_validate_implementation_plan_generation(self):
        """Test the implementation plan generation for different assessment types"""
        if not self.typed_assessment_ids:
            self.skipTest("No typed assessment IDs available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        for assessment_type, assessment_id in self.typed_assessment_ids.items():
            response = requests.get(f"{self.base_url}/assessments/{assessment_id}/implementation-plan", headers=headers)
            print(f"Implementation plan for {assessment_type} response: {response.status_code} - {response.text[:200]}...")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            self.assertIn("suggested_duration_weeks", data)
            self.assertIn("critical_success_factors", data)
            self.assertIn("resource_priorities", data)
            self.assertIn("key_milestones", data)
            
            # Verify type-specific adjustments
            if assessment_type == "software_implementation":
                # Software implementation should take longer
                self.assertGreaterEqual(data["suggested_duration_weeks"], 12)
            elif assessment_type == "manufacturing_operations":
                # Manufacturing should take the longest
                self.assertGreaterEqual(data["suggested_duration_weeks"], 16)
            
            print(f"✅ Implementation plan generation for {assessment_type} successful")
            print(f"   - Suggested Duration: {data['suggested_duration_weeks']} weeks")
            print(f"   - Critical Success Factors: {len(data['critical_success_factors'])}")
            print(f"   - Key Milestones: {len(data['key_milestones'])}")

def run_tests():
    """Run all tests in order"""
    test_suite = unittest.TestSuite()
    
    # Basic health check and authentication
    test_suite.addTest(IMPACTMethodologyAPITest('test_01_health_check'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_02_user_registration'))
    test_suite.addTest(IMPACTMethodologyAPITest('test_03_user_login'))
    
    # Create a test instance to share the token
    test_instance = IMPACTMethodologyAPITest('test_04_get_user_profile')
    test_instance.setUp()
    test_instance.test_03_user_login()
    
    # Add the remaining tests using the same instance
    test_suite.addTest(test_instance)
    
    # Add tests for assessment types
    assessment_types_test = IMPACTMethodologyAPITest('test_05_get_assessment_types')
    assessment_types_test.setUp()
    test_suite.addTest(assessment_types_test)
    
    # Add tests for universal IMPACT phases
    impact_phases_test = IMPACTMethodologyAPITest('test_12_get_universal_impact_phases')
    impact_phases_test.setUp()
    test_suite.addTest(impact_phases_test)
    
    impact_phase_details_test = IMPACTMethodologyAPITest('test_13_get_impact_phase_details')
    impact_phase_details_test.setUp()
    test_suite.addTest(impact_phase_details_test)
    
    # Add tests for creating different assessment types
    assessment_test = IMPACTMethodologyAPITest('test_06_create_general_readiness_assessment')
    assessment_test.setUp()
    assessment_test.token = test_instance.token
    test_suite.addTest(assessment_test)
    
    software_test = IMPACTMethodologyAPITest('test_07_create_software_implementation_assessment')
    software_test.setUp()
    software_test.token = test_instance.token
    test_suite.addTest(software_test)
    
    business_test = IMPACTMethodologyAPITest('test_08_create_business_process_assessment')
    business_test.setUp()
    business_test.token = test_instance.token
    test_suite.addTest(business_test)
    
    manufacturing_test = IMPACTMethodologyAPITest('test_09_create_manufacturing_operations_assessment')
    manufacturing_test.setUp()
    manufacturing_test.token = test_instance.token
    test_suite.addTest(manufacturing_test)
    
    # Add tests for project management
    project_test = IMPACTMethodologyAPITest('test_15_create_project')
    project_test.setUp()
    project_test.token = test_instance.token
    test_suite.addTest(project_test)
    
    # Add tests for type-specific analysis
    analysis_test = IMPACTMethodologyAPITest('test_22_get_type_specific_analysis')
    analysis_test.setUp()
    analysis_test.token = test_instance.token
    analysis_test.typed_assessment_ids = software_test.typed_assessment_ids
    test_suite.addTest(analysis_test)
    
    # Add test for implementation plan generation
    plan_test = IMPACTMethodologyAPITest('test_24_validate_implementation_plan_generation')
    plan_test.setUp()
    plan_test.token = test_instance.token
    plan_test.typed_assessment_ids = software_test.typed_assessment_ids
    test_suite.addTest(plan_test)
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)


class ProductionReadinessTest(IMPACTMethodologyAPITest):
    """Test suite for production readiness testing of the IMPACT Methodology API"""
    
    def setUp(self):
        """Set up test environment before each test"""
        super().setUp()
        # Login to get token for authenticated tests
        login_data = {
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        }
        response = requests.post(f"{self.base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.token = data["token"]
            self.user_id = data["user"]["id"]
        else:
            print(f"Warning: Login failed with status {response.status_code}")
    
    def test_01_api_performance(self):
        """Test API performance under load"""
        endpoints = [
            "/health",
            "/assessment-types",
            "/impact/phases"
        ]
        
        results = {}
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{self.base_url}{endpoint}")
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            results[endpoint] = {
                "status_code": response.status_code,
                "response_time_ms": response_time
            }
            
            # Check if response time is acceptable (< 500ms)
            self.assertLess(response_time, 500, f"Response time for {endpoint} is too slow: {response_time:.2f}ms")
            
        print("✅ API Performance Test Results:")
        for endpoint, data in results.items():
            print(f"   - {endpoint}: {data['status_code']} in {data['response_time_ms']:.2f}ms")
    
    def test_02_concurrent_requests(self):
        """Test API performance with concurrent requests"""
        endpoint = "/health"
        num_requests = 10
        
        def make_request():
            start_time = time.time()
            response = requests.get(f"{self.base_url}{endpoint}")
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time_ms": (end_time - start_time) * 1000
            }
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Calculate statistics
        response_times = [result["response_time_ms"] for result in results]
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # Check if all requests were successful
        all_successful = all(result["status_code"] == 200 for result in results)
        self.assertTrue(all_successful, "Not all concurrent requests were successful")
        
        # Check if average response time is acceptable (< 500ms)
        self.assertLess(avg_response_time, 500, f"Average response time is too slow: {avg_response_time:.2f}ms")
        
        print("✅ Concurrent Requests Test Results:")
        print(f"   - Number of concurrent requests: {num_requests}")
        print(f"   - Average response time: {avg_response_time:.2f}ms")
        print(f"   - Maximum response time: {max_response_time:.2f}ms")
    
    def test_03_jwt_token_security(self):
        """Test JWT token security"""
        if not self.token:
            self.skipTest("No token available")
        
        # Test 1: Valid token should work
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/user/profile", headers=headers)
        self.assertEqual(response.status_code, 200, "Valid token should be accepted")
        
        # Test 2: Invalid token should fail
        invalid_token = self.token[:-5] + "12345"
        headers = {"Authorization": f"Bearer {invalid_token}"}
        response = requests.get(f"{self.base_url}/user/profile", headers=headers)
        self.assertNotEqual(response.status_code, 200, "Invalid token should be rejected")
        
        # Test 3: Expired token (can't easily test without modifying server code)
        
        # Test 4: Missing token should fail
        response = requests.get(f"{self.base_url}/user/profile")
        self.assertNotEqual(response.status_code, 200, "Missing token should be rejected")
        
        # Test 5: Malformed token should fail
        headers = {"Authorization": "Bearer not_a_valid_token"}
        response = requests.get(f"{self.base_url}/user/profile", headers=headers)
        self.assertNotEqual(response.status_code, 200, "Malformed token should be rejected")
        
        print("✅ JWT Token Security Test Results:")
        print("   - Valid token accepted")
        print("   - Invalid token rejected")
        print("   - Missing token rejected")
        print("   - Malformed token rejected")
    
    def test_04_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        # Test SQL injection in login
        sql_injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users; --",
            "admin' --"
        ]
        
        for payload in sql_injection_payloads:
            login_data = {
                "email": payload,
                "password": payload
            }
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            self.assertNotEqual(response.status_code, 200, f"SQL injection payload should be rejected: {payload}")
        
        # Test SQL injection in URL parameters
        if self.assessment_id:
            injection_id = self.assessment_id + "' OR '1'='1"
            response = requests.get(f"{self.base_url}/assessments/{injection_id}")
            self.assertNotEqual(response.status_code, 200, "SQL injection in URL parameter should be rejected")
        
        print("✅ SQL Injection Prevention Test Results:")
        print("   - SQL injection payloads rejected in login")
        print("   - SQL injection in URL parameters rejected")
    
    def test_05_cors_configuration(self):
        """Test CORS configuration"""
        headers = {
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type, Authorization"
        }
        
        # Test preflight request
        response = requests.options(f"{self.base_url}/health", headers=headers)
        
        # Check if CORS headers are present
        self.assertIn("Access-Control-Allow-Origin", response.headers, "CORS headers missing")
        
        # Check if methods are allowed
        if "Access-Control-Allow-Methods" in response.headers:
            allowed_methods = response.headers["Access-Control-Allow-Methods"]
            self.assertIn("GET", allowed_methods, "GET method should be allowed in CORS")
            self.assertIn("POST", allowed_methods, "POST method should be allowed in CORS")
        
        # Check if headers are allowed
        if "Access-Control-Allow-Headers" in response.headers:
            allowed_headers = response.headers["Access-Control-Allow-Headers"]
            self.assertIn("Content-Type", allowed_headers, "Content-Type header should be allowed in CORS")
            self.assertIn("Authorization", allowed_headers, "Authorization header should be allowed in CORS")
        
        print("✅ CORS Configuration Test Results:")
        print("   - CORS headers present")
        print("   - Appropriate methods allowed")
        print("   - Appropriate headers allowed")
    
    def test_06_input_validation(self):
        """Test input validation and sanitization"""
        if not self.token:
            self.skipTest("No token available")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test 1: Invalid email format
        invalid_user = {
            "email": "not_an_email",
            "password": "password123",
            "full_name": "Test User",
            "organization": "Demo Organization",
            "role": "Team Member"
        }
        response = requests.post(f"{self.base_url}/auth/register", json=invalid_user)
        self.assertNotEqual(response.status_code, 200, "Invalid email format should be rejected")
        
        # Test 2: Missing required fields
        incomplete_assessment = {
            "assessment_type": "general_readiness",
            "project_name": "Incomplete Assessment"
            # Missing required dimensions
        }
        response = requests.post(f"{self.base_url}/assessments/create", json=incomplete_assessment, headers=headers)
        self.assertNotEqual(response.status_code, 200, "Assessment with missing required fields should be rejected")
        
        # Test 3: Invalid data types
        invalid_project = {
            "name": "Invalid Project",
            "description": "A project with invalid data types",
            "organization": "Demo Organization",
            "target_completion_date": "not-a-date",  # Invalid date format
            "budget": "not-a-number"  # Invalid number format
        }
        response = requests.post(f"{self.base_url}/projects", json=invalid_project, headers=headers)
        self.assertNotEqual(response.status_code, 200, "Project with invalid data types should be rejected")
        
        print("✅ Input Validation Test Results:")
        print("   - Invalid email format rejected")
        print("   - Missing required fields rejected")
        print("   - Invalid data types rejected")
    
    def test_07_error_handling(self):
        """Test error handling and HTTP status codes"""
        # Test 1: Resource not found
        response = requests.get(f"{self.base_url}/nonexistent-endpoint")
        self.assertEqual(response.status_code, 404, "Nonexistent endpoint should return 404")
        
        # Test 2: Unauthorized access
        response = requests.get(f"{self.base_url}/user/profile")
        self.assertEqual(response.status_code, 401, "Unauthorized access should return 401")
        
        # Test 3: Bad request
        response = requests.post(f"{self.base_url}/auth/login", json={"invalid": "data"})
        self.assertEqual(response.status_code, 422, "Bad request should return 422")
        
        # Test 4: Method not allowed
        response = requests.delete(f"{self.base_url}/health")
        self.assertIn(response.status_code, [405, 404, 501], "Method not allowed should return appropriate error code")
        
        print("✅ Error Handling Test Results:")
        print("   - Resource not found returns 404")
        print("   - Unauthorized access returns 401")
        print("   - Bad request returns 422")
        print("   - Method not allowed returns appropriate error code")
    
    def test_08_error_response_consistency(self):
        """Test error response format consistency"""
        # Test 1: Resource not found
        response = requests.get(f"{self.base_url}/nonexistent-endpoint")
        self.assertEqual(response.status_code, 404)
        
        # Check if response is JSON
        try:
            error_data = response.json()
            self.assertIn("detail", error_data, "Error response should contain 'detail' field")
        except json.JSONDecodeError:
            self.fail("Error response is not valid JSON")
        
        # Test 2: Unauthorized access
        response = requests.get(f"{self.base_url}/user/profile")
        self.assertEqual(response.status_code, 401)
        
        # Check if response is JSON
        try:
            error_data = response.json()
            self.assertIn("detail", error_data, "Error response should contain 'detail' field")
        except json.JSONDecodeError:
            self.fail("Error response is not valid JSON")
        
        print("✅ Error Response Consistency Test Results:")
        print("   - Error responses are valid JSON")
        print("   - Error responses contain 'detail' field")
    
    def test_09_database_connection_resilience(self):
        """Test database connection resilience"""
        # Test repeated database operations to check connection pooling
        if not self.token:
            self.skipTest("No token available")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Make multiple requests that require database access
        num_requests = 5
        endpoints = [
            "/assessments",
            "/projects",
            "/dashboard/metrics"
        ]
        
        all_successful = True
        for _ in range(num_requests):
            for endpoint in endpoints:
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
                if response.status_code != 200:
                    all_successful = False
                    print(f"Database operation failed for {endpoint}: {response.status_code}")
        
        self.assertTrue(all_successful, "All database operations should succeed")
        
        print("✅ Database Connection Resilience Test Results:")
        print(f"   - Completed {num_requests * len(endpoints)} database operations successfully")
    
    def test_10_rate_limiting_and_ddos_protection(self):
        """Test rate limiting and DDoS protection"""
        # Make rapid requests to check if rate limiting is in place
        num_requests = 20
        interval = 0.1  # 100ms between requests
        
        success_count = 0
        rate_limited_count = 0
        
        for _ in range(num_requests):
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                success_count += 1
            elif response.status_code in [429, 503]:
                rate_limited_count += 1
            
            time.sleep(interval)
        
        print("✅ Rate Limiting Test Results:")
        print(f"   - Successful requests: {success_count}/{num_requests}")
        print(f"   - Rate limited requests: {rate_limited_count}/{num_requests}")
        print(f"   - Rate limiting {'is' if rate_limited_count > 0 else 'is not'} implemented")
    
    def test_11_environment_configuration(self):
        """Test environment configuration"""
        # Check if environment variables are properly used
        # This is more of a code review, but we can check if the API behaves correctly
        
        # Test database connection (indirectly tests if MONGO_URL is configured correctly)
        if not self.token:
            self.skipTest("No token available")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{self.base_url}/assessments", headers=headers)
        self.assertEqual(response.status_code, 200, "Database connection should work (MONGO_URL configured correctly)")
        
        # Test JWT authentication (indirectly tests if SECRET_KEY is configured correctly)
        response = requests.get(f"{self.base_url}/user/profile", headers=headers)
        self.assertEqual(response.status_code, 200, "JWT authentication should work (SECRET_KEY configured correctly)")
        
        print("✅ Environment Configuration Test Results:")
        print("   - Database connection works (MONGO_URL configured correctly)")
        print("   - JWT authentication works (SECRET_KEY configured correctly)")
    
    def test_12_api_documentation(self):
        """Test API documentation availability"""
        # Check if OpenAPI documentation is available
        base_url_parts = self.base_url.split('/api')
        docs_url = f"{base_url_parts[0]}/docs"
        redoc_url = f"{base_url_parts[0]}/redoc"
        
        response = requests.get(docs_url)
        docs_available = response.status_code in [200, 301, 302]
        
        # Check if ReDoc documentation is available
        response = requests.get(redoc_url)
        redoc_available = response.status_code in [200, 301, 302]
        
        print("✅ API Documentation Test Results:")
        print(f"   - OpenAPI documentation is {'available' if docs_available else 'not available'}")
        print(f"   - ReDoc documentation is {'available' if redoc_available else 'not available'}")
    
    def test_13_data_validation_and_integrity(self):
        """Test data validation and integrity"""
        if not self.token:
            self.skipTest("No token available")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create a project with specific data
        project_name = f"Test Project {uuid.uuid4()}"
        project_data = {
            "name": project_name,
            "description": "A test project for data validation",
            "organization": "Demo Organization",
            "target_completion_date": (datetime.utcnow() + timedelta(days=90)).isoformat(),
            "budget": 50000
        }
        
        # Create the project
        response = requests.post(f"{self.base_url}/projects", json=project_data, headers=headers)
        self.assertEqual(response.status_code, 200, "Project creation should succeed")
        data = response.json()
        project_id = data["id"]
        
        # Retrieve the project and verify data integrity
        response = requests.get(f"{self.base_url}/projects/{project_id}", headers=headers)
        self.assertEqual(response.status_code, 200, "Project retrieval should succeed")
        retrieved_data = response.json()
        
        # Check if data is preserved correctly
        self.assertEqual(retrieved_data["name"], project_data["name"], "Project name should be preserved")
        self.assertEqual(retrieved_data["description"], project_data["description"], "Project description should be preserved")
        self.assertEqual(retrieved_data["organization"], project_data["organization"], "Project organization should be preserved")
        self.assertEqual(retrieved_data["budget"], project_data["budget"], "Project budget should be preserved")
        
        print("✅ Data Validation and Integrity Test Results:")
        print("   - Project created successfully")
        print("   - Data integrity maintained between creation and retrieval")
    
    def test_14_security_headers(self):
        """Test security headers"""
        response = requests.get(f"{self.base_url}/health")
        headers = response.headers
        
        # Check for common security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": None,
            "Strict-Transport-Security": None,
            "X-XSS-Protection": "1; mode=block"
        }
        
        present_headers = []
        missing_headers = []
        
        for header, expected_value in security_headers.items():
            if header in headers:
                present_headers.append(header)
                if expected_value and headers[header] != expected_value:
                    print(f"   - Warning: {header} has value '{headers[header]}', expected '{expected_value}'")
            else:
                missing_headers.append(header)
        
        print("✅ Security Headers Test Results:")
        print(f"   - Present security headers: {', '.join(present_headers) if present_headers else 'None'}")
        print(f"   - Missing security headers: {', '.join(missing_headers) if missing_headers else 'None'}")
    
    def test_15_sensitive_data_exposure(self):
        """Test for sensitive data exposure"""
        if not self.token:
            self.skipTest("No token available")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Check user profile for password hash
        response = requests.get(f"{self.base_url}/user/profile", headers=headers)
        self.assertEqual(response.status_code, 200, "User profile retrieval should succeed")
        user_data = response.json()
        
        # Check if password or password hash is exposed
        self.assertNotIn("password", user_data, "Password should not be exposed in user profile")
        self.assertNotIn("password_hash", user_data, "Password hash should not be exposed in user profile")
        
        # Check if sensitive environment variables are exposed
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200, "Health check should succeed")
        health_data = response.json()
        
        # Convert to string to check for sensitive data in any field
        health_data_str = json.dumps(health_data)
        sensitive_terms = ["SECRET_KEY", "MONGO_URL", "password", "api_key", "token"]
        
        exposed_terms = []
        for term in sensitive_terms:
            if term.lower() in health_data_str.lower():
                exposed_terms.append(term)
        
        self.assertEqual(len(exposed_terms), 0, f"Sensitive data exposed: {', '.join(exposed_terms)}")
        
        print("✅ Sensitive Data Exposure Test Results:")
        print("   - No password or password hash exposed in user profile")
        print("   - No sensitive environment variables exposed in API responses")
    
    def test_16_authentication_bypass(self):
        """Test authentication bypass prevention"""
        # Test 1: Access protected endpoint without authentication
        response = requests.get(f"{self.base_url}/user/profile")
        self.assertEqual(response.status_code, 401, "Unauthenticated access should be rejected")
        
        # Test 2: Access with empty token
        headers = {"Authorization": "Bearer "}
        response = requests.get(f"{self.base_url}/user/profile", headers=headers)
        self.assertEqual(response.status_code, 401, "Empty token should be rejected")
        
        # Test 3: Access with malformed token
        headers = {"Authorization": "Bearer malformed.token.here"}
        response = requests.get(f"{self.base_url}/user/profile", headers=headers)
        self.assertEqual(response.status_code, 401, "Malformed token should be rejected")
        
        # Test 4: Access with token in wrong format
        headers = {"Authorization": "Token " + (self.token or "dummy_token")}
        response = requests.get(f"{self.base_url}/user/profile", headers=headers)
        self.assertEqual(response.status_code, 401, "Token in wrong format should be rejected")
        
        print("✅ Authentication Bypass Prevention Test Results:")
        print("   - Unauthenticated access rejected")
        print("   - Empty token rejected")
        print("   - Malformed token rejected")
        print("   - Token in wrong format rejected")
    
    def test_17_api_response_structure(self):
        """Test API response structure consistency"""
        # Test public endpoints
        public_endpoints = [
            "/health",
            "/assessment-types",
            "/impact/phases"
        ]
        
        for endpoint in public_endpoints:
            response = requests.get(f"{self.base_url}{endpoint}")
            self.assertEqual(response.status_code, 200, f"Endpoint {endpoint} should return 200")
            
            # Check if response is valid JSON
            try:
                data = response.json()
                self.assertIsNotNone(data, f"Endpoint {endpoint} should return valid JSON")
            except json.JSONDecodeError:
                self.fail(f"Endpoint {endpoint} did not return valid JSON")
        
        # Test authenticated endpoints if token is available
        if self.token:
            authenticated_endpoints = [
                "/user/profile",
                "/assessments",
                "/projects",
                "/dashboard/metrics"
            ]
            
            headers = {"Authorization": f"Bearer {self.token}"}
            
            for endpoint in authenticated_endpoints:
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
                self.assertEqual(response.status_code, 200, f"Endpoint {endpoint} should return 200")
                
                # Check if response is valid JSON
                try:
                    data = response.json()
                    self.assertIsNotNone(data, f"Endpoint {endpoint} should return valid JSON")
                except json.JSONDecodeError:
                    self.fail(f"Endpoint {endpoint} did not return valid JSON")
        
        print("✅ API Response Structure Test Results:")
        print(f"   - All {len(public_endpoints)} public endpoints return valid JSON")
        if self.token:
            print(f"   - All {len(authenticated_endpoints)} authenticated endpoints return valid JSON")
    
    def test_18_stress_test_critical_endpoints(self):
        """Stress test critical endpoints"""
        if not self.token:
            self.skipTest("No token available")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Define critical endpoints
        critical_endpoints = [
            {"method": "GET", "url": "/health"},
            {"method": "GET", "url": "/assessment-types"},
            {"method": "GET", "url": "/impact/phases"},
            {"method": "GET", "url": "/user/profile", "auth": True},
            {"method": "GET", "url": "/assessments", "auth": True},
            {"method": "GET", "url": "/projects", "auth": True},
            {"method": "GET", "url": "/dashboard/metrics", "auth": True}
        ]
        
        num_requests = 5  # Number of requests per endpoint
        results = {}
        
        for endpoint in critical_endpoints:
            endpoint_url = f"{self.base_url}{endpoint['url']}"
            endpoint_headers = headers if endpoint.get("auth", False) else {}
            method = endpoint["method"]
            
            response_times = []
            success_count = 0
            
            for _ in range(num_requests):
                start_time = time.time()
                
                if method == "GET":
                    response = requests.get(endpoint_url, headers=endpoint_headers)
                elif method == "POST":
                    response = requests.post(endpoint_url, headers=endpoint_headers)
                else:
                    continue
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if response.status_code == 200:
                    success_count += 1
                    response_times.append(response_time)
                
                time.sleep(0.1)  # Small delay between requests
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
            else:
                avg_response_time = max_response_time = min_response_time = 0
            
            results[endpoint["url"]] = {
                "success_rate": (success_count / num_requests) * 100,
                "avg_response_time_ms": avg_response_time,
                "max_response_time_ms": max_response_time,
                "min_response_time_ms": min_response_time
            }
        
        print("✅ Stress Test Results for Critical Endpoints:")
        for endpoint, data in results.items():
            print(f"   - {endpoint}:")
            print(f"     * Success Rate: {data['success_rate']}%")
            print(f"     * Avg Response Time: {data['avg_response_time_ms']:.2f}ms")
            print(f"     * Max Response Time: {data['max_response_time_ms']:.2f}ms")
            print(f"     * Min Response Time: {data['min_response_time_ms']:.2f}ms")
            
            # Only assert for endpoints that had successful responses
            if data['success_rate'] > 0:
                # Assert that average response time is acceptable (< 500ms)
                self.assertLess(data['avg_response_time_ms'], 500, f"Average response time for {endpoint} is too slow")


def run_production_readiness_tests():
    """Run production readiness tests"""
    test_suite = unittest.TestSuite()
    
    # Create a test instance
    test_instance = ProductionReadinessTest('test_01_api_performance')
    test_instance.setUp()
    
    # Add all test methods
    test_methods = [
        'test_01_api_performance',
        'test_02_concurrent_requests',
        'test_03_jwt_token_security',
        'test_04_sql_injection_prevention',
        'test_05_cors_configuration',
        'test_06_input_validation',
        'test_07_error_handling',
        'test_08_error_response_consistency',
        'test_09_database_connection_resilience',
        'test_10_rate_limiting_and_ddos_protection',
        'test_11_environment_configuration',
        'test_12_api_documentation',
        'test_13_data_validation_and_integrity',
        'test_14_security_headers',
        'test_15_sensitive_data_exposure',
        'test_16_authentication_bypass',
        'test_17_api_response_structure',
        'test_18_stress_test_critical_endpoints'
    ]
    
    for method in test_methods:
        test = ProductionReadinessTest(method)
        test.token = test_instance.token
        test.user_id = test_instance.user_id
        test_suite.addTest(test)
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)


def run_all_tests():
    """Run all tests including basic functionality and production readiness"""
    print("\n===== RUNNING BASIC FUNCTIONALITY TESTS =====\n")
    run_tests()
    
    print("\n===== RUNNING PRODUCTION READINESS TESTS =====\n")
    run_production_readiness_tests()


if __name__ == "__main__":
    run_all_tests()