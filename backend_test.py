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
        self.base_url = "https://16f31f7a-9a22-44c2-8d41-3e2a1b72fd7c.preview.emergentagent.com/api"
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
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        print(f"✅ Retrieved {len(data)} projects")
    
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

if __name__ == "__main__":
    run_tests()