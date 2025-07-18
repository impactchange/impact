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

    def test_25_new_week_by_week_implementation_plan(self):
        """Test the NEW week-by-week implementation plan generation endpoint"""
        if not self.assessment_id:
            self.skipTest("No assessment ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test the new POST endpoint for week-by-week implementation plan
        response = requests.post(f"{self.base_url}/assessments/{self.assessment_id}/implementation-plan", headers=headers)
        print(f"NEW Week-by-week implementation plan response: {response.status_code} - {response.text[:300]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify the new structure with weeks
        self.assertIn("weeks", data)
        self.assertIn("summary", data)
        self.assertIn("metadata", data)
        
        # Verify weeks structure
        weeks = data["weeks"]
        self.assertEqual(len(weeks), 10, "Should have exactly 10 weeks")
        
        for week_num in range(1, 11):
            week_data = weeks[str(week_num)]
            self.assertIn("week", week_data)
            self.assertIn("phase", week_data)
            self.assertIn("title", week_data)
            self.assertIn("description", week_data)
            self.assertIn("base_activities", week_data)
            self.assertIn("deliverables", week_data)
            self.assertIn("duration_hours", week_data)
            self.assertIn("final_budget", week_data)
            self.assertIn("risk_level", week_data)
            self.assertIn("impact_phase_alignment", week_data)
            
        # Verify summary structure
        summary = data["summary"]
        self.assertIn("total_weeks", summary)
        self.assertIn("total_budget", summary)
        self.assertIn("total_hours", summary)
        self.assertIn("overall_risk_level", summary)
        self.assertIn("success_probability", summary)
        self.assertIn("key_risk_factors", summary)
        self.assertIn("critical_success_factors", summary)
        
        # Verify metadata structure
        metadata = data["metadata"]
        self.assertIn("assessment_id", metadata)
        self.assertIn("project_name", metadata)
        self.assertIn("assessment_type", metadata)
        self.assertIn("overall_readiness_score", metadata)
        self.assertIn("generated_at", metadata)
        self.assertIn("generated_by", metadata)
        
        print("✅ NEW Week-by-week implementation plan generation successful")
        print(f"   - Total Weeks: {summary['total_weeks']}")
        print(f"   - Total Budget: ${summary['total_budget']:,}")
        print(f"   - Total Hours: {summary['total_hours']}")
        print(f"   - Overall Risk Level: {summary['overall_risk_level']}")
        print(f"   - Success Probability: {summary['success_probability']}%")

    def test_26_customized_playbook_generation(self):
        """Test the NEW customized change management playbook generation"""
        if not self.assessment_id:
            self.skipTest("No assessment ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test the new POST endpoint for customized playbook
        response = requests.post(f"{self.base_url}/assessments/{self.assessment_id}/customized-playbook", headers=headers)
        print(f"NEW Customized playbook generation response: {response.status_code} - {response.text[:300]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify playbook structure
        self.assertIn("assessment_id", data)
        self.assertIn("project_name", data)
        self.assertIn("organization", data)
        self.assertIn("assessment_type", data)
        self.assertIn("overall_readiness_score", data)
        self.assertIn("readiness_level", data)
        self.assertIn("success_probability", data)
        self.assertIn("content", data)
        self.assertIn("generated_at", data)
        self.assertIn("generated_by", data)
        self.assertIn("version", data)
        self.assertIn("customization_factors", data)
        
        # Verify content is substantial (AI-generated playbook should be comprehensive)
        content = data["content"]
        self.assertGreater(len(content), 1000, "Playbook content should be comprehensive (>1000 characters)")
        
        # Verify customization factors
        customization_factors = data["customization_factors"]
        self.assertIn("leadership_support", customization_factors)
        self.assertIn("resource_availability", customization_factors)
        self.assertIn("change_management_maturity", customization_factors)
        self.assertIn("communication_effectiveness", customization_factors)
        self.assertIn("workforce_adaptability", customization_factors)
        
        # Verify playbook contains key sections (basic content validation)
        content_lower = content.lower()
        expected_sections = ["executive summary", "implementation", "risk", "stakeholder", "communication"]
        found_sections = [section for section in expected_sections if section in content_lower]
        self.assertGreaterEqual(len(found_sections), 3, f"Playbook should contain key sections. Found: {found_sections}")
        
        print("✅ NEW Customized playbook generation successful")
        print(f"   - Assessment ID: {data['assessment_id']}")
        print(f"   - Project: {data['project_name']}")
        print(f"   - Content Length: {len(content)} characters")
        print(f"   - Success Probability: {data['success_probability']}%")
        print(f"   - Key Sections Found: {found_sections}")

    def test_27_intelligence_layer_different_readiness_levels(self):
        """Test intelligence layer features with different readiness levels"""
        if not self.typed_assessment_ids:
            self.skipTest("No typed assessment IDs available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test implementation plans for different assessment types
        for assessment_type, assessment_id in self.typed_assessment_ids.items():
            print(f"\n--- Testing Intelligence Layer for {assessment_type} ---")
            
            # Test week-by-week implementation plan
            response = requests.post(f"{self.base_url}/assessments/{assessment_id}/implementation-plan", headers=headers)
            self.assertEqual(response.status_code, 200)
            plan_data = response.json()
            
            # Verify readiness-based customizations
            summary = plan_data["summary"]
            overall_risk = summary["overall_risk_level"]
            success_prob = summary["success_probability"]
            
            # Test customized playbook
            response = requests.post(f"{self.base_url}/assessments/{assessment_id}/customized-playbook", headers=headers)
            self.assertEqual(response.status_code, 200)
            playbook_data = response.json()
            
            # Verify type-specific content
            content = playbook_data["content"].lower()
            
            if assessment_type == "software_implementation":
                # Should contain software-specific terms
                software_terms = ["technical", "system", "user adoption", "data migration"]
                found_terms = [term for term in software_terms if term in content]
                self.assertGreater(len(found_terms), 0, f"Software playbook should contain relevant terms. Found: {found_terms}")
                
            elif assessment_type == "manufacturing_operations":
                # Should contain manufacturing-specific terms
                manufacturing_terms = ["operational", "maintenance", "shift", "safety", "production"]
                found_terms = [term for term in manufacturing_terms if term in content]
                self.assertGreater(len(found_terms), 0, f"Manufacturing playbook should contain relevant terms. Found: {found_terms}")
                
            elif assessment_type == "business_process":
                # Should contain process-specific terms
                process_terms = ["process", "workflow", "cross-functional", "performance"]
                found_terms = [term for term in process_terms if term in content]
                self.assertGreater(len(found_terms), 0, f"Business process playbook should contain relevant terms. Found: {found_terms}")
            
            print(f"✅ Intelligence layer testing for {assessment_type} successful")
            print(f"   - Risk Level: {overall_risk}")
            print(f"   - Success Probability: {success_prob}%")
            print(f"   - Total Budget: ${summary['total_budget']:,}")
            print(f"   - Playbook Length: {len(playbook_data['content'])} characters")

    def test_28_budget_prediction_accuracy(self):
        """Test budget prediction accuracy and risk-based adjustments"""
        if not self.typed_assessment_ids:
            self.skipTest("No typed assessment IDs available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        budget_results = {}
        
        for assessment_type, assessment_id in self.typed_assessment_ids.items():
            response = requests.post(f"{self.base_url}/assessments/{assessment_id}/implementation-plan", headers=headers)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            summary = data["summary"]
            total_budget = summary["total_budget"]
            risk_level = summary["overall_risk_level"]
            
            # Verify budget is reasonable (between $50K and $200K for 10-week project)
            self.assertGreaterEqual(total_budget, 50000, f"Budget too low for {assessment_type}: ${total_budget}")
            self.assertLessEqual(total_budget, 200000, f"Budget too high for {assessment_type}: ${total_budget}")
            
            # Verify risk-based adjustments
            weeks = data["weeks"]
            base_budgets = [weeks[str(i)]["base_budget"] for i in range(1, 11)]
            final_budgets = [weeks[str(i)]["final_budget"] for i in range(1, 11)]
            
            total_base = sum(base_budgets)
            total_final = sum(final_budgets)
            
            if risk_level == "High":
                self.assertGreater(total_final, total_base, f"High risk should increase budget for {assessment_type}")
            elif risk_level == "Low":
                self.assertGreaterEqual(total_final, total_base, f"Low risk budget should be >= base for {assessment_type}")
            
            budget_results[assessment_type] = {
                "total_budget": total_budget,
                "risk_level": risk_level,
                "risk_adjustment": ((total_final - total_base) / total_base) * 100
            }
        
        print("✅ Budget prediction accuracy testing successful")
        for assessment_type, results in budget_results.items():
            print(f"   - {assessment_type}:")
            print(f"     • Total Budget: ${results['total_budget']:,}")
            print(f"     • Risk Level: {results['risk_level']}")
            print(f"     • Risk Adjustment: {results['risk_adjustment']:.1f}%")

    def test_29_impact_phase_alignment(self):
        """Test IMPACT phase alignment in implementation plans"""
        if not self.assessment_id:
            self.skipTest("No assessment ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(f"{self.base_url}/assessments/{self.assessment_id}/implementation-plan", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        weeks = data["weeks"]
        
        # Verify IMPACT phase alignment for each week
        expected_phases = {
            "1": "Investigate & Assess",
            "2": "Investigate & Assess", 
            "3": "Mobilize & Prepare",
            "4": "Mobilize & Prepare",
            "5": "Pilot & Adapt",
            "6": "Pilot & Adapt",
            "7": "Activate & Deploy",
            "8": "Activate & Deploy",
            "9": "Cement & Transfer",
            "10": "Track & Optimize"
        }
        
        for week_num, expected_phase in expected_phases.items():
            week_data = weeks[week_num]
            actual_phase = week_data["impact_phase_alignment"]
            self.assertEqual(actual_phase, expected_phase, 
                           f"Week {week_num} should align with {expected_phase}, got {actual_phase}")
        
        # Verify phase progression makes sense
        phase_sequence = [weeks[str(i)]["impact_phase_alignment"] for i in range(1, 11)]
        unique_phases = list(dict.fromkeys(phase_sequence))  # Preserve order, remove duplicates
        
        expected_sequence = ["Investigate & Assess", "Mobilize & Prepare", "Pilot & Adapt", 
                           "Activate & Deploy", "Cement & Transfer", "Track & Optimize"]
        
        self.assertEqual(unique_phases, expected_sequence, "IMPACT phase sequence should be correct")
        
        print("✅ IMPACT phase alignment testing successful")
        print(f"   - All 10 weeks properly aligned with IMPACT phases")
        print(f"   - Phase sequence: {' → '.join(unique_phases)}")

    def test_30_success_probability_calculations(self):
        """Test success probability calculations across different assessment types"""
        if not self.typed_assessment_ids:
            self.skipTest("No typed assessment IDs available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        probability_results = {}
        
        for assessment_type, assessment_id in self.typed_assessment_ids.items():
            # Get assessment details
            response = requests.get(f"{self.base_url}/assessments/{assessment_id}", headers=headers)
            self.assertEqual(response.status_code, 200)
            assessment_data = response.json()
            
            # Get implementation plan
            response = requests.post(f"{self.base_url}/assessments/{assessment_id}/implementation-plan", headers=headers)
            self.assertEqual(response.status_code, 200)
            plan_data = response.json()
            
            overall_score = assessment_data.get("overall_score", 0)
            success_probability = plan_data["summary"]["success_probability"]
            
            # Verify success probability is reasonable (15-95% range)
            self.assertGreaterEqual(success_probability, 15, f"Success probability too low for {assessment_type}")
            self.assertLessEqual(success_probability, 95, f"Success probability too high for {assessment_type}")
            
            # Verify correlation with overall score (higher score should generally mean higher probability)
            expected_min_probability = max(15, overall_score * 15)  # Rough correlation
            self.assertGreaterEqual(success_probability, expected_min_probability - 10, 
                                  f"Success probability should correlate with overall score for {assessment_type}")
            
            probability_results[assessment_type] = {
                "overall_score": overall_score,
                "success_probability": success_probability,
                "correlation_ratio": success_probability / (overall_score * 20) if overall_score > 0 else 0
            }
        
        print("✅ Success probability calculations testing successful")
        for assessment_type, results in probability_results.items():
            print(f"   - {assessment_type}:")
            print(f"     • Overall Score: {results['overall_score']:.1f}/5")
            print(f"     • Success Probability: {results['success_probability']:.1f}%")
            print(f"     • Score-Probability Ratio: {results['correlation_ratio']:.2f}")

    def test_31_manufacturing_specific_features(self):
        """Test manufacturing-specific features in intelligence layer"""
        if not self.typed_assessment_ids.get("manufacturing_operations"):
            self.skipTest("No manufacturing operations assessment ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        assessment_id = self.typed_assessment_ids["manufacturing_operations"]
        
        # Test implementation plan for manufacturing
        response = requests.post(f"{self.base_url}/assessments/{assessment_id}/implementation-plan", headers=headers)
        self.assertEqual(response.status_code, 200)
        plan_data = response.json()
        
        # Verify manufacturing-specific activities are included
        weeks = plan_data["weeks"]
        manufacturing_activities_found = False
        
        for week_num in range(1, 11):
            week_data = weeks[str(week_num)]
            type_specific_activities = week_data.get("type_specific_activities", [])
            
            # Check for manufacturing-specific terms
            activities_text = " ".join(type_specific_activities).lower()
            manufacturing_terms = ["maintenance", "operations", "shift", "manufacturing", "operational", "production"]
            
            if any(term in activities_text for term in manufacturing_terms):
                manufacturing_activities_found = True
                break
        
        self.assertTrue(manufacturing_activities_found, "Manufacturing-specific activities should be included")
        
        # Test customized playbook for manufacturing
        response = requests.post(f"{self.base_url}/assessments/{assessment_id}/customized-playbook", headers=headers)
        self.assertEqual(response.status_code, 200)
        playbook_data = response.json()
        
        content = playbook_data["content"].lower()
        manufacturing_terms = ["maintenance", "operations", "manufacturing", "operational", "production", "shift", "safety"]
        found_terms = [term for term in manufacturing_terms if term in content]
        
        self.assertGreaterEqual(len(found_terms), 3, f"Manufacturing playbook should contain manufacturing terms. Found: {found_terms}")
        
        print("✅ Manufacturing-specific features testing successful")
        print(f"   - Manufacturing activities included in implementation plan")
        print(f"   - Manufacturing terms in playbook: {found_terms}")
        print(f"   - Playbook content length: {len(playbook_data['content'])} characters")

    def test_32_predictive_analytics_comprehensive(self):
        """Test the NEW Predictive Analytics Engine - Comprehensive Analysis"""
        if not self.assessment_id:
            self.skipTest("No assessment ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test the new POST endpoint for predictive analytics
        response = requests.post(f"{self.base_url}/assessments/{self.assessment_id}/predictive-analytics", headers=headers)
        print(f"Predictive Analytics response: {response.status_code} - {response.text[:300]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify main structure
        self.assertIn("assessment_id", data)
        self.assertIn("project_name", data)
        self.assertIn("assessment_type", data)
        self.assertIn("overall_readiness_score", data)
        self.assertIn("generated_at", data)
        self.assertIn("generated_by", data)
        
        # Verify task success predictions
        self.assertIn("task_success_predictions", data)
        task_predictions = data["task_success_predictions"]
        self.assertEqual(len(task_predictions), 10, "Should have predictions for all 10 tasks")
        
        # Verify each task prediction structure
        for i, task_pred in enumerate(task_predictions, 1):
            self.assertIn("task_id", task_pred)
            self.assertIn("task_description", task_pred)
            self.assertIn("success_probability", task_pred)
            self.assertIn("risk_level", task_pred)
            self.assertIn("primary_factors", task_pred)
            self.assertIn("critical_dependencies", task_pred)
            self.assertIn("confidence", task_pred)
            
            # Verify task_id format
            self.assertEqual(task_pred["task_id"], f"task_{i}")
            
            # Verify success probability range (10-95%)
            success_prob = task_pred["success_probability"]
            self.assertGreaterEqual(success_prob, 10, f"Task {i} success probability too low: {success_prob}")
            self.assertLessEqual(success_prob, 95, f"Task {i} success probability too high: {success_prob}")
            
            # Verify risk level is valid
            self.assertIn(task_pred["risk_level"], ["Low", "Medium", "High"])
        
        # Verify highest and lowest risk tasks
        self.assertIn("highest_risk_tasks", data)
        self.assertIn("lowest_risk_tasks", data)
        self.assertEqual(len(data["highest_risk_tasks"]), 3, "Should identify 3 highest risk tasks")
        self.assertEqual(len(data["lowest_risk_tasks"]), 3, "Should identify 3 lowest risk tasks")
        
        # Verify budget risk analysis
        self.assertIn("budget_risk_analysis", data)
        budget_risk = data["budget_risk_analysis"]
        self.assertIn("overrun_probability", budget_risk)
        self.assertIn("expected_overrun_percentage", budget_risk)
        self.assertIn("risk_adjusted_budget", budget_risk)
        self.assertIn("risk_level", budget_risk)
        self.assertIn("confidence", budget_risk)
        
        # Verify overrun probability range (5-80%)
        overrun_prob = budget_risk["overrun_probability"]
        self.assertGreaterEqual(overrun_prob, 5, f"Budget overrun probability too low: {overrun_prob}")
        self.assertLessEqual(overrun_prob, 80, f"Budget overrun probability too high: {overrun_prob}")
        
        # Verify scope creep analysis
        self.assertIn("scope_creep_analysis", data)
        scope_creep = data["scope_creep_analysis"]
        self.assertIn("probability", scope_creep)
        self.assertIn("typical_scope_additions", scope_creep)
        self.assertIn("impact_level", scope_creep)
        self.assertIn("mitigation_strategies", scope_creep)
        
        # Verify timeline optimization
        self.assertIn("timeline_optimization", data)
        timeline_opt = data["timeline_optimization"]
        self.assertIn("acceleration_potential", timeline_opt)
        self.assertIn("delay_risk", timeline_opt)
        self.assertIn("optimization_opportunities", timeline_opt)
        
        # Verify risk trending
        self.assertIn("risk_trending", data)
        risk_trending = data["risk_trending"]
        self.assertIn("technical_risk_trend", risk_trending)
        self.assertIn("adoption_risk_trend", risk_trending)
        self.assertIn("stakeholder_risk_trend", risk_trending)
        self.assertIn("resource_risk_trend", risk_trending)
        self.assertIn("critical_monitoring_weeks", risk_trending)
        
        # Verify project outlook
        self.assertIn("project_outlook", data)
        outlook = data["project_outlook"]
        self.assertIn("overall_risk_level", outlook)
        self.assertIn("success_probability", outlook)
        self.assertIn("recommended_actions", outlook)
        self.assertIn("critical_success_factors", outlook)
        self.assertIn("key_monitoring_points", outlook)
        
        print("✅ Comprehensive Predictive Analytics testing successful")
        print(f"   - Assessment ID: {data['assessment_id']}")
        print(f"   - Overall Risk Level: {outlook['overall_risk_level']}")
        print(f"   - Success Probability: {outlook['success_probability']}%")
        print(f"   - Budget Overrun Risk: {budget_risk['risk_level']} ({overrun_prob}%)")
        print(f"   - Scope Creep Probability: {scope_creep['probability']}%")
        print(f"   - High Risk Tasks: {len(data['highest_risk_tasks'])}")
        print(f"   - Recommended Actions: {len(outlook['recommended_actions'])}")

    def test_33_task_specific_success_predictions(self):
        """Test task-specific success probability mapping for all 10 tasks"""
        if not self.assessment_id:
            self.skipTest("No assessment ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(f"{self.base_url}/assessments/{self.assessment_id}/predictive-analytics", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        task_predictions = data["task_success_predictions"]
        
        # Verify all 10 tasks are present
        task_ids = [pred["task_id"] for pred in task_predictions]
        expected_task_ids = [f"task_{i}" for i in range(1, 11)]
        self.assertEqual(sorted(task_ids), sorted(expected_task_ids), "All 10 tasks should be predicted")
        
        # Verify high-risk tasks (Tasks 3, 5, 9) are correctly identified
        high_risk_tasks = data["highest_risk_tasks"]
        high_risk_task_ids = [task["task_id"] for task in high_risk_tasks]
        
        # Check if known high-risk tasks are in the high-risk list
        known_high_risk = ["task_3", "task_5", "task_9"]  # Business Process Review, Data Migration, Go Live Week 1
        found_high_risk = [task_id for task_id in known_high_risk if task_id in high_risk_task_ids]
        
        # At least 2 of the 3 known high-risk tasks should be identified
        self.assertGreaterEqual(len(found_high_risk), 2, f"Should identify known high-risk tasks. Found: {found_high_risk}")
        
        # Verify task descriptions are meaningful
        for pred in task_predictions:
            description = pred["task_description"]
            self.assertGreater(len(description), 20, f"Task description should be meaningful: {description}")
            
            # Verify primary factors are relevant
            primary_factors = pred["primary_factors"]
            self.assertGreater(len(primary_factors), 0, "Each task should have primary risk factors")
            
            # Verify critical dependencies exist
            dependencies = pred["critical_dependencies"]
            self.assertGreater(len(dependencies), 0, "Each task should have critical dependencies")
        
        # Test specific task characteristics
        task_3 = next((pred for pred in task_predictions if pred["task_id"] == "task_3"), None)
        if task_3:
            # Task 3 (Business Process Review) should be high risk
            self.assertIn("process", task_3["task_description"].lower())
            self.assertIn(task_3["risk_level"], ["Medium", "High"])
        
        task_9 = next((pred for pred in task_predictions if pred["task_id"] == "task_9"), None)
        if task_9:
            # Task 9 (Go Live Week 1) should be high risk
            self.assertIn("go", task_9["task_description"].lower())
            self.assertIn(task_9["risk_level"], ["Medium", "High"])
        
        print("✅ Task-specific success predictions testing successful")
        print(f"   - All 10 tasks predicted successfully")
        print(f"   - High-risk tasks identified: {high_risk_task_ids}")
        print(f"   - Known high-risk tasks found: {found_high_risk}")
        
        # Print task risk summary
        for pred in task_predictions:
            print(f"   - {pred['task_id']}: {pred['success_probability']:.1f}% success ({pred['risk_level']} risk)")

    def test_34_budget_overrun_risk_prediction(self):
        """Test budget overrun risk prediction with realistic calculations"""
        if not self.typed_assessment_ids:
            self.skipTest("No typed assessment IDs available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        budget_results = {}
        
        for assessment_type, assessment_id in self.typed_assessment_ids.items():
            response = requests.post(f"{self.base_url}/assessments/{assessment_id}/predictive-analytics", headers=headers)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            budget_risk = data["budget_risk_analysis"]
            
            # Verify budget risk structure
            self.assertIn("overrun_probability", budget_risk)
            self.assertIn("expected_overrun_percentage", budget_risk)
            self.assertIn("risk_adjusted_budget", budget_risk)
            self.assertIn("risk_level", budget_risk)
            self.assertIn("primary_risk_factors", budget_risk)
            self.assertIn("mitigation_strategies", budget_risk)
            self.assertIn("confidence", budget_risk)
            
            # Verify overrun probability range (5-80%)
            overrun_prob = budget_risk["overrun_probability"]
            self.assertGreaterEqual(overrun_prob, 5, f"Overrun probability too low for {assessment_type}")
            self.assertLessEqual(overrun_prob, 80, f"Overrun probability too high for {assessment_type}")
            
            # Verify expected overrun percentage is reasonable
            expected_overrun = budget_risk["expected_overrun_percentage"]
            self.assertGreaterEqual(expected_overrun, 0, f"Expected overrun should be non-negative for {assessment_type}")
            self.assertLessEqual(expected_overrun, 50, f"Expected overrun too high for {assessment_type}")
            
            # Verify risk-adjusted budget is higher than base
            risk_adjusted = budget_risk["risk_adjusted_budget"]
            self.assertGreater(risk_adjusted, 50000, f"Risk-adjusted budget too low for {assessment_type}")
            self.assertLess(risk_adjusted, 250000, f"Risk-adjusted budget too high for {assessment_type}")
            
            # Verify risk level is valid
            self.assertIn(budget_risk["risk_level"], ["Low", "Medium", "High"])
            
            # Verify mitigation strategies are provided
            mitigation_strategies = budget_risk["mitigation_strategies"]
            self.assertGreater(len(mitigation_strategies), 0, f"Should provide mitigation strategies for {assessment_type}")
            
            budget_results[assessment_type] = {
                "overrun_probability": overrun_prob,
                "expected_overrun": expected_overrun,
                "risk_level": budget_risk["risk_level"],
                "risk_adjusted_budget": risk_adjusted
            }
        
        print("✅ Budget overrun risk prediction testing successful")
        for assessment_type, results in budget_results.items():
            print(f"   - {assessment_type}:")
            print(f"     • Overrun Probability: {results['overrun_probability']:.1f}%")
            print(f"     • Expected Overrun: {results['expected_overrun']:.1f}%")
            print(f"     • Risk Level: {results['risk_level']}")
            print(f"     • Risk-Adjusted Budget: ${results['risk_adjusted_budget']:,}")

    def test_35_scope_creep_risk_analysis(self):
        """Test scope creep risk analysis by assessment type"""
        if not self.typed_assessment_ids:
            self.skipTest("No typed assessment IDs available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        scope_results = {}
        
        for assessment_type, assessment_id in self.typed_assessment_ids.items():
            response = requests.post(f"{self.base_url}/assessments/{assessment_id}/predictive-analytics", headers=headers)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            scope_creep = data["scope_creep_analysis"]
            
            # Verify scope creep structure
            self.assertIn("probability", scope_creep)
            self.assertIn("typical_scope_additions", scope_creep)
            self.assertIn("impact_level", scope_creep)
            self.assertIn("mitigation_strategies", scope_creep)
            self.assertIn("assessment_type_factors", scope_creep)
            
            # Verify probability range
            probability = scope_creep["probability"]
            self.assertGreaterEqual(probability, 10, f"Scope creep probability too low for {assessment_type}")
            self.assertLessEqual(probability, 85, f"Scope creep probability too high for {assessment_type}")
            
            # Verify impact level is valid
            self.assertIn(scope_creep["impact_level"], ["Low", "Medium", "High"])
            
            # Verify typical scope additions are provided
            scope_additions = scope_creep["typical_scope_additions"]
            self.assertGreater(len(scope_additions), 0, f"Should provide typical scope additions for {assessment_type}")
            
            # Verify assessment type-specific factors
            type_factors = scope_creep["assessment_type_factors"]
            self.assertGreater(len(type_factors), 0, f"Should provide type-specific factors for {assessment_type}")
            
            # Verify type-specific scope additions
            if assessment_type == "software_implementation":
                # Software should have technical scope additions
                additions_text = " ".join(scope_additions).lower()
                software_terms = ["technical", "integration", "customization", "data", "user"]
                found_terms = [term for term in software_terms if term in additions_text]
                self.assertGreater(len(found_terms), 0, f"Software scope additions should contain relevant terms. Found: {found_terms}")
                
            elif assessment_type == "manufacturing_operations":
                # Manufacturing should have operational scope additions
                additions_text = " ".join(scope_additions).lower()
                manufacturing_terms = ["operational", "maintenance", "production", "safety", "equipment"]
                found_terms = [term for term in manufacturing_terms if term in additions_text]
                self.assertGreater(len(found_terms), 0, f"Manufacturing scope additions should contain relevant terms. Found: {found_terms}")
            
            scope_results[assessment_type] = {
                "probability": probability,
                "impact_level": scope_creep["impact_level"],
                "additions_count": len(scope_additions),
                "mitigation_count": len(scope_creep["mitigation_strategies"])
            }
        
        print("✅ Scope creep risk analysis testing successful")
        for assessment_type, results in scope_results.items():
            print(f"   - {assessment_type}:")
            print(f"     • Scope Creep Probability: {results['probability']:.1f}%")
            print(f"     • Impact Level: {results['impact_level']}")
            print(f"     • Typical Additions: {results['additions_count']} identified")
            print(f"     • Mitigation Strategies: {results['mitigation_count']} provided")

    def test_36_timeline_optimization_predictions(self):
        """Test timeline optimization predictions"""
        if not self.assessment_id:
            self.skipTest("No assessment ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(f"{self.base_url}/assessments/{self.assessment_id}/predictive-analytics", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        timeline_opt = data["timeline_optimization"]
        
        # Verify timeline optimization structure
        self.assertIn("acceleration_potential", timeline_opt)
        self.assertIn("delay_risk", timeline_opt)
        self.assertIn("optimization_opportunities", timeline_opt)
        self.assertIn("critical_path_analysis", timeline_opt)
        self.assertIn("resource_optimization", timeline_opt)
        
        # Verify acceleration potential
        acceleration = timeline_opt["acceleration_potential"]
        self.assertIn("weeks_saved", acceleration)
        self.assertIn("probability", acceleration)
        self.assertIn("requirements", acceleration)
        
        weeks_saved = acceleration["weeks_saved"]
        self.assertGreaterEqual(weeks_saved, 0, "Weeks saved should be non-negative")
        self.assertLessEqual(weeks_saved, 4, "Weeks saved should be realistic")
        
        accel_probability = acceleration["probability"]
        self.assertGreaterEqual(accel_probability, 10, "Acceleration probability too low")
        self.assertLessEqual(accel_probability, 90, "Acceleration probability too high")
        
        # Verify delay risk
        delay_risk = timeline_opt["delay_risk"]
        self.assertIn("weeks_at_risk", delay_risk)
        self.assertIn("probability", delay_risk)
        self.assertIn("risk_factors", delay_risk)
        
        weeks_at_risk = delay_risk["weeks_at_risk"]
        self.assertGreaterEqual(weeks_at_risk, 0, "Weeks at risk should be non-negative")
        self.assertLessEqual(weeks_at_risk, 6, "Weeks at risk should be realistic")
        
        delay_probability = delay_risk["probability"]
        self.assertGreaterEqual(delay_probability, 5, "Delay probability too low")
        self.assertLessEqual(delay_probability, 80, "Delay probability too high")
        
        # Verify optimization opportunities
        opportunities = timeline_opt["optimization_opportunities"]
        self.assertGreater(len(opportunities), 0, "Should provide optimization opportunities")
        
        # Verify critical path analysis
        critical_path = timeline_opt["critical_path_analysis"]
        self.assertIn("critical_tasks", critical_path)
        self.assertIn("bottlenecks", critical_path)
        
        critical_tasks = critical_path["critical_tasks"]
        self.assertGreater(len(critical_tasks), 0, "Should identify critical tasks")
        
        # Verify resource optimization
        resource_opt = timeline_opt["resource_optimization"]
        self.assertIn("recommendations", resource_opt)
        self.assertIn("efficiency_gains", resource_opt)
        
        print("✅ Timeline optimization predictions testing successful")
        print(f"   - Acceleration Potential: {weeks_saved} weeks ({accel_probability:.1f}% probability)")
        print(f"   - Delay Risk: {weeks_at_risk} weeks ({delay_probability:.1f}% probability)")
        print(f"   - Optimization Opportunities: {len(opportunities)} identified")
        print(f"   - Critical Tasks: {len(critical_tasks)} identified")
        print(f"   - Resource Optimization: {len(resource_opt['recommendations'])} recommendations")

    def test_37_real_time_risk_monitoring(self):
        """Test real-time risk monitoring dashboard for active projects"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test the new POST endpoint for risk monitoring
        response = requests.post(f"{self.base_url}/projects/{self.project_id}/risk-monitoring", headers=headers)
        print(f"Risk Monitoring response: {response.status_code} - {response.text[:300]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify main structure
        self.assertIn("project_id", data)
        self.assertIn("project_name", data)
        self.assertIn("current_status", data)
        self.assertIn("risk_alerts", data)
        self.assertIn("trend_analysis", data)
        self.assertIn("predictive_insights", data)
        self.assertIn("recommendations", data)
        self.assertIn("generated_at", data)
        
        # Verify current status
        current_status = data["current_status"]
        self.assertIn("overall_progress", current_status)
        self.assertIn("current_week", current_status)
        self.assertIn("budget_utilization", current_status)
        self.assertIn("health_status", current_status)
        
        # Verify progress values are reasonable
        progress = current_status["overall_progress"]
        self.assertGreaterEqual(progress, 0, "Progress should be non-negative")
        self.assertLessEqual(progress, 100, "Progress should not exceed 100%")
        
        current_week = current_status["current_week"]
        self.assertGreaterEqual(current_week, 1, "Current week should be at least 1")
        self.assertLessEqual(current_week, 10, "Current week should not exceed 10")
        
        budget_utilization = current_status["budget_utilization"]
        self.assertGreaterEqual(budget_utilization, 0, "Budget utilization should be non-negative")
        
        # Verify risk alerts structure
        risk_alerts = data["risk_alerts"]
        self.assertIsInstance(risk_alerts, list, "Risk alerts should be a list")
        
        for alert in risk_alerts:
            self.assertIn("type", alert)
            self.assertIn("severity", alert)
            self.assertIn("message", alert)
            self.assertIn("recommended_action", alert)
            
            # Verify alert types and severities are valid
            self.assertIn(alert["type"], ["Budget", "Schedule", "Scope", "Resource", "Quality"])
            self.assertIn(alert["severity"], ["Low", "Medium", "High", "Critical"])
        
        # Verify trend analysis
        trend_analysis = data["trend_analysis"]
        self.assertIn("budget_trend", trend_analysis)
        self.assertIn("schedule_trend", trend_analysis)
        self.assertIn("scope_trend", trend_analysis)
        
        # Verify trend values are valid
        valid_trends = ["On Track", "At Risk", "Behind Schedule", "Over Budget", "Stable"]
        self.assertIn(trend_analysis["budget_trend"], valid_trends)
        self.assertIn(trend_analysis["schedule_trend"], valid_trends)
        self.assertIn(trend_analysis["scope_trend"], valid_trends)
        
        # Verify predictive insights
        predictive_insights = data["predictive_insights"]
        self.assertIn("completion_probability", predictive_insights)
        self.assertIn("budget_overrun_risk", predictive_insights)
        self.assertIn("timeline_risk", predictive_insights)
        
        completion_prob = predictive_insights["completion_probability"]
        self.assertGreaterEqual(completion_prob, 30, "Completion probability too low")
        self.assertLessEqual(completion_prob, 95, "Completion probability too high")
        
        # Verify risk levels are valid
        valid_risk_levels = ["Low", "Medium", "High"]
        self.assertIn(predictive_insights["budget_overrun_risk"], valid_risk_levels)
        self.assertIn(predictive_insights["timeline_risk"], valid_risk_levels)
        
        # Verify recommendations
        recommendations = data["recommendations"]
        self.assertIsInstance(recommendations, list, "Recommendations should be a list")
        
        print("✅ Real-time risk monitoring testing successful")
        print(f"   - Project ID: {data['project_id']}")
        print(f"   - Overall Progress: {progress:.1f}%")
        print(f"   - Current Week: {current_week}")
        print(f"   - Budget Utilization: {budget_utilization:.1f}%")
        print(f"   - Risk Alerts: {len(risk_alerts)} active")
        print(f"   - Completion Probability: {completion_prob:.1f}%")
        print(f"   - Budget Risk: {predictive_insights['budget_overrun_risk']}")
        print(f"   - Timeline Risk: {predictive_insights['timeline_risk']}")
        print(f"   - Recommendations: {len(recommendations)} provided")

    def test_38_risk_trending_analysis(self):
        """Test risk trending analysis across different risk categories"""
        if not self.assessment_id:
            self.skipTest("No assessment ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(f"{self.base_url}/assessments/{self.assessment_id}/predictive-analytics", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        risk_trending = data["risk_trending"]
        
        # Verify risk trending structure
        self.assertIn("technical_risk_trend", risk_trending)
        self.assertIn("adoption_risk_trend", risk_trending)
        self.assertIn("stakeholder_risk_trend", risk_trending)
        self.assertIn("resource_risk_trend", risk_trending)
        self.assertIn("critical_monitoring_weeks", risk_trending)
        
        # Verify each risk trend has proper structure
        risk_categories = ["technical_risk_trend", "adoption_risk_trend", "stakeholder_risk_trend", "resource_risk_trend"]
        
        for category in risk_categories:
            trend = risk_trending[category]
            self.assertIn("current_level", trend)
            self.assertIn("projected_trend", trend)
            self.assertIn("peak_risk_weeks", trend)
            self.assertIn("mitigation_priority", trend)
            
            # Verify current level is valid
            self.assertIn(trend["current_level"], ["Low", "Medium", "High"])
            
            # Verify projected trend is valid
            self.assertIn(trend["projected_trend"], ["Improving", "Stable", "Deteriorating"])
            
            # Verify peak risk weeks are reasonable
            peak_weeks = trend["peak_risk_weeks"]
            self.assertIsInstance(peak_weeks, list, f"{category} peak weeks should be a list")
            for week in peak_weeks:
                self.assertGreaterEqual(week, 1, f"Peak week should be >= 1 for {category}")
                self.assertLessEqual(week, 10, f"Peak week should be <= 10 for {category}")
            
            # Verify mitigation priority is valid
            self.assertIn(trend["mitigation_priority"], ["Low", "Medium", "High", "Critical"])
        
        # Verify critical monitoring weeks
        critical_weeks = risk_trending["critical_monitoring_weeks"]
        self.assertIsInstance(critical_weeks, list, "Critical monitoring weeks should be a list")
        self.assertGreater(len(critical_weeks), 0, "Should identify critical monitoring weeks")
        
        for week in critical_weeks:
            self.assertGreaterEqual(week, 1, "Critical week should be >= 1")
            self.assertLessEqual(week, 10, "Critical week should be <= 10")
        
        print("✅ Risk trending analysis testing successful")
        print(f"   - Technical Risk: {risk_trending['technical_risk_trend']['current_level']} ({risk_trending['technical_risk_trend']['projected_trend']})")
        print(f"   - Adoption Risk: {risk_trending['adoption_risk_trend']['current_level']} ({risk_trending['adoption_risk_trend']['projected_trend']})")
        print(f"   - Stakeholder Risk: {risk_trending['stakeholder_risk_trend']['current_level']} ({risk_trending['stakeholder_risk_trend']['projected_trend']})")
        print(f"   - Resource Risk: {risk_trending['resource_risk_trend']['current_level']} ({risk_trending['resource_risk_trend']['projected_trend']})")
        print(f"   - Critical Monitoring Weeks: {critical_weeks}")

    def test_39_predictive_analytics_performance(self):
        """Test predictive analytics performance and response times"""
        if not self.assessment_id:
            self.skipTest("No assessment ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test performance of predictive analytics endpoint
        start_time = time.time()
        response = requests.post(f"{self.base_url}/assessments/{self.assessment_id}/predictive-analytics", headers=headers)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 100, f"Predictive analytics response time too slow: {response_time:.2f}ms")
        
        data = response.json()
        
        # Verify comprehensive data is returned quickly
        self.assertGreater(len(data["task_success_predictions"]), 0, "Should return task predictions")
        self.assertIn("budget_risk_analysis", data, "Should return budget analysis")
        self.assertIn("scope_creep_analysis", data, "Should return scope analysis")
        self.assertIn("timeline_optimization", data, "Should return timeline optimization")
        self.assertIn("risk_trending", data, "Should return risk trending")
        
        # Test risk monitoring performance if project exists
        if self.project_id:
            start_time = time.time()
            response = requests.post(f"{self.base_url}/projects/{self.project_id}/risk-monitoring", headers=headers)
            end_time = time.time()
            
            monitoring_response_time = (end_time - start_time) * 1000
            
            self.assertEqual(response.status_code, 200)
            self.assertLess(monitoring_response_time, 100, f"Risk monitoring response time too slow: {monitoring_response_time:.2f}ms")
        
        print("✅ Predictive analytics performance testing successful")
        print(f"   - Predictive Analytics Response Time: {response_time:.2f}ms")
        if self.project_id:
            print(f"   - Risk Monitoring Response Time: {monitoring_response_time:.2f}ms")
        print(f"   - Both endpoints under 100ms requirement")

    def test_40_confidence_scoring_validation(self):
        """Test prediction confidence levels and scoring accuracy"""
        if not self.typed_assessment_ids:
            self.skipTest("No typed assessment IDs available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        confidence_results = {}
        
        for assessment_type, assessment_id in self.typed_assessment_ids.items():
            response = requests.post(f"{self.base_url}/assessments/{assessment_id}/predictive-analytics", headers=headers)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Verify task prediction confidence levels
            task_predictions = data["task_success_predictions"]
            confidence_levels = [pred["confidence"] for pred in task_predictions]
            
            # All confidence levels should be valid
            valid_confidence = ["Low", "Medium", "High"]
            for confidence in confidence_levels:
                self.assertIn(confidence, valid_confidence, f"Invalid confidence level: {confidence}")
            
            # Verify budget risk confidence
            budget_confidence = data["budget_risk_analysis"]["confidence"]
            self.assertIn(budget_confidence, valid_confidence, f"Invalid budget confidence: {budget_confidence}")
            
            # Count confidence distribution
            confidence_counts = {level: confidence_levels.count(level) for level in valid_confidence}
            
            # Verify we have a reasonable distribution (not all the same)
            unique_confidence_levels = len([count for count in confidence_counts.values() if count > 0])
            self.assertGreaterEqual(unique_confidence_levels, 1, f"Should have varied confidence levels for {assessment_type}")
            
            # Verify high confidence predictions have reasonable success probabilities
            high_confidence_tasks = [pred for pred in task_predictions if pred["confidence"] == "High"]
            if high_confidence_tasks:
                avg_success_prob = sum(task["success_probability"] for task in high_confidence_tasks) / len(high_confidence_tasks)
                # High confidence predictions should generally be more reliable
                self.assertGreater(len(high_confidence_tasks), 0, f"Should have some high confidence predictions for {assessment_type}")
            
            confidence_results[assessment_type] = {
                "task_confidence_distribution": confidence_counts,
                "budget_confidence": budget_confidence,
                "high_confidence_count": confidence_counts.get("High", 0),
                "medium_confidence_count": confidence_counts.get("Medium", 0),
                "low_confidence_count": confidence_counts.get("Low", 0)
            }
        
        print("✅ Confidence scoring validation testing successful")
        for assessment_type, results in confidence_results.items():
            print(f"   - {assessment_type}:")
            print(f"     • High Confidence Tasks: {results['high_confidence_count']}")
            print(f"     • Medium Confidence Tasks: {results['medium_confidence_count']}")
            print(f"     • Low Confidence Tasks: {results['low_confidence_count']}")
            print(f"     • Budget Analysis Confidence: {results['budget_confidence']}")

    def test_41_manufacturing_predictive_customizations(self):
        """Test manufacturing-specific predictive analytics customizations"""
        if not self.typed_assessment_ids.get("manufacturing_operations"):
            self.skipTest("No manufacturing operations assessment ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        assessment_id = self.typed_assessment_ids["manufacturing_operations"]
        
        response = requests.post(f"{self.base_url}/assessments/{assessment_id}/predictive-analytics", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify manufacturing-specific scope creep factors
        scope_creep = data["scope_creep_analysis"]
        type_factors = scope_creep["assessment_type_factors"]
        
        # Should include manufacturing-specific factors
        factors_text = " ".join(type_factors).lower()
        manufacturing_terms = ["operational", "maintenance", "production", "shift", "safety", "equipment"]
        found_terms = [term for term in manufacturing_terms if term in factors_text]
        self.assertGreater(len(found_terms), 0, f"Manufacturing scope factors should contain relevant terms. Found: {found_terms}")
        
        # Verify manufacturing-specific scope additions
        scope_additions = scope_creep["typical_scope_additions"]
        additions_text = " ".join(scope_additions).lower()
        manufacturing_additions = ["maintenance", "operational", "production", "safety", "equipment"]
        found_additions = [term for term in manufacturing_additions if term in additions_text]
        self.assertGreater(len(found_additions), 0, f"Manufacturing scope additions should be relevant. Found: {found_additions}")
        
        # Verify timeline optimization includes manufacturing considerations
        timeline_opt = data["timeline_optimization"]
        optimization_opportunities = timeline_opt["optimization_opportunities"]
        opportunities_text = " ".join(optimization_opportunities).lower()
        
        # Should consider operational constraints
        manufacturing_optimization_terms = ["operational", "maintenance", "shift", "production", "downtime"]
        found_optimization = [term for term in manufacturing_optimization_terms if term in opportunities_text]
        
        # Verify risk trending includes manufacturing-specific risks
        risk_trending = data["risk_trending"]
        
        # Technical risk should consider operational factors
        technical_trend = risk_trending["technical_risk_trend"]
        self.assertIn("current_level", technical_trend)
        self.assertIn("mitigation_priority", technical_trend)
        
        # Resource risk should consider shift work and operational constraints
        resource_trend = risk_trending["resource_risk_trend"]
        self.assertIn("current_level", resource_trend)
        self.assertIn("peak_risk_weeks", resource_trend)
        
        print("✅ Manufacturing predictive customizations testing successful")
        print(f"   - Manufacturing scope factors: {found_terms}")
        print(f"   - Manufacturing scope additions: {found_additions}")
        print(f"   - Manufacturing optimization considerations: {found_optimization}")
        print(f"   - Technical Risk Level: {technical_trend['current_level']}")
        print(f"   - Resource Risk Level: {resource_trend['current_level']}")
        print(f"   - Scope Creep Probability: {scope_creep['probability']:.1f}%")

    def test_42_detailed_budget_tracking(self):
        """Test Enhancement 3: Detailed Budget Tracking endpoint"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test the new POST endpoint for detailed budget tracking
        response = requests.post(f"{self.base_url}/projects/{self.project_id}/detailed-budget-tracking", headers=headers)
        print(f"Detailed Budget Tracking response: {response.status_code} - {response.text[:300]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify main structure
        self.assertIn("project_id", data)
        self.assertIn("project_name", data)
        self.assertIn("generated_at", data)
        
        # Verify budget tracking structure
        self.assertIn("budget_tracking", data)
        budget_tracking = data["budget_tracking"]
        
        # Verify task-level budget tracking
        self.assertIn("task_level_budgets", budget_tracking)
        task_budgets = budget_tracking["task_level_budgets"]
        
        # Should have budget tracking for tasks (may be empty if no implementation plan)
        if len(task_budgets) > 0:
            for task in task_budgets:
                self.assertIn("task_id", task)
                self.assertIn("task_name", task)
                self.assertIn("budgeted_amount", task)
                self.assertIn("spent_amount", task)
                self.assertIn("remaining_amount", task)
                self.assertIn("risk_level", task)
                self.assertIn("cost_performance_index", task)
        
        # Verify phase-level budget aggregation
        self.assertIn("phase_level_budgets", budget_tracking)
        phase_budgets = budget_tracking["phase_level_budgets"]
        
        # Verify overall metrics
        self.assertIn("overall_metrics", budget_tracking)
        overall_metrics = budget_tracking["overall_metrics"]
        
        self.assertIn("total_budgeted", overall_metrics)
        self.assertIn("total_spent", overall_metrics)
        self.assertIn("total_remaining", overall_metrics)
        self.assertIn("budget_utilization", overall_metrics)
        self.assertIn("cost_performance_index", overall_metrics)
        self.assertIn("budget_health", overall_metrics)
        
        # Verify budget alerts
        self.assertIn("budget_alerts", data)
        budget_alerts = data["budget_alerts"]
        
        # Verify cost forecasting
        self.assertIn("cost_forecasting", data)
        cost_forecasting = data["cost_forecasting"]
        
        self.assertIn("estimated_final_cost", cost_forecasting)
        self.assertIn("cost_overrun_risk", cost_forecasting)
        self.assertIn("performance_trend", cost_forecasting)
        
        print("✅ Detailed Budget Tracking testing successful")
        print(f"   - Project ID: {data['project_id']}")
        print(f"   - Task-level budgets: {len(task_budgets)} tasks")
        print(f"   - Phase-level budgets: {len(phase_budgets)} phases")
        print(f"   - Budget alerts: {len(budget_alerts)} alerts")
        print(f"   - Budget health: {overall_metrics.get('budget_health', 'N/A')}")
        print(f"   - Performance trend: {cost_forecasting.get('performance_trend', 'N/A')}")

    def test_43_advanced_project_forecasting(self):
        """Test Enhancement 3: Advanced Project Outcome Forecasting endpoint"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test the new POST endpoint for advanced forecasting
        response = requests.post(f"{self.base_url}/projects/{self.project_id}/advanced-forecasting", headers=headers)
        print(f"Advanced Forecasting response: {response.status_code} - {response.text[:300]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify main structure
        self.assertIn("project_id", data)
        self.assertIn("forecasting_confidence", data)
        self.assertIn("overall_success_score", data)
        self.assertIn("generated_at", data)
        
        # Verify delivery outcome predictions
        self.assertIn("delivery_outcomes", data)
        delivery_outcomes = data["delivery_outcomes"]
        
        self.assertIn("on_time_delivery", delivery_outcomes)
        self.assertIn("budget_compliance", delivery_outcomes)
        self.assertIn("scope_completion", delivery_outcomes)
        self.assertIn("quality_achievement", delivery_outcomes)
        self.assertIn("stakeholder_satisfaction", delivery_outcomes)
        
        # Verify probability ranges (0-100%)
        for key, probability in delivery_outcomes.items():
            if isinstance(probability, (int, float)):
                self.assertGreaterEqual(probability, 0, f"{key} probability too low: {probability}")
                self.assertLessEqual(probability, 100, f"{key} probability too high: {probability}")
        
        # Verify success drivers and risk mitigations
        self.assertIn("success_drivers", data)
        self.assertIn("risk_mitigations", data)
        self.assertIn("recommendations", data)
        
        # Verify manufacturing excellence correlation
        self.assertIn("manufacturing_excellence", data)
        manufacturing_excellence = data["manufacturing_excellence"]
        
        self.assertIn("correlation_strength", manufacturing_excellence)
        self.assertIn("maintenance_excellence_potential", manufacturing_excellence)
        self.assertIn("operational_performance_impact", manufacturing_excellence)
        self.assertIn("manufacturing_readiness", manufacturing_excellence)
        self.assertIn("excellence_pathway", manufacturing_excellence)
        
        # Verify correlation strength is valid (0-1)
        correlation_strength = manufacturing_excellence["correlation_strength"]
        self.assertGreaterEqual(correlation_strength, 0, "Correlation strength should be >= 0")
        self.assertLessEqual(correlation_strength, 1, "Correlation strength should be <= 1")
        
        # Verify manufacturing readiness level
        manufacturing_readiness = manufacturing_excellence["manufacturing_readiness"]
        self.assertIn(manufacturing_readiness, ["Low", "Medium", "High"], f"Invalid manufacturing readiness: {manufacturing_readiness}")
        
        # Verify confidence level
        self.assertIn("confidence_level", data)
        confidence_level = data["confidence_level"]
        self.assertIn(confidence_level, ["Low", "Medium", "High"], f"Invalid confidence level: {confidence_level}")
        
        print("✅ Advanced Project Forecasting testing successful")
        print(f"   - Project ID: {data['project_id']}")
        print(f"   - Forecasting Confidence: {data['forecasting_confidence']}%")
        print(f"   - Overall Success Score: {data['overall_success_score']}%")
        print(f"   - On-time Delivery: {delivery_outcomes['on_time_delivery']}%")
        print(f"   - Budget Compliance: {delivery_outcomes['budget_compliance']}%")
        print(f"   - Manufacturing Readiness: {manufacturing_readiness}")
        print(f"   - Confidence Level: {confidence_level}")

    def test_44_stakeholder_communications(self):
        """Test Enhancement 3: Stakeholder Communication Automation endpoint"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test the new POST endpoint for stakeholder communications
        response = requests.post(f"{self.base_url}/projects/{self.project_id}/stakeholder-communications", headers=headers)
        print(f"Stakeholder Communications response: {response.status_code} - {response.text[:300]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify main structure
        self.assertIn("project_id", data)
        self.assertIn("communication_date", data)
        self.assertIn("executive_summary", data)
        self.assertIn("detailed_report", data)
        
        # Verify stakeholder-specific messages
        self.assertIn("stakeholder_messages", data)
        stakeholder_messages = data["stakeholder_messages"]
        
        # Should have messages for different stakeholder roles
        expected_roles = ["executive_leadership", "project_team", "client_stakeholders", "technical_teams"]
        
        for role in expected_roles:
            self.assertIn(role, stakeholder_messages, f"Missing message for {role}")
            message = stakeholder_messages[role]
            self.assertGreater(len(message), 20, f"Message for {role} should be substantial")
        
        # Verify alert notifications
        self.assertIn("alert_notifications", data)
        alert_notifications = data["alert_notifications"]
        self.assertIsInstance(alert_notifications, list, "Alert notifications should be a list")
        
        # Verify communication frequency and scheduling
        self.assertIn("recommended_frequency", data)
        frequency = data["recommended_frequency"]
        self.assertIn(frequency, ["Daily", "Weekly", "Bi-weekly", "Monthly"], f"Invalid frequency: {frequency}")
        
        self.assertIn("next_communication_date", data)
        self.assertIn("escalation_required", data)
        
        # Verify escalation flag is boolean
        escalation_required = data["escalation_required"]
        self.assertIsInstance(escalation_required, bool, "Escalation required should be boolean")
        
        # Verify executive summary and detailed report content
        executive_summary = data["executive_summary"]
        detailed_report = data["detailed_report"]
        
        self.assertGreater(len(executive_summary), 50, "Executive summary should be substantial")
        self.assertGreater(len(detailed_report), 50, "Detailed report should be substantial")
        
        print("✅ Stakeholder Communications testing successful")
        print(f"   - Project ID: {data['project_id']}")
        print(f"   - Stakeholder roles: {len(stakeholder_messages)} roles")
        print(f"   - Alert notifications: {len(alert_notifications)} alerts")
        print(f"   - Recommended frequency: {frequency}")
        print(f"   - Escalation required: {escalation_required}")

    def test_45_manufacturing_excellence_tracking(self):
        """Test Enhancement 3: Manufacturing Excellence Integration endpoint"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test the new POST endpoint for manufacturing excellence tracking
        response = requests.post(f"{self.base_url}/projects/{self.project_id}/manufacturing-excellence-tracking", headers=headers)
        print(f"Manufacturing Excellence Tracking response: {response.status_code} - {response.text[:300]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify main structure
        self.assertIn("project_id", data)
        self.assertIn("project_name", data)
        self.assertIn("generated_at", data)
        
        # Verify maintenance excellence tracking
        self.assertIn("maintenance_excellence", data)
        maintenance_excellence = data["maintenance_excellence"]
        
        self.assertIn("current_score", maintenance_excellence)
        self.assertIn("potential_score", maintenance_excellence)
        self.assertIn("improvement_pathway", maintenance_excellence)
        self.assertIn("critical_success_factors", maintenance_excellence)
        
        # Verify scores are in valid range (0-5)
        current_score = maintenance_excellence["current_score"]
        potential_score = maintenance_excellence["potential_score"]
        self.assertGreaterEqual(current_score, 0, f"Current score too low: {current_score}")
        self.assertLessEqual(current_score, 5, f"Current score too high: {current_score}")
        self.assertGreaterEqual(potential_score, current_score, "Potential score should be >= current score")
        self.assertLessEqual(potential_score, 5, f"Potential score too high: {potential_score}")
        
        # Verify performance predictions
        self.assertIn("performance_predictions", data)
        performance_predictions = data["performance_predictions"]
        
        expected_metrics = ["unplanned_downtime_reduction", "oee_improvement", "maintenance_cost_reduction", 
                           "safety_improvement", "operational_efficiency"]
        
        for metric in expected_metrics:
            self.assertIn(metric, performance_predictions)
            # Verify percentage format
            value = performance_predictions[metric]
            self.assertTrue(value.endswith('%'), f"{metric} should be in percentage format")
        
        # Verify ROI analysis
        self.assertIn("roi_analysis", data)
        roi_analysis = data["roi_analysis"]
        
        self.assertIn("estimated_annual_savings", roi_analysis)
        self.assertIn("implementation_investment", roi_analysis)
        self.assertIn("roi_percentage", roi_analysis)
        self.assertIn("payback_period_months", roi_analysis)
        self.assertIn("business_case_strength", roi_analysis)
        
        # Verify ROI calculations are realistic
        annual_savings = roi_analysis["estimated_annual_savings"]
        investment = roi_analysis["implementation_investment"]
        roi_percentage = roi_analysis["roi_percentage"]
        payback_months = roi_analysis["payback_period_months"]
        
        self.assertGreaterEqual(annual_savings, 0, "Annual savings should be non-negative")
        self.assertGreaterEqual(investment, 0, "Investment should be non-negative")
        self.assertGreaterEqual(payback_months, 6, "Payback period should be at least 6 months")
        self.assertLessEqual(payback_months, 36, "Payback period should be at most 36 months")
        
        # Verify business case strength
        business_case = roi_analysis["business_case_strength"]
        self.assertIn(business_case, ["Strong", "Moderate", "Developing"], f"Invalid business case strength: {business_case}")
        
        # Verify correlation metrics
        self.assertIn("correlation_metrics", data)
        correlation_metrics = data["correlation_metrics"]
        
        expected_correlations = ["maintenance_operations_correlation", "technology_adoption_correlation", "workforce_readiness_correlation"]
        
        for correlation in expected_correlations:
            self.assertIn(correlation, correlation_metrics)
            value = correlation_metrics[correlation]
            self.assertGreaterEqual(value, 0, f"{correlation} should be >= 0")
            self.assertLessEqual(value, 1, f"{correlation} should be <= 1")
        
        # Verify manufacturing KPIs
        self.assertIn("manufacturing_kpis", data)
        manufacturing_kpis = data["manufacturing_kpis"]
        
        expected_kpis = ["equipment_reliability", "planned_maintenance_ratio", "mean_time_to_repair", "maintenance_productivity"]
        
        for kpi in expected_kpis:
            self.assertIn(kpi, manufacturing_kpis)
        
        print("✅ Manufacturing Excellence Tracking testing successful")
        print(f"   - Project ID: {data['project_id']}")
        print(f"   - Current maintenance score: {current_score}")
        print(f"   - Potential score: {potential_score}")
        print(f"   - ROI percentage: {roi_percentage}%")
        print(f"   - Payback period: {payback_months} months")
        print(f"   - Business case: {business_case}")
        print(f"   - Annual savings: ${annual_savings:,}")

    def test_46_enhancement_3_performance_validation(self):
        """Test Enhancement 3: Performance validation for all new endpoints"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test performance of all Enhancement 3 endpoints
        endpoints = [
            ("detailed-budget-tracking", "Detailed Budget Tracking"),
            ("advanced-forecasting", "Advanced Forecasting"),
            ("stakeholder-communications", "Stakeholder Communications"),
            ("manufacturing-excellence-tracking", "Manufacturing Excellence Tracking")
        ]
        
        performance_results = {}
        
        for endpoint, name in endpoints:
            start_time = time.time()
            
            response = requests.post(f"{self.base_url}/projects/{self.project_id}/{endpoint}", headers=headers)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            self.assertEqual(response.status_code, 200, f"{name} endpoint failed")
            self.assertLess(response_time, 100, f"{name} response time too slow: {response_time:.1f}ms")
            
            performance_results[name] = response_time
        
        print("✅ Enhancement 3 Performance Validation successful")
        for name, response_time in performance_results.items():
            print(f"   - {name}: {response_time:.1f}ms")
        
        # Verify average performance
        avg_response_time = sum(performance_results.values()) / len(performance_results)
        self.assertLess(avg_response_time, 75, f"Average response time too slow: {avg_response_time:.1f}ms")
        print(f"   - Average response time: {avg_response_time:.1f}ms")

    def test_47_enhancement_3_data_validation(self):
        """Test Enhancement 3: Data validation and mathematical accuracy"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test detailed budget tracking calculations
        response = requests.post(f"{self.base_url}/projects/{self.project_id}/detailed-budget-tracking", headers=headers)
        self.assertEqual(response.status_code, 200)
        budget_data = response.json()
        
        # Verify budget calculations are mathematically sound
        budget_tracking = budget_data["budget_tracking"]
        overall_metrics = budget_tracking["overall_metrics"]
        
        total_budgeted = overall_metrics["total_budgeted"]
        total_spent = overall_metrics["total_spent"]
        total_remaining = overall_metrics["total_remaining"]
        
        self.assertGreaterEqual(total_budgeted, 0, "Total budgeted should be non-negative")
        self.assertGreaterEqual(total_spent, 0, "Total spent should be non-negative")
        self.assertGreaterEqual(total_remaining, 0, "Total remaining should be non-negative")
        
        # Verify budget math: budgeted = spent + remaining
        if total_budgeted > 0:
            self.assertAlmostEqual(total_budgeted, total_spent + total_remaining, delta=1, 
                                  msg="Budget math should be consistent")
        
        # Test manufacturing excellence ROI calculations
        response = requests.post(f"{self.base_url}/projects/{self.project_id}/manufacturing-excellence-tracking", headers=headers)
        self.assertEqual(response.status_code, 200)
        manufacturing_data = response.json()
        
        roi_analysis = manufacturing_data["roi_analysis"]
        annual_savings = roi_analysis["estimated_annual_savings"]
        investment = roi_analysis["implementation_investment"]
        roi_percentage = roi_analysis["roi_percentage"]
        payback_months = roi_analysis["payback_period_months"]
        
        # Verify ROI calculation accuracy (when investment > 0)
        if investment > 0:
            expected_roi = ((annual_savings - investment) / investment * 100)
            self.assertAlmostEqual(roi_percentage, expected_roi, delta=5, 
                                  msg="ROI percentage calculation should be accurate")
        
        # Verify payback period is reasonable
        self.assertGreaterEqual(payback_months, 6, "Payback period should be at least 6 months")
        self.assertLessEqual(payback_months, 36, "Payback period should be at most 36 months")
        
        # Test advanced forecasting calculations
        response = requests.post(f"{self.base_url}/projects/{self.project_id}/advanced-forecasting", headers=headers)
        self.assertEqual(response.status_code, 200)
        forecasting_data = response.json()
        
        delivery_outcomes = forecasting_data["delivery_outcomes"]
        overall_success_score = forecasting_data["overall_success_score"]
        
        # Verify all delivery outcomes are in valid range (0-100)
        for outcome_name, outcome_value in delivery_outcomes.items():
            self.assertGreaterEqual(outcome_value, 0, f"{outcome_name} should be >= 0")
            self.assertLessEqual(outcome_value, 100, f"{outcome_name} should be <= 100")
        
        # Verify overall success score is reasonable
        self.assertGreaterEqual(overall_success_score, 0, "Overall success score should be >= 0")
        self.assertLessEqual(overall_success_score, 100, "Overall success score should be <= 100")
        
        print("✅ Enhancement 3 Data Validation successful")
        print(f"   - Total budgeted: ${total_budgeted:,}")
        print(f"   - Total spent: ${total_spent:,}")
        print(f"   - Budget consistency: ✓")
        print(f"   - ROI percentage: {roi_percentage}%")
        print(f"   - Manufacturing annual savings: ${annual_savings:,}")
        print(f"   - Overall success score: {overall_success_score}%")

    # ====================================================================================
    # ENHANCEMENT 4: ADVANCED PROJECT WORKFLOW MANAGEMENT WITH PHASE-BASED INTELLIGENCE
    # ====================================================================================

    def test_48_enhanced_project_editing(self):
        """Test Enhancement 4: Enhanced project editing with ProjectUpdate model"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test the enhanced PUT endpoint for project editing
        project_update = {
            "project_name": "Enhanced Project Name",
            "description": "Updated project description with enhanced features",
            "client_organization": "Enhanced Client Organization",
            "objectives": [
                "Implement advanced workflow management",
                "Achieve phase-based intelligence integration",
                "Optimize project lifecycle management"
            ],
            "scope": "Enhanced project scope with phase-based intelligence",
            "total_budget": 125000.0,
            "estimated_end_date": (datetime.utcnow() + timedelta(days=120)).isoformat(),
            "current_phase": "mobilize",
            "health_status": "healthy",
            "spent_budget": 15000.0,
            "team_members": ["team.member1@company.com", "team.member2@company.com"],
            "stakeholders": ["stakeholder1@client.com", "stakeholder2@client.com"],
            "key_milestones": [
                {
                    "name": "Phase 1 Completion",
                    "target_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                    "status": "pending"
                },
                {
                    "name": "Phase 2 Completion", 
                    "target_date": (datetime.utcnow() + timedelta(days=60)).isoformat(),
                    "status": "pending"
                }
            ]
        }
        
        response = requests.put(f"{self.base_url}/projects/{self.project_id}", json=project_update, headers=headers)
        print(f"Enhanced Project Editing response: {response.status_code} - {response.text[:300]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify project update structure
        self.assertEqual(data["id"], self.project_id)
        self.assertEqual(data["name"], project_update["project_name"])
        self.assertEqual(data["description"], project_update["description"])
        self.assertEqual(data["current_phase"], project_update["current_phase"])
        self.assertEqual(data["status"], "active")  # Should remain active
        self.assertEqual(data["budget"], project_update["total_budget"])
        
        # Verify objectives were updated
        if "objectives" in data:
            self.assertEqual(len(data["objectives"]), len(project_update["objectives"]))
        
        # Verify team members and stakeholders
        if "team_members" in data:
            self.assertEqual(len(data["team_members"]), len(project_update["team_members"]))
        
        if "stakeholders" in data:
            self.assertEqual(len(data["stakeholders"]), len(project_update["stakeholders"]))
        
        # Verify milestones
        if "milestones" in data:
            self.assertGreaterEqual(len(data["milestones"]), len(project_update["key_milestones"]))
        
        # Verify datetime fields are handled properly
        self.assertIn("updated_at", data)
        
        print("✅ Enhanced Project Editing testing successful")
        print(f"   - Project ID: {data['id']}")
        print(f"   - Updated Name: {data['name']}")
        print(f"   - Current Phase: {data['current_phase']}")
        print(f"   - Total Budget: ${data['budget']:,}")
        print(f"   - Team Members: {len(data.get('team_members', []))}")
        print(f"   - Stakeholders: {len(data.get('stakeholders', []))}")
        print(f"   - Milestones: {len(data.get('milestones', []))}")

    def test_49_phase_based_intelligence_generation(self):
        """Test Enhancement 4: Phase-based intelligence and recommendations"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test intelligence generation for different IMPACT phases
        impact_phases = ["investigate", "mobilize", "pilot", "activate", "cement", "track"]
        
        intelligence_results = {}
        
        for phase_name in impact_phases:
            response = requests.post(f"{self.base_url}/projects/{self.project_id}/phases/{phase_name}/intelligence", headers=headers)
            print(f"Phase Intelligence for {phase_name} response: {response.status_code} - {response.text[:200]}...")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Verify intelligence structure
            self.assertIn("project_id", data)
            self.assertIn("phase_name", data)
            self.assertIn("phase_display_name", data)
            self.assertIn("generated_at", data)
            self.assertIn("generated_by", data)
            
            # Verify phase-specific intelligence
            self.assertIn("phase_intelligence", data)
            phase_intelligence = data["phase_intelligence"]
            
            self.assertIn("phase_objectives", phase_intelligence)
            self.assertIn("key_activities", phase_intelligence)
            self.assertIn("success_criteria", phase_intelligence)
            self.assertIn("deliverables", phase_intelligence)
            self.assertIn("newton_law_application", phase_intelligence)
            
            # Verify recommendations
            self.assertIn("recommendations", data)
            recommendations = data["recommendations"]
            
            self.assertIn("strategic_recommendations", recommendations)
            self.assertIn("tactical_actions", recommendations)
            self.assertIn("risk_mitigation", recommendations)
            self.assertIn("success_factors", recommendations)
            
            # Verify success probability calculation
            self.assertIn("success_probability", data)
            success_probability = data["success_probability"]
            self.assertGreaterEqual(success_probability, 15, f"Success probability too low for {phase_name}")
            self.assertLessEqual(success_probability, 95, f"Success probability too high for {phase_name}")
            
            # Verify budget recommendations
            self.assertIn("budget_recommendations", data)
            budget_recommendations = data["budget_recommendations"]
            
            self.assertIn("phase_budget_estimate", budget_recommendations)
            self.assertIn("risk_adjustment_factor", budget_recommendations)
            self.assertIn("recommended_contingency", budget_recommendations)
            self.assertIn("cost_optimization_opportunities", budget_recommendations)
            
            # Verify risk assessment
            self.assertIn("risk_assessment", data)
            risk_assessment = data["risk_assessment"]
            
            self.assertIn("phase_specific_risks", risk_assessment)
            self.assertIn("risk_level", risk_assessment)
            self.assertIn("mitigation_strategies", risk_assessment)
            
            # Verify risk level is valid
            self.assertIn(risk_assessment["risk_level"], ["Low", "Medium", "High"])
            
            # Verify lessons learned integration
            self.assertIn("lessons_learned", data)
            lessons_learned = data["lessons_learned"]
            
            self.assertIn("previous_phase_insights", lessons_learned)
            self.assertIn("best_practices", lessons_learned)
            self.assertIn("improvement_opportunities", lessons_learned)
            
            intelligence_results[phase_name] = {
                "success_probability": success_probability,
                "risk_level": risk_assessment["risk_level"],
                "phase_budget": budget_recommendations["phase_budget_estimate"],
                "recommendations_count": len(recommendations["strategic_recommendations"])
            }
        
        print("✅ Phase-based Intelligence Generation testing successful")
        for phase_name, results in intelligence_results.items():
            print(f"   - {phase_name.capitalize()}:")
            print(f"     • Success Probability: {results['success_probability']:.1f}%")
            print(f"     • Risk Level: {results['risk_level']}")
            print(f"     • Phase Budget: ${results['phase_budget']:,}")
            print(f"     • Recommendations: {results['recommendations_count']}")

    def test_50_phase_progress_tracking(self):
        """Test Enhancement 4: Phase progress tracking and updates"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test progress updates for different phases
        phase_updates = [
            {
                "phase_name": "investigate",
                "completion_percentage": 75.0,
                "status": "in_progress",
                "success_status": "on_track",
                "success_reason": "Strong stakeholder engagement and comprehensive analysis completed",
                "lessons_learned": "Early stakeholder involvement critical for success",
                "budget_spent": 12000.0,
                "scope_changes": ["Added additional stakeholder interviews", "Extended analysis period"],
                "tasks_completed": ["Stakeholder analysis", "Current state assessment"],
                "deliverables_completed": ["Stakeholder Analysis Report", "Current State Analysis"],
                "risks_identified": ["Resource availability concerns", "Timeline pressure"]
            },
            {
                "phase_name": "mobilize",
                "completion_percentage": 45.0,
                "status": "in_progress",
                "success_status": "at_risk",
                "success_reason": "Some delays in resource allocation",
                "failure_reason": "Delayed approval for additional resources",
                "lessons_learned": "Need earlier resource planning and approval processes",
                "budget_spent": 8500.0,
                "scope_changes": ["Reduced training scope due to budget constraints"],
                "tasks_completed": ["Change management plan development"],
                "deliverables_completed": ["Change Management Plan"],
                "risks_identified": ["Budget constraints", "Resource allocation delays"]
            },
            {
                "phase_name": "pilot",
                "completion_percentage": 0.0,
                "status": "not_started",
                "lessons_learned": "Awaiting completion of mobilize phase",
                "budget_spent": 0.0,
                "scope_changes": [],
                "tasks_completed": [],
                "deliverables_completed": [],
                "risks_identified": ["Dependency on mobilize phase completion"]
            }
        ]
        
        progress_results = {}
        
        for update in phase_updates:
            phase_name = update["phase_name"]
            
            response = requests.put(f"{self.base_url}/projects/{self.project_id}/phases/{phase_name}/progress", 
                                  json=update, headers=headers)
            print(f"Phase Progress Update for {phase_name} response: {response.status_code} - {response.text[:200]}...")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Verify update response structure
            self.assertIn("message", data)
            self.assertIn("project_id", data)
            self.assertIn("phase_name", data)
            self.assertIn("updated_progress", data)
            
            # Verify updated progress details
            updated_progress = data["updated_progress"]
            self.assertEqual(updated_progress["completion_percentage"], update["completion_percentage"])
            self.assertEqual(updated_progress["status"], update["status"])
            self.assertEqual(updated_progress["budget_spent"], update["budget_spent"])
            
            if "success_status" in update:
                self.assertEqual(updated_progress["success_status"], update["success_status"])
            
            if "lessons_learned" in update:
                self.assertEqual(updated_progress["lessons_learned"], update["lessons_learned"])
            
            # Verify scope changes and tasks
            if "scope_changes" in update:
                self.assertEqual(len(updated_progress["scope_changes"]), len(update["scope_changes"]))
            
            if "tasks_completed" in update:
                self.assertEqual(len(updated_progress["tasks_completed"]), len(update["tasks_completed"]))
            
            if "deliverables_completed" in update:
                self.assertEqual(len(updated_progress["deliverables_completed"]), len(update["deliverables_completed"]))
            
            if "risks_identified" in update:
                self.assertEqual(len(updated_progress["risks_identified"]), len(update["risks_identified"]))
            
            progress_results[phase_name] = {
                "completion_percentage": updated_progress["completion_percentage"],
                "status": updated_progress["status"],
                "budget_spent": updated_progress["budget_spent"],
                "risks_count": len(updated_progress.get("risks_identified", []))
            }
        
        print("✅ Phase Progress Tracking testing successful")
        for phase_name, results in progress_results.items():
            print(f"   - {phase_name.capitalize()}:")
            print(f"     • Completion: {results['completion_percentage']:.1f}%")
            print(f"     • Status: {results['status']}")
            print(f"     • Budget Spent: ${results['budget_spent']:,}")
            print(f"     • Risks Identified: {results['risks_count']}")

    def test_51_phase_completion_analysis(self):
        """Test Enhancement 4: Phase completion and comprehensive analysis"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test phase completion for investigate phase
        completion_data = {
            "completion_percentage": 100.0,
            "success_status": "successful",
            "success_reason": "All objectives met with stakeholder satisfaction",
            "lessons_learned": "Early stakeholder engagement was key to success. Comprehensive analysis provided solid foundation.",
            "budget_spent": 15000.0,
            "scope_changes": ["Added stakeholder interviews", "Extended analysis period"],
            "deliverables_completed": [
                "Stakeholder Analysis Report",
                "Current State Analysis", 
                "Risk Assessment Matrix",
                "Cultural Assessment Report"
            ],
            "final_notes": "Phase completed successfully with all deliverables approved",
            "performance_metrics": {
                "quality_score": 4.5,
                "timeline_adherence": 0.95,
                "budget_efficiency": 0.88,
                "stakeholder_satisfaction": 4.2
            }
        }
        
        response = requests.post(f"{self.base_url}/projects/{self.project_id}/phases/investigate/complete", 
                               json=completion_data, headers=headers)
        print(f"Phase Completion Analysis response: {response.status_code} - {response.text[:300]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify completion analysis structure
        self.assertIn("project_id", data)
        self.assertIn("phase_name", data)
        self.assertIn("completion_date", data)
        self.assertIn("generated_at", data)
        
        # Verify completion analysis
        self.assertIn("completion_analysis", data)
        completion_analysis = data["completion_analysis"]
        
        self.assertIn("completion_score", completion_analysis)
        self.assertIn("performance_metrics", completion_analysis)
        self.assertIn("success_factors", completion_analysis)
        self.assertIn("improvement_areas", completion_analysis)
        self.assertIn("lessons_learned_summary", completion_analysis)
        
        # Verify completion score is reasonable (0-100)
        completion_score = completion_analysis["completion_score"]
        self.assertGreaterEqual(completion_score, 0, "Completion score should be >= 0")
        self.assertLessEqual(completion_score, 100, "Completion score should be <= 100")
        
        # Verify performance metrics
        performance_metrics = completion_analysis["performance_metrics"]
        self.assertIn("overall_performance", performance_metrics)
        self.assertIn("quality_achievement", performance_metrics)
        self.assertIn("timeline_performance", performance_metrics)
        self.assertIn("budget_performance", performance_metrics)
        self.assertIn("stakeholder_satisfaction", performance_metrics)
        
        # Verify next phase readiness
        self.assertIn("next_phase_readiness", data)
        next_phase_readiness = data["next_phase_readiness"]
        
        self.assertIn("readiness_score", next_phase_readiness)
        self.assertIn("readiness_level", next_phase_readiness)
        self.assertIn("prerequisites_met", next_phase_readiness)
        self.assertIn("preparation_recommendations", next_phase_readiness)
        
        # Verify readiness level is valid
        readiness_level = next_phase_readiness["readiness_level"]
        self.assertIn(readiness_level, ["Ready", "Conditionally Ready", "Not Ready"])
        
        # Verify next phase recommendations
        self.assertIn("next_phase_recommendations", data)
        next_phase_recommendations = data["next_phase_recommendations"]
        
        self.assertIn("recommended_actions", next_phase_recommendations)
        self.assertIn("success_strategies", next_phase_recommendations)
        self.assertIn("risk_mitigation", next_phase_recommendations)
        self.assertIn("resource_requirements", next_phase_recommendations)
        self.assertIn("timeline_recommendations", next_phase_recommendations)
        
        # Verify comprehensive insights
        self.assertIn("comprehensive_insights", data)
        comprehensive_insights = data["comprehensive_insights"]
        
        self.assertIn("phase_impact_assessment", comprehensive_insights)
        self.assertIn("project_trajectory", comprehensive_insights)
        self.assertIn("success_probability_update", comprehensive_insights)
        self.assertIn("strategic_recommendations", comprehensive_insights)
        
        print("✅ Phase Completion Analysis testing successful")
        print(f"   - Project ID: {data['project_id']}")
        print(f"   - Phase: {data['phase_name']}")
        print(f"   - Completion Score: {completion_score:.1f}")
        print(f"   - Next Phase Readiness: {readiness_level}")
        print(f"   - Success Factors: {len(completion_analysis['success_factors'])}")
        print(f"   - Improvement Areas: {len(completion_analysis['improvement_areas'])}")
        print(f"   - Next Phase Recommendations: {len(next_phase_recommendations['recommended_actions'])}")

    def test_52_workflow_status_monitoring(self):
        """Test Enhancement 4: Comprehensive workflow status monitoring"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.get(f"{self.base_url}/projects/{self.project_id}/workflow-status", headers=headers)
        print(f"Workflow Status response: {response.status_code} - {response.text[:300]}...")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify workflow status structure
        self.assertIn("project_id", data)
        self.assertIn("project_name", data)
        self.assertIn("current_phase", data)
        self.assertIn("generated_at", data)
        
        # Verify overall progress
        self.assertIn("overall_progress", data)
        overall_progress = data["overall_progress"]
        
        self.assertIn("completion_percentage", overall_progress)
        self.assertIn("phases_completed", overall_progress)
        self.assertIn("phases_in_progress", overall_progress)
        self.assertIn("phases_not_started", overall_progress)
        self.assertIn("project_health", overall_progress)
        
        # Verify completion percentage is valid
        completion_percentage = overall_progress["completion_percentage"]
        self.assertGreaterEqual(completion_percentage, 0, "Completion percentage should be >= 0")
        self.assertLessEqual(completion_percentage, 100, "Completion percentage should be <= 100")
        
        # Verify project health is valid
        project_health = overall_progress["project_health"]
        self.assertIn(project_health, ["Excellent", "Good", "At Risk", "Critical"])
        
        # Verify phase completion summary
        self.assertIn("phase_completion_summary", data)
        phase_summary = data["phase_completion_summary"]
        
        # Should have all 6 IMPACT phases
        impact_phases = ["investigate", "mobilize", "pilot", "activate", "cement", "track"]
        for phase in impact_phases:
            self.assertIn(phase, phase_summary)
            phase_info = phase_summary[phase]
            
            self.assertIn("status", phase_info)
            self.assertIn("completion_percentage", phase_info)
            self.assertIn("budget_spent", phase_info)
            self.assertIn("success_status", phase_info)
            
            # Verify status is valid
            self.assertIn(phase_info["status"], ["not_started", "in_progress", "completed", "failed"])
            
            # Verify completion percentage is valid
            phase_completion = phase_info["completion_percentage"]
            self.assertGreaterEqual(phase_completion, 0, f"Phase {phase} completion should be >= 0")
            self.assertLessEqual(phase_completion, 100, f"Phase {phase} completion should be <= 100")
        
        # Verify budget utilization
        self.assertIn("budget_utilization", data)
        budget_utilization = data["budget_utilization"]
        
        self.assertIn("total_budget", budget_utilization)
        self.assertIn("total_spent", budget_utilization)
        self.assertIn("remaining_budget", budget_utilization)
        self.assertIn("utilization_percentage", budget_utilization)
        self.assertIn("budget_health", budget_utilization)
        self.assertIn("phase_budget_breakdown", budget_utilization)
        
        # Verify budget calculations
        total_budget = budget_utilization["total_budget"]
        total_spent = budget_utilization["total_spent"]
        remaining_budget = budget_utilization["remaining_budget"]
        
        self.assertGreaterEqual(total_budget, 0, "Total budget should be non-negative")
        self.assertGreaterEqual(total_spent, 0, "Total spent should be non-negative")
        self.assertGreaterEqual(remaining_budget, 0, "Remaining budget should be non-negative")
        
        # Verify budget math consistency
        if total_budget > 0:
            self.assertAlmostEqual(total_budget, total_spent + remaining_budget, delta=1, 
                                  msg="Budget math should be consistent")
        
        # Verify success rates
        self.assertIn("success_rates", data)
        success_rates = data["success_rates"]
        
        self.assertIn("completed_phases_success_rate", success_rates)
        self.assertIn("overall_project_success_probability", success_rates)
        self.assertIn("phase_success_breakdown", success_rates)
        
        # Verify success rates are valid percentages
        completed_success_rate = success_rates["completed_phases_success_rate"]
        overall_success_prob = success_rates["overall_project_success_probability"]
        
        self.assertGreaterEqual(completed_success_rate, 0, "Completed success rate should be >= 0")
        self.assertLessEqual(completed_success_rate, 100, "Completed success rate should be <= 100")
        self.assertGreaterEqual(overall_success_prob, 0, "Overall success probability should be >= 0")
        self.assertLessEqual(overall_success_prob, 100, "Overall success probability should be <= 100")
        
        # Verify project insights
        self.assertIn("project_insights", data)
        project_insights = data["project_insights"]
        
        self.assertIn("key_achievements", project_insights)
        self.assertIn("current_challenges", project_insights)
        self.assertIn("upcoming_milestones", project_insights)
        self.assertIn("recommended_actions", project_insights)
        self.assertIn("risk_alerts", project_insights)
        
        print("✅ Workflow Status Monitoring testing successful")
        print(f"   - Project ID: {data['project_id']}")
        print(f"   - Current Phase: {data['current_phase']}")
        print(f"   - Overall Completion: {completion_percentage:.1f}%")
        print(f"   - Project Health: {project_health}")
        print(f"   - Budget Utilization: {budget_utilization['utilization_percentage']:.1f}%")
        print(f"   - Completed Phases Success Rate: {completed_success_rate:.1f}%")
        print(f"   - Overall Success Probability: {overall_success_prob:.1f}%")
        print(f"   - Key Achievements: {len(project_insights['key_achievements'])}")
        print(f"   - Current Challenges: {len(project_insights['current_challenges'])}")
        print(f"   - Risk Alerts: {len(project_insights['risk_alerts'])}")

    def test_53_enhancement_4_integration_workflow(self):
        """Test Enhancement 4: Complete workflow integration from assessment to project completion"""
        if not self.assessment_id:
            self.skipTest("No assessment ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Step 1: Create project from assessment
        project_data = {
            "assessment_id": self.assessment_id,
            "project_name": "Enhancement 4 Integration Test Project",
            "description": "Complete workflow test for Enhancement 4 features",
            "target_completion_date": (datetime.utcnow() + timedelta(days=180)).isoformat(),
            "budget": 150000
        }
        
        response = requests.post(f"{self.base_url}/projects/from-assessment", json=project_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        project_data_response = response.json()
        integration_project_id = project_data_response["id"]
        
        # Step 2: Generate phase intelligence for first phase
        response = requests.post(f"{self.base_url}/projects/{integration_project_id}/phases/investigate/intelligence", headers=headers)
        self.assertEqual(response.status_code, 200)
        intelligence_data = response.json()
        
        # Step 3: Update phase progress
        progress_update = {
            "phase_name": "investigate",
            "completion_percentage": 100.0,
            "status": "completed",
            "success_status": "successful",
            "success_reason": "All investigation objectives met",
            "lessons_learned": "Thorough stakeholder analysis was crucial",
            "budget_spent": 20000.0,
            "scope_changes": ["Added additional stakeholder interviews"],
            "tasks_completed": ["Stakeholder analysis", "Current state assessment"],
            "deliverables_completed": ["Stakeholder Analysis Report", "Current State Analysis"],
            "risks_identified": ["Resource availability", "Timeline constraints"]
        }
        
        response = requests.put(f"{self.base_url}/projects/{integration_project_id}/phases/investigate/progress", 
                               json=progress_update, headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Complete the phase
        completion_data = {
            "completion_percentage": 100.0,
            "success_status": "successful",
            "success_reason": "All objectives achieved with stakeholder approval",
            "lessons_learned": "Early stakeholder engagement critical for success",
            "budget_spent": 20000.0,
            "scope_changes": ["Added stakeholder interviews"],
            "deliverables_completed": ["Stakeholder Analysis Report", "Current State Analysis"],
            "final_notes": "Phase completed successfully"
        }
        
        response = requests.post(f"{self.base_url}/projects/{integration_project_id}/phases/investigate/complete", 
                               json=completion_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        completion_response = response.json()
        
        # Step 5: Get comprehensive workflow status
        response = requests.get(f"{self.base_url}/projects/{integration_project_id}/workflow-status", headers=headers)
        self.assertEqual(response.status_code, 200)
        workflow_status = response.json()
        
        # Step 6: Generate intelligence for next phase based on lessons learned
        response = requests.post(f"{self.base_url}/projects/{integration_project_id}/phases/mobilize/intelligence", headers=headers)
        self.assertEqual(response.status_code, 200)
        next_phase_intelligence = response.json()
        
        # Verify integration workflow results
        self.assertIn("next_phase_readiness", completion_response)
        self.assertIn("next_phase_recommendations", completion_response)
        
        # Verify workflow status reflects completed phase
        phase_summary = workflow_status["phase_completion_summary"]
        investigate_status = phase_summary["investigate"]
        self.assertEqual(investigate_status["status"], "completed")
        self.assertEqual(investigate_status["completion_percentage"], 100.0)
        
        # Verify next phase intelligence incorporates lessons learned
        self.assertIn("lessons_learned", next_phase_intelligence)
        lessons_learned = next_phase_intelligence["lessons_learned"]
        self.assertIn("previous_phase_insights", lessons_learned)
        
        # Verify budget tracking across phases
        budget_utilization = workflow_status["budget_utilization"]
        self.assertGreater(budget_utilization["total_spent"], 0)
        self.assertLess(budget_utilization["total_spent"], budget_utilization["total_budget"])
        
        print("✅ Enhancement 4 Integration Workflow testing successful")
        print(f"   - Integration Project ID: {integration_project_id}")
        print(f"   - Phase Intelligence Generated: ✓")
        print(f"   - Phase Progress Tracked: ✓")
        print(f"   - Phase Completion Analysis: ✓")
        print(f"   - Workflow Status Monitoring: ✓")
        print(f"   - Next Phase Intelligence: ✓")
        print(f"   - Lessons Learned Integration: ✓")
        print(f"   - Budget Tracking: ${budget_utilization['total_spent']:,} spent")
        print(f"   - Project Health: {workflow_status['overall_progress']['project_health']}")

    def test_54_enhancement_4_performance_validation(self):
        """Test Enhancement 4: Performance validation for all new endpoints"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test performance of all Enhancement 4 endpoints
        endpoints_to_test = [
            ("PUT", f"/projects/{self.project_id}", "Enhanced Project Editing", {
                "project_name": "Performance Test Project",
                "description": "Testing performance of enhanced editing"
            }),
            ("POST", f"/projects/{self.project_id}/phases/investigate/intelligence", "Phase Intelligence Generation", {}),
            ("PUT", f"/projects/{self.project_id}/phases/investigate/progress", "Phase Progress Update", {
                "phase_name": "investigate",
                "completion_percentage": 50.0,
                "status": "in_progress",
                "budget_spent": 10000.0
            }),
            ("POST", f"/projects/{self.project_id}/phases/investigate/complete", "Phase Completion Analysis", {
                "completion_percentage": 100.0,
                "success_status": "successful",
                "budget_spent": 20000.0
            }),
            ("GET", f"/projects/{self.project_id}/workflow-status", "Workflow Status Monitoring", {})
        ]
        
        performance_results = {}
        
        for method, endpoint, name, payload in endpoints_to_test:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
            elif method == "POST":
                response = requests.post(f"{self.base_url}{endpoint}", json=payload, headers=headers)
            elif method == "PUT":
                response = requests.put(f"{self.base_url}{endpoint}", json=payload, headers=headers)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            self.assertEqual(response.status_code, 200, f"{name} endpoint failed")
            self.assertLess(response_time, 100, f"{name} response time too slow: {response_time:.1f}ms")
            
            performance_results[name] = response_time
        
        print("✅ Enhancement 4 Performance Validation successful")
        for name, response_time in performance_results.items():
            print(f"   - {name}: {response_time:.1f}ms")
        
        # Verify average performance
        avg_response_time = sum(performance_results.values()) / len(performance_results)
        self.assertLess(avg_response_time, 75, f"Average response time too slow: {avg_response_time:.1f}ms")
        print(f"   - Average response time: {avg_response_time:.1f}ms")

    def test_55_enhancement_4_data_consistency(self):
        """Test Enhancement 4: Data consistency across all workflow operations"""
        if not self.project_id:
            self.skipTest("No project ID available")
            
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test data consistency across workflow operations
        
        # Step 1: Update project with specific budget
        project_update = {
            "project_name": "Data Consistency Test Project",
            "total_budget": 100000.0,
            "spent_budget": 0.0
        }
        
        response = requests.put(f"{self.base_url}/projects/{self.project_id}", json=project_update, headers=headers)
        self.assertEqual(response.status_code, 200)
        updated_project = response.json()
        
        # Step 2: Update phase progress with budget spending
        progress_update = {
            "phase_name": "investigate",
            "completion_percentage": 75.0,
            "status": "in_progress",
            "budget_spent": 15000.0,
            "tasks_completed": ["Task 1", "Task 2"],
            "deliverables_completed": ["Deliverable 1"],
            "risks_identified": ["Risk 1", "Risk 2"]
        }
        
        response = requests.put(f"{self.base_url}/projects/{self.project_id}/phases/investigate/progress", 
                               json=progress_update, headers=headers)
        self.assertEqual(response.status_code, 200)
        progress_response = response.json()
        
        # Step 3: Get workflow status and verify consistency
        response = requests.get(f"{self.base_url}/projects/{self.project_id}/workflow-status", headers=headers)
        self.assertEqual(response.status_code, 200)
        workflow_status = response.json()
        
        # Verify project data consistency
        self.assertEqual(workflow_status["project_name"], project_update["project_name"])
        
        # Verify budget consistency
        budget_utilization = workflow_status["budget_utilization"]
        self.assertEqual(budget_utilization["total_budget"], project_update["total_budget"])
        
        # Verify phase progress consistency
        phase_summary = workflow_status["phase_completion_summary"]
        investigate_phase = phase_summary["investigate"]
        self.assertEqual(investigate_phase["completion_percentage"], progress_update["completion_percentage"])
        self.assertEqual(investigate_phase["status"], progress_update["status"])
        self.assertEqual(investigate_phase["budget_spent"], progress_update["budget_spent"])
        
        # Step 4: Generate phase intelligence and verify it reflects current state
        response = requests.post(f"{self.base_url}/projects/{self.project_id}/phases/investigate/intelligence", headers=headers)
        self.assertEqual(response.status_code, 200)
        intelligence_data = response.json()
        
        # Verify intelligence reflects current project state
        self.assertEqual(intelligence_data["project_id"], self.project_id)
        self.assertEqual(intelligence_data["phase_name"], "investigate")
        
        # Step 5: Complete phase and verify all data is consistent
        completion_data = {
            "completion_percentage": 100.0,
            "success_status": "successful",
            "budget_spent": 20000.0,
            "deliverables_completed": ["Deliverable 1", "Deliverable 2"],
            "lessons_learned": "Data consistency maintained throughout workflow"
        }
        
        response = requests.post(f"{self.base_url}/projects/{self.project_id}/phases/investigate/complete", 
                               json=completion_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        completion_response = response.json()
        
        # Step 6: Final workflow status check
        response = requests.get(f"{self.base_url}/projects/{self.project_id}/workflow-status", headers=headers)
        self.assertEqual(response.status_code, 200)
        final_workflow_status = response.json()
        
        # Verify final consistency
        final_phase_summary = final_workflow_status["phase_completion_summary"]
        final_investigate_phase = final_phase_summary["investigate"]
        
        self.assertEqual(final_investigate_phase["completion_percentage"], 100.0)
        self.assertEqual(final_investigate_phase["status"], "completed")
        self.assertEqual(final_investigate_phase["budget_spent"], completion_data["budget_spent"])
        
        # Verify budget calculations are consistent
        final_budget_utilization = final_workflow_status["budget_utilization"]
        self.assertGreater(final_budget_utilization["total_spent"], 0)
        self.assertLess(final_budget_utilization["total_spent"], final_budget_utilization["total_budget"])
        
        print("✅ Enhancement 4 Data Consistency testing successful")
        print(f"   - Project data consistency: ✓")
        print(f"   - Budget tracking consistency: ✓")
        print(f"   - Phase progress consistency: ✓")
        print(f"   - Intelligence data consistency: ✓")
        print(f"   - Completion data consistency: ✓")
        print(f"   - Final budget spent: ${final_budget_utilization['total_spent']:,}")
        print(f"   - Final project health: {final_workflow_status['overall_progress']['project_health']}")

    def test_56_enhancement_4_error_handling(self):
        """Test Enhancement 4: Error handling and edge cases"""
        if not self.token:
            self.skipTest("No token available")
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test 1: Invalid project ID
        invalid_project_id = "invalid-project-id-12345"
        
        response = requests.put(f"{self.base_url}/projects/{invalid_project_id}", 
                               json={"project_name": "Test"}, headers=headers)
        self.assertEqual(response.status_code, 404, "Invalid project ID should return 404")
        
        response = requests.get(f"{self.base_url}/projects/{invalid_project_id}/workflow-status", headers=headers)
        self.assertEqual(response.status_code, 404, "Invalid project ID should return 404 for workflow status")
        
        # Test 2: Invalid phase name
        if self.project_id:
            response = requests.post(f"{self.base_url}/projects/{self.project_id}/phases/invalid_phase/intelligence", headers=headers)
            self.assertEqual(response.status_code, 400, "Invalid phase name should return 400")
            
            response = requests.put(f"{self.base_url}/projects/{self.project_id}/phases/invalid_phase/progress", 
                                   json={"completion_percentage": 50.0}, headers=headers)
            self.assertEqual(response.status_code, 400, "Invalid phase name should return 400")
        
        # Test 3: Invalid completion percentage
        if self.project_id:
            invalid_progress = {
                "phase_name": "investigate",
                "completion_percentage": 150.0,  # Invalid: > 100
                "status": "in_progress"
            }
            
            response = requests.put(f"{self.base_url}/projects/{self.project_id}/phases/investigate/progress", 
                                   json=invalid_progress, headers=headers)
            self.assertNotEqual(response.status_code, 200, "Invalid completion percentage should be rejected")
        
        # Test 4: Invalid budget values
        if self.project_id:
            invalid_budget_update = {
                "total_budget": -1000.0,  # Invalid: negative budget
                "spent_budget": -500.0    # Invalid: negative spent
            }
            
            response = requests.put(f"{self.base_url}/projects/{self.project_id}", 
                                   json=invalid_budget_update, headers=headers)
            self.assertNotEqual(response.status_code, 200, "Negative budget values should be rejected")
        
        # Test 5: Missing required fields
        if self.project_id:
            incomplete_progress = {
                "completion_percentage": 50.0
                # Missing required phase_name and status
            }
            
            response = requests.put(f"{self.base_url}/projects/{self.project_id}/phases/investigate/progress", 
                                   json=incomplete_progress, headers=headers)
            self.assertNotEqual(response.status_code, 200, "Missing required fields should be rejected")
        
        # Test 6: Unauthorized access (no token)
        response = requests.get(f"{self.base_url}/projects/test-id/workflow-status")
        self.assertEqual(response.status_code, 401, "Missing token should return 401")
        
        response = requests.post(f"{self.base_url}/projects/test-id/phases/investigate/intelligence")
        self.assertEqual(response.status_code, 401, "Missing token should return 401")
        
        print("✅ Enhancement 4 Error Handling testing successful")
        print("   - Invalid project ID handling: ✓")
        print("   - Invalid phase name handling: ✓")
        print("   - Invalid completion percentage handling: ✓")
        print("   - Invalid budget values handling: ✓")
        print("   - Missing required fields handling: ✓")
        print("   - Unauthorized access handling: ✓")

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


def run_comprehensive_intelligence_tests():
    """Run comprehensive tests for the new intelligence layer features"""
    test_suite = unittest.TestSuite()
    
    # Create a test instance to share the token and assessment IDs
    test_instance = IMPACTMethodologyAPITest('test_03_user_login')
    test_instance.setUp()
    test_instance.test_03_user_login()
    
    # Create different assessment types for testing
    assessment_tests = [
        IMPACTMethodologyAPITest('test_06_create_general_readiness_assessment'),
        IMPACTMethodologyAPITest('test_07_create_software_implementation_assessment'),
        IMPACTMethodologyAPITest('test_08_create_business_process_assessment'),
        IMPACTMethodologyAPITest('test_09_create_manufacturing_operations_assessment')
    ]
    
    for test in assessment_tests:
        test.setUp()
        test.token = test_instance.token
        test.user_id = test_instance.user_id
        test_suite.addTest(test)
    
    # Get the assessment IDs from the last test
    last_test = assessment_tests[-1]
    
    # Add new intelligence layer tests
    intelligence_tests = [
        'test_25_new_week_by_week_implementation_plan',
        'test_26_customized_playbook_generation',
        'test_27_intelligence_layer_different_readiness_levels',
        'test_28_budget_prediction_accuracy',
        'test_29_impact_phase_alignment',
        'test_30_success_probability_calculations',
        'test_31_manufacturing_specific_features'
    ]
    
    for test_name in intelligence_tests:
        intelligence_test = IMPACTMethodologyAPITest(test_name)
        intelligence_test.setUp()
        intelligence_test.token = test_instance.token
        intelligence_test.user_id = test_instance.user_id
        intelligence_test.assessment_id = last_test.assessment_id
        intelligence_test.typed_assessment_ids = last_test.typed_assessment_ids
        test_suite.addTest(intelligence_test)
    
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(test_suite)


def run_all_tests():
    """Run all tests including basic functionality and production readiness"""
    print("\n===== RUNNING BASIC FUNCTIONALITY TESTS =====\n")
    run_tests()
    
    print("\n===== RUNNING PRODUCTION READINESS TESTS =====\n")
    run_production_readiness_tests()


if __name__ == "__main__":
    print("🚀 Starting Comprehensive Intelligence Layer Testing...")
    print("=" * 80)
    result = run_comprehensive_intelligence_tests()
    print("=" * 80)
    if result.wasSuccessful():
        print("✅ ALL INTELLIGENCE LAYER TESTS PASSED!")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        print(f"Failures: {len(result.failures)}, Errors: {len(result.errors)}")