import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { 
  TrendingUp, Activity, Target, Users, Zap, Shield, AlertTriangle, CheckCircle, 
  Calendar, Clock, PlayCircle, PauseCircle, CheckSquare, Flag, ArrowRight,
  FileText, User, Settings, BarChart3, Plus, Filter, Search, Edit, Eye,
  Lightbulb, Award, Bookmark, MessageSquare, Upload, Download, Star,
  ChevronDown, ChevronRight, List, Grid, MapPin, Layers
} from 'lucide-react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Color schemes for charts
const COLORS = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444'];
const NEWTON_COLORS = {
  inertia: '#ef4444',
  force: '#f59e0b', 
  reaction: '#8b5cf6'
};

// IMPACT Phases configuration - Manufacturing EAM Implementation
const IMPACT_PHASES = [
  {
    id: 'investigate',
    name: 'Investigate & Assess',
    color: '#ef4444',
    description: 'Understanding current state and establishing implementation foundation',
    icon: Target,
    shortDesc: 'Current State Analysis',
    newtonLaw: 'Overcoming Manufacturing Organizational Inertia',
    focus: 'Maintenance-Operations gap analysis and manufacturing performance baseline'
  },
  {
    id: 'mobilize',
    name: 'Mobilize & Prepare',
    color: '#f59e0b',
    description: 'Building infrastructure and preparing for implementation success',
    icon: Users,
    shortDesc: 'Infrastructure Building',
    newtonLaw: 'Measuring Forces and Preparing for Acceleration',
    focus: 'Cross-shift champion network and maintenance excellence communication'
  },
  {
    id: 'pilot',
    name: 'Pilot & Adapt',
    color: '#8b5cf6',
    description: 'Testing approach with limited group and refining strategies',
    icon: TrendingUp,
    shortDesc: 'Controlled Testing',
    newtonLaw: 'Testing Action-Reaction in Controlled Environment',
    focus: 'Proving maintenance excellence drives manufacturing performance'
  },
  {
    id: 'activate',
    name: 'Activate & Deploy',
    color: '#10b981',
    description: 'Full-scale implementation with comprehensive support',
    icon: CheckCircle,
    shortDesc: 'Full Deployment',
    newtonLaw: 'Applied Force - Implementation in Motion',
    focus: 'Embedding maintenance excellence across manufacturing organization'
  },
  {
    id: 'cement',
    name: 'Cement & Transfer',
    color: '#3b82f6',
    description: 'Institutionalizing change and transferring ownership',
    icon: Award,
    shortDesc: 'Institutionalization',
    newtonLaw: 'Continuous Force Application for Sustainable Motion',
    focus: 'Making maintenance excellence part of organizational culture'
  },
  {
    id: 'track',
    name: 'Track & Optimize',
    color: '#6366f1',
    description: 'Long-term monitoring and continuous improvement',
    icon: BarChart3,
    shortDesc: 'Continuous Improvement',
    newtonLaw: 'New Equilibrium State with Continuous Optimization',
    focus: 'Demonstrating sustained manufacturing performance gains'
  }
];

function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Auth states
  const [isLogin, setIsLogin] = useState(true);
  const [authData, setAuthData] = useState({
    email: '',
    password: '',
    full_name: '',
    organization: '',
    role: 'Team Member'
  });

  // Enhanced Assessment states for Multiple Types
  const [selectedAssessmentType, setSelectedAssessmentType] = useState('general_readiness');
  const [assessmentTypes, setAssessmentTypes] = useState({});
  const [assessmentData, setAssessmentData] = useState({
    project_name: '',
    assessment_type: 'general_readiness'
  });
  const [availableProjects, setAvailableProjects] = useState([]);

  // Dashboard states
  const [dashboardMetrics, setDashboardMetrics] = useState({});
  const [assessments, setAssessments] = useState([]);
  const [projects, setProjects] = useState([]);
  const [advancedAnalytics, setAdvancedAnalytics] = useState(null);
  const [impactPhases, setImpactPhases] = useState({});

  // Project workflow states
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedPhase, setSelectedPhase] = useState(null);
  const [newProjectData, setNewProjectData] = useState({
    name: '',
    description: '',
    target_completion_date: '',
    budget: '',
    project_name: '',
    client_organization: '',
    objectives: [''],
    scope: '',
    total_budget: '',
    estimated_end_date: ''
  });
  const [showNewProjectForm, setShowNewProjectForm] = useState(false);
  const [showEditProjectForm, setShowEditProjectForm] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [editProjectData, setEditProjectData] = useState({
    name: '',
    description: '',
    target_completion_date: '',
    budget: '',
    project_name: '',
    client_organization: '',
    objectives: [''],
    scope: '',
    total_budget: '',
    estimated_end_date: ''
  });
  const [showAssessmentToProject, setShowAssessmentToProject] = useState(false);
  const [selectedAssessmentForProject, setSelectedAssessmentForProject] = useState(null);
  const [projectView, setProjectView] = useState('grid'); // grid or timeline
  const [expandedTasks, setExpandedTasks] = useState({});

  // New Intelligence Layer States
  const [implementationPlan, setImplementationPlan] = useState(null);
  const [showImplementationPlan, setShowImplementationPlan] = useState(false);
  const [customizedPlaybook, setCustomizedPlaybook] = useState(null);
  const [showCustomizedPlaybook, setShowCustomizedPlaybook] = useState(false);
  
  // Predictive Analytics States
  const [predictiveAnalytics, setPredictiveAnalytics] = useState(null);
  const [showPredictiveAnalytics, setShowPredictiveAnalytics] = useState(false);
  const [riskMonitoring, setRiskMonitoring] = useState(null);
  const [showRiskMonitoring, setShowRiskMonitoring] = useState(false);
  
  // Enhancement 3: Detailed Project Management States
  const [budgetTracking, setBudgetTracking] = useState(null);
  const [showBudgetTracking, setShowBudgetTracking] = useState(false);
  const [projectForecasting, setProjectForecasting] = useState(null);
  const [showProjectForecasting, setShowProjectForecasting] = useState(false);
  const [stakeholderComms, setStakeholderComms] = useState(null);
  const [showStakeholderComms, setShowStakeholderComms] = useState(false);
  const [manufacturingExcellence, setManufacturingExcellence] = useState(null);
  const [showManufacturingExcellence, setShowManufacturingExcellence] = useState(false);
  
  // Enhancement 4: Advanced Project Workflow States
  const [projectEditMode, setProjectEditMode] = useState(false);
  const [phaseIntelligence, setPhaseIntelligence] = useState(null);
  const [showPhaseIntelligence, setShowPhaseIntelligence] = useState(false);
  const [phaseProgress, setPhaseProgress] = useState({});
  const [showPhaseProgressModal, setShowPhaseProgressModal] = useState(false);
  const [selectedPhaseForProgress, setSelectedPhaseForProgress] = useState(null);
  const [workflowStatus, setWorkflowStatus] = useState(null);
  const [showWorkflowStatus, setShowWorkflowStatus] = useState(false);

  // Enhancement 5: Admin Center States
  const [adminDashboard, setAdminDashboard] = useState(null);
  const [allUsers, setAllUsers] = useState([]);
  const [pendingUsers, setPendingUsers] = useState([]);
  const [userFilter, setUserFilter] = useState('all'); // all, pending, approved, rejected
  const [showUserDetails, setShowUserDetails] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showProjectAssignment, setShowProjectAssignment] = useState(false);
  const [assignmentData, setAssignmentData] = useState({
    project_id: '',
    user_id: '',
    role: 'collaborator',
    permissions: []
  });
  const [projectActivities, setProjectActivities] = useState([]);
  const [showProjectActivities, setShowProjectActivities] = useState(false);
  const [selectedProjectForActivities, setSelectedProjectForActivities] = useState(null);

  useEffect(() => {
    fetchAssessmentTypes(); // Fetch assessment types on component mount
  }, []);

  useEffect(() => {
    if (token) {
      fetchUserProfile();
      fetchDashboardData();
      fetchAdvancedAnalytics();
      fetchImpactPhases();
      fetchProjects();
    }
  }, [token]);

  useEffect(() => {
    if (user && user.is_admin) {
      fetchAdminDashboard();
      fetchAllUsers();
    }
  }, [user]);

  const fetchAssessmentTypes = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/assessment-types`);
      if (response.ok) {
        const data = await response.json();
        setAssessmentTypes(data.assessment_types);
        // Initialize with default assessment type if none selected
        if (!selectedAssessmentType && Object.keys(data.assessment_types).length > 0) {
          const firstType = Object.keys(data.assessment_types)[0];
          setSelectedAssessmentType(firstType);
          setTimeout(() => initializeAssessmentData(firstType), 100);
        }
      } else {
        console.error('Failed to fetch assessment types:', response.status, response.statusText);
      }
    } catch (err) {
      console.error('Failed to fetch assessment types:', err);
    }
  };

  const initializeAssessmentData = (assessmentType) => {
    if (!assessmentTypes[assessmentType]) return;
    
    const typeConfig = assessmentTypes[assessmentType];
    const newData = {
      project_name: '',
      assessment_type: assessmentType
    };
    
    // Initialize all dimensions for this type
    typeConfig.dimensions.forEach(dimension => {
      newData[dimension.id] = {
        name: dimension.name,
        score: 3,
        notes: '',
        description: dimension.description,
        category: dimension.category
      };
    });
    
    setAssessmentData(newData);
  };

  const fetchUserProfile = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/user/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (err) {
      console.error('Failed to fetch user profile:', err);
      handleAuthError();
    }
  };

  const fetchDashboardData = async () => {
    try {
      const [metricsRes, assessmentsRes, projectsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/dashboard/metrics`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_BASE_URL}/api/assessments`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_BASE_URL}/api/projects`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      setDashboardMetrics(metricsRes.data);
      setAssessments(assessmentsRes.data);
      setProjects(projectsRes.data.projects || []);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
    }
  };

  const fetchAdvancedAnalytics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/analytics/advanced`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAdvancedAnalytics(response.data);
    } catch (err) {
      console.error('Failed to fetch advanced analytics:', err);
    }
  };

  const fetchImpactPhases = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/impact/phases`);
      setImpactPhases(response.data);
    } catch (err) {
      console.error('Failed to fetch IMPACT phases:', err);
    }
  };

  const handleAuthError = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const response = await axios.post(`${API_BASE_URL}${endpoint}`, authData);
      
      // Handle different response formats for login vs register
      if (isLogin) {
        setToken(response.data.access_token);
        setUser(response.data.user);
        localStorage.setItem('token', response.data.access_token);
      } else {
        // Registration successful, show success message
        setError('Registration successful! Please wait for admin approval.');
        return;
      }
      
      setAuthData({
        email: '',
        password: '',
        full_name: '',
        organization: '',
        role: 'Team Member'
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleTypedAssessmentSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/assessments/create`, assessmentData, {
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        }
      });

      if (response.status === 200) {
        const result = response.data;
        alert(`${assessmentTypes[selectedAssessmentType]?.name || 'Assessment'} completed successfully! AI analysis has been generated.`);
        
        // Reset form
        initializeAssessmentData(selectedAssessmentType);
        
        // Refresh data
        fetchDashboardData();
        setActiveTab('results');
      } else {
        throw new Error('Failed to create assessment');
      }
    } catch (err) {
      console.error('Assessment submission error:', err);
      setError(err.response?.data?.detail || 'Failed to submit assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAssessmentSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/assessments`, assessmentData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('Manufacturing EAM Assessment completed successfully! AI analysis has been generated.');
      setAssessmentData({
        project_name: '',
        project_type: 'Manufacturing EAM Implementation',
        // Core Assessment Dimensions
        leadership_commitment: { 
          name: 'Leadership Commitment & Sponsorship', 
          score: 3, 
          notes: '',
          description: 'How committed is senior leadership to this manufacturing EAM implementation?'
        },
        organizational_culture: { 
          name: 'Organizational Culture & Change History', 
          score: 3, 
          notes: '',
          description: 'How well does the organization typically adapt to change in manufacturing environments?'
        },
        resource_availability: { 
          name: 'Resource Availability & Capability', 
          score: 3, 
          notes: '',
          description: 'Are adequate financial, human, and technical resources available for implementation?'
        },
        stakeholder_engagement: { 
          name: 'Stakeholder Engagement & Communication', 
          score: 3, 
          notes: '',
          description: 'How effective are existing stakeholder engagement and communication capabilities?'
        },
        training_capability: { 
          name: 'Training & Development Capability', 
          score: 3, 
          notes: '',
          description: 'What training capabilities and infrastructure exist for manufacturing teams?'
        },
        // Manufacturing-Specific Dimensions
        manufacturing_constraints: { 
          name: 'Manufacturing Constraints Management', 
          score: 3, 
          notes: '',
          description: 'How manageable are operational constraints during EAM implementation?'
        },
        maintenance_operations_alignment: { 
          name: 'Maintenance-Operations Alignment', 
          score: 3, 
          notes: '',
          description: 'How well aligned are maintenance and operations teams currently?'
        },
        shift_work_considerations: { 
          name: 'Shift Work & Coordination', 
          score: 3, 
          notes: '',
          description: 'How well can shift work patterns accommodate change activities?'
        },
        technical_readiness: { 
          name: 'Technical Infrastructure Readiness', 
          score: 3, 
          notes: '',
          description: 'How ready are employees and systems for EAM technology adoption?'
        },
        safety_compliance: { 
          name: 'Safety & Compliance Integration', 
          score: 3, 
          notes: '',
          description: 'How well can safety and regulatory requirements be integrated with changes?'
        }
      });
      
      fetchDashboardData();
      fetchAdvancedAnalytics();
      setActiveTab('assessments');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit assessment');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProjectFromAssessment = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const projectPayload = {
        assessment_id: selectedAssessmentForProject.id,
        project_name: newProjectData.name,
        description: newProjectData.description,
        target_completion_date: newProjectData.target_completion_date ? new Date(newProjectData.target_completion_date).toISOString() : null,
        budget: newProjectData.budget ? parseFloat(newProjectData.budget) : null
      };

      const response = await axios.post(`${API_BASE_URL}/api/projects/from-assessment`, projectPayload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('Project created successfully from assessment with AI-optimized workflow!');
      setNewProjectData({
        name: '',
        description: '',
        target_completion_date: '',
        budget: ''
      });
      setShowAssessmentToProject(false);
      setSelectedAssessmentForProject(null);
      fetchDashboardData();
      setActiveTab('projects');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project from assessment');
    } finally {
      setLoading(false);
    }
  };

  const handleTaskUpdate = async (projectId, taskId, updates) => {
    try {
      await axios.put(`${API_BASE_URL}/api/projects/${projectId}/tasks/${taskId}`, updates, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchDashboardData();
      // Update selected project if it's open
      if (selectedProject && selectedProject.id === projectId) {
        const updatedProject = await axios.get(`${API_BASE_URL}/api/projects/${projectId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSelectedProject(updatedProject.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update task');
    }
  };

  // New Intelligence Functions
  const generateImplementationPlan = async (assessmentId) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/assessments/${assessmentId}/implementation-plan`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Show implementation plan in a modal or new tab
      setImplementationPlan(response.data);
      setShowImplementationPlan(true);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate implementation plan');
    } finally {
      setLoading(false);
    }
  };

  const generateCustomizedPlaybook = async (assessmentId) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/assessments/${assessmentId}/customized-playbook`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Show customized playbook in a modal or new tab
      setCustomizedPlaybook(response.data);
      setShowCustomizedPlaybook(true);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate customized playbook');
    } finally {
      setLoading(false);
    }
  };

  // Enhancement 2: Predictive Analytics Functions
  const generatePredictiveAnalytics = async (assessmentId) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/assessments/${assessmentId}/predictive-analytics`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Show predictive analytics in a modal
      setPredictiveAnalytics(response.data);
      setShowPredictiveAnalytics(true);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate predictive analytics');
    } finally {
      setLoading(false);
    }
  };

  const generateRiskMonitoring = async (projectId) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/projects/${projectId}/risk-monitoring`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Show risk monitoring dashboard
      setRiskMonitoring(response.data);
      setShowRiskMonitoring(true);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate risk monitoring');
    } finally {
      setLoading(false);
    }
  };

  // Enhancement 3: Detailed Project Management Functions
  const generateDetailedBudgetTracking = async (projectId) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/projects/${projectId}/detailed-budget-tracking`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setBudgetTracking(response.data);
      setShowBudgetTracking(true);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate detailed budget tracking');
    } finally {
      setLoading(false);
    }
  };

  const generateAdvancedForecasting = async (projectId) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/projects/${projectId}/advanced-forecasting`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setProjectForecasting(response.data);
      setShowProjectForecasting(true);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate advanced forecasting');
    } finally {
      setLoading(false);
    }
  };

  const generateStakeholderCommunications = async (projectId) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/projects/${projectId}/stakeholder-communications`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setStakeholderComms(response.data);
      setShowStakeholderComms(true);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate stakeholder communications');
    } finally {
      setLoading(false);
    }
  };

  const generateManufacturingExcellenceTracking = async (projectId) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/projects/${projectId}/manufacturing-excellence-tracking`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setManufacturingExcellence(response.data);
      setShowManufacturingExcellence(true);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate manufacturing excellence tracking');
    } finally {
      setLoading(false);
    }
  };

  // Enhancement 4: Advanced Project Workflow Functions
  const updateProject = async (projectId, updateData) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.put(`${API_BASE_URL}/api/projects/${projectId}`, updateData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update selected project if it's the one being edited
      if (selectedProject && selectedProject.id === projectId) {
        setSelectedProject(response.data);
      }
      
      // Refresh projects list
      fetchDashboardData();
      
      setProjectEditMode(false);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update project');
    } finally {
      setLoading(false);
    }
  };

  const generatePhaseIntelligence = async (projectId, phaseName) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/projects/${projectId}/phases/${phaseName}/intelligence`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setPhaseIntelligence(response.data);
      setShowPhaseIntelligence(true);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate phase intelligence');
    } finally {
      setLoading(false);
    }
  };

  const updatePhaseProgress = async (projectId, phaseName, progressData) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.put(`${API_BASE_URL}/api/projects/${projectId}/phases/${phaseName}/progress`, progressData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update selected project
      setSelectedProject(response.data);
      
      // Refresh projects list
      fetchDashboardData();
      
      setShowPhaseProgressModal(false);
      setSelectedPhaseForProgress(null);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update phase progress');
    } finally {
      setLoading(false);
    }
  };

  const completePhaseWithAnalysis = async (projectId, phaseName, completionData) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/projects/${projectId}/phases/${phaseName}/complete`, completionData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update selected project
      const updatedProject = await axios.get(`${API_BASE_URL}/api/projects/${projectId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSelectedProject(updatedProject.data);
      
      // Show completion analysis
      alert(`Phase ${phaseName} completed successfully! Analysis generated.`);
      
      // Refresh projects list
      fetchDashboardData();
      
      setShowPhaseProgressModal(false);
      setSelectedPhaseForProgress(null);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to complete phase with analysis');
    } finally {
      setLoading(false);
    }
  };

  const getWorkflowStatus = async (projectId) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/projects/${projectId}/workflow-status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setWorkflowStatus(response.data);
      setShowWorkflowStatus(true);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get workflow status');
    } finally {
      setLoading(false);
    }
  };

  const openPhaseProgressModal = (phase) => {
    setSelectedPhaseForProgress(phase);
    setPhaseProgress({
      phase_name: phase.phase_name,
      completion_percentage: phase.completion_percentage || 0,
      status: phase.status || 'not_started',
      success_status: phase.success_status || '',
      success_reason: phase.success_reason || '',
      failure_reason: phase.failure_reason || '',
      lessons_learned: phase.lessons_learned || '',
      budget_spent: phase.budget_spent || 0,
      scope_changes: phase.scope_changes || [],
      tasks_completed: phase.tasks_completed || [],
      deliverables_completed: phase.deliverables_completed || [],
      risks_identified: phase.risks_identified || []
    });
    setShowPhaseProgressModal(true);
  };

  const handleDeliverableUpdate = async (projectId, deliverableId, updates) => {
    try {
      await axios.put(`${API_BASE_URL}/api/projects/${projectId}/deliverables/${deliverableId}`, updates, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchDashboardData();
      // Update selected project if it's open
      if (selectedProject && selectedProject.id === projectId) {
        const updatedProject = await axios.get(`${API_BASE_URL}/api/projects/${projectId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSelectedProject(updatedProject.data);
      }
    } catch (err) {
      console.error('Failed to update deliverable:', err);
    }
  };

  // Enhancement 5: Admin Center Functions
  const fetchAdminDashboard = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/admin/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAdminDashboard(response.data);
    } catch (err) {
      console.error('Failed to fetch admin dashboard:', err);
    }
  };

  const fetchAllUsers = async (status = null) => {
    try {
      const params = status ? { status } : {};
      const response = await axios.get(`${API_BASE_URL}/api/admin/users`, {
        headers: { Authorization: `Bearer ${token}` },
        params
      });
      setAllUsers(response.data.users);
      
      // Filter pending users
      const pending = response.data.users.filter(user => user.status === 'pending_approval');
      setPendingUsers(pending);
    } catch (err) {
      console.error('Failed to fetch users:', err);
    }
  };

  const approveUser = async (userId, action, rejectionReason = null) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/admin/users/approve`, {
        user_id: userId,
        action: action,
        rejection_reason: rejectionReason
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert(`User ${action}d successfully!`);
      
      // Refresh users list
      fetchAllUsers();
      if (user.is_admin) {
        fetchAdminDashboard();
      }
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to ${action} user`);
    } finally {
      setLoading(false);
    }
  };

  const assignUserToProject = async (projectId, userId, role, permissions = []) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/admin/projects/${projectId}/assign`, {
        project_id: projectId,
        user_id: userId,
        role: role,
        permissions: permissions
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('User assigned to project successfully!');
      
      // Refresh projects and close modal
      fetchDashboardData();
      setShowProjectAssignment(false);
      setAssignmentData({
        project_id: '',
        user_id: '',
        role: 'collaborator',
        permissions: []
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to assign user to project');
    } finally {
      setLoading(false);
    }
  };

  const fetchProjectActivities = async (projectId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/projects/${projectId}/activities`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProjectActivities(response.data.activities);
      setSelectedProjectForActivities(projectId);
      setShowProjectActivities(true);
    } catch (err) {
      console.error('Failed to fetch project activities:', err);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  const getPhaseColor = (phase) => {
    const phaseConfig = IMPACT_PHASES.find(p => p.id === phase);
    return phaseConfig ? phaseConfig.color : '#6b7280';
  };

  const getPhaseProgress = (project, phase) => {
    return project.phase_progress?.[phase] || 0;
  };

  const toggleTaskExpansion = (taskId) => {
    setExpandedTasks(prev => ({
      ...prev,
      [taskId]: !prev[taskId]
    }));
  };

  const renderAuthForm = () => (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">IMPACT Methodology</h1>
          <p className="text-gray-600">Revolutionizing Change Management with AI</p>
        </div>

        <div className="flex mb-6">
          <button
            onClick={() => setIsLogin(true)}
            className={`flex-1 py-2 px-4 rounded-l-lg font-semibold ${
              isLogin ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className={`flex-1 py-2 px-4 rounded-r-lg font-semibold ${
              !isLogin ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            Register
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleAuth} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              type="email"
              value={authData.email}
              onChange={(e) => setAuthData({...authData, email: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input
              type="password"
              value={authData.password}
              onChange={(e) => setAuthData({...authData, password: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              required
            />
          </div>

          {!isLogin && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                <input
                  type="text"
                  value={authData.full_name}
                  onChange={(e) => setAuthData({...authData, full_name: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Organization</label>
                <input
                  type="text"
                  value={authData.organization}
                  onChange={(e) => setAuthData({...authData, organization: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
                <select
                  value={authData.role}
                  onChange={(e) => setAuthData({...authData, role: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                >
                  <option value="Team Member">Team Member</option>
                  <option value="Project Manager">Project Manager</option>
                  <option value="Administrator">Administrator</option>
                  <option value="Super Administrator">Super Administrator</option>
                </select>
              </div>
            </>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 font-semibold"
          >
            {loading ? 'Processing...' : (isLogin ? 'Login' : 'Register')}
          </button>
        </form>
      </div>
    </div>
  );

  const renderDashboard = () => (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
      
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-700">Total Assessments</h3>
              <p className="text-3xl font-bold text-green-600">{dashboardMetrics.total_assessments || 0}</p>
            </div>
            <Activity className="h-8 w-8 text-green-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-700">Active Projects</h3>
              <p className="text-3xl font-bold text-blue-600">{dashboardMetrics.total_projects || 0}</p>
            </div>
            <Target className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-700">Avg Readiness</h3>
              <p className="text-3xl font-bold text-purple-600">{dashboardMetrics.average_readiness_score || 0}/5</p>
            </div>
            <TrendingUp className="h-8 w-8 text-purple-600" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-700">Success Rate</h3>
              <p className="text-3xl font-bold text-orange-600">{dashboardMetrics.average_success_probability || 0}%</p>
            </div>
            <CheckCircle className="h-8 w-8 text-orange-600" />
          </div>
        </div>
      </div>

      {/* IMPACT Methodology Overview */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">IMPACT Methodology Framework</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {IMPACT_PHASES.map((phase, index) => (
            <div key={phase.id} className="text-center p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg hover:shadow-md transition-shadow">
              <div className="text-2xl font-bold mb-2" style={{color: phase.color}}>{phase.name.charAt(0)}</div>
              <div className="text-sm text-gray-700 font-medium">{phase.name}</div>
              <div className="text-xs text-gray-500 mt-1">{phase.shortDesc}</div>
              <div className="text-xs text-gray-400 mt-1">Phase {index + 1}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Projects */}
      {projects.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-800">Recent Projects</h2>
            <button
              onClick={() => setActiveTab('projects')}
              className="text-green-600 hover:text-green-700 font-medium"
            >
              View All
            </button>
          </div>
          <div className="space-y-3">
            {projects.slice(0, 3).map(project => (
              <div key={project.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-800">{project.name}</h3>
                  <div className="flex items-center space-x-4 mt-1">
                    <p className="text-sm text-gray-600">
                      Current Phase: <span 
                        className="font-medium" 
                        style={{color: getPhaseColor(project.current_phase)}}
                      >
                        {project.current_phase?.charAt(0).toUpperCase() + project.current_phase?.slice(1)}
                      </span>
                    </p>
                    <p className="text-sm text-gray-500">
                      {project.tasks?.filter(t => t.status === 'completed').length || 0} / {project.tasks?.length || 0} tasks
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-700">{project.progress_percentage?.toFixed(1) || 0}% Complete</p>
                  <div className="w-24 h-2 bg-gray-200 rounded-full mt-1">
                    <div 
                      className="h-2 bg-green-500 rounded-full transition-all duration-300" 
                      style={{width: `${project.progress_percentage || 0}%`}}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => setActiveTab('assessment')}
            className="flex items-center p-4 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
          >
            <BarChart3 className="h-8 w-8 text-blue-600 mr-3" />
            <div className="text-left">
              <h3 className="font-medium text-blue-900">New Assessment</h3>
              <p className="text-sm text-blue-700">Evaluate change readiness</p>
            </div>
          </button>
          <button
            onClick={() => setShowNewProjectForm(true)}
            className="flex items-center p-4 bg-green-50 hover:bg-green-100 rounded-lg transition-colors"
          >
            <Plus className="h-8 w-8 text-green-600 mr-3" />
            <div className="text-left">
              <h3 className="font-medium text-green-900">New Project</h3>
              <p className="text-sm text-green-700">Start IMPACT workflow</p>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className="flex items-center p-4 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors"
          >
            <Zap className="h-8 w-8 text-purple-600 mr-3" />
            <div className="text-left">
              <h3 className="font-medium text-purple-900">View Analytics</h3>
              <p className="text-sm text-purple-700">AI-powered insights</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  );

  const handleCreateProject = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Transform frontend field names to match backend expectations
      const projectPayload = {
        project_name: newProjectData.name,
        description: newProjectData.description,
        target_completion_date: newProjectData.target_completion_date,
        total_budget: newProjectData.budget ? parseFloat(newProjectData.budget) : null,
        client_organization: newProjectData.client_organization,
        objectives: newProjectData.objectives,
        scope: newProjectData.scope,
        estimated_end_date: newProjectData.estimated_end_date
      };

      const response = await axios.post(`${API_BASE_URL}/api/projects`, projectPayload, {
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        }
      });

      if (response.status === 200) {
        alert('Project created successfully!');
        setNewProjectData({
          name: '',
          description: '',
          target_completion_date: '',
          budget: '',
          project_name: '',
          client_organization: '',
          objectives: [''],
          scope: '',
          total_budget: '',
          estimated_end_date: ''
        });
        setShowNewProjectForm(false);
        fetchProjects();
        fetchDashboardData();
        // Fix: Add redirect to dashboard after project creation
        setActiveTab('dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  // Handle editing a project
  const handleEditProject = (project) => {
    setEditingProject(project);
    setEditProjectData({
      name: project.name || project.project_name || '',
      description: project.description || '',
      target_completion_date: project.target_completion_date ? 
        new Date(project.target_completion_date).toISOString().split('T')[0] : '',
      budget: project.budget || project.total_budget || '',
      project_name: project.project_name || project.name || '',
      client_organization: project.client_organization || '',
      objectives: project.objectives || [''],
      scope: project.scope || '',
      total_budget: project.total_budget || project.budget || '',
      estimated_end_date: project.estimated_end_date || project.target_completion_date ?
        new Date(project.estimated_end_date || project.target_completion_date).toISOString().split('T')[0] : ''
    });
    setShowEditProjectForm(true);
  };

  // Handle updating a project
  const handleUpdateProject = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await axios.put(`${API_BASE_URL}/api/projects/${editingProject.id}`, editProjectData, {
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        }
      });

      if (response.status === 200) {
        alert('Project updated successfully!');
        setEditProjectData({
          name: '',
          description: '',
          target_completion_date: '',
          budget: '',
          project_name: '',
          client_organization: '',
          objectives: [''],
          scope: '',
          total_budget: '',
          estimated_end_date: ''
        });
        setShowEditProjectForm(false);
        setEditingProject(null);
        fetchProjects();
        fetchDashboardData();
        // Redirect to dashboard after successful update
        setActiveTab('dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update project');
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/projects`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setProjects(response.data.projects || []);
    } catch (err) {
      console.error('Failed to fetch projects:', err);
    }
  };

  const renderProjectWorkflow = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">IMPACT Project Workflow</h1>
        <button
          onClick={() => setShowNewProjectForm(true)}
          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Project
        </button>
      </div>



      {projects.length === 0 ? (
        <div className="text-center py-12">
          <Target className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-600 mb-2">No Projects Yet</h2>
          <p className="text-gray-500 mb-4">Start your first IMPACT methodology project</p>
          <button
            onClick={() => setShowNewProjectForm(true)}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700"
          >
            Create Your First Project
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Array.isArray(projects) && projects.map(project => (
            <div key={project.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800">{project.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{project.description}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${{
                    'active': 'bg-green-100 text-green-800',
                    'on_hold': 'bg-yellow-100 text-yellow-800',
                    'completed': 'bg-blue-100 text-blue-800',
                    'cancelled': 'bg-red-100 text-red-800'
                  }[project.status] || 'bg-gray-100 text-gray-800'}`}>
                    {project.status?.replace('_', ' ').toUpperCase()}
                  </span>
                </div>

                {/* Current Phase */}
                <div className="mb-4">
                  <div className="flex items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">Current Phase:</span>
                    <span 
                      className="ml-2 px-2 py-1 text-xs font-medium rounded-full text-white"
                      style={{backgroundColor: getPhaseColor(project.current_phase)}}
                    >
                      {project.current_phase?.toUpperCase()}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{width: `${project.progress_percentage || 0}%`}}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{project.progress_percentage?.toFixed(1) || 0}% Complete</p>
                </div>

                {/* IMPACT Phase Progress */}
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700">IMPACT Progress</h4>
                  <div className="grid grid-cols-6 gap-1">
                    {IMPACT_PHASES.map(phase => {
                      const progress = getPhaseProgress(project, phase.id);
                      const isCurrent = project.current_phase === phase.id;
                      return (
                        <div key={phase.id} className="text-center">
                          <div 
                            className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white mb-1 ${
                              isCurrent ? 'ring-2 ring-offset-1 ring-blue-500' : ''
                            }`}
                            style={{backgroundColor: phase.color, opacity: progress > 0 ? 1 : 0.3}}
                          >
                            {phase.name.charAt(0)}
                          </div>
                          <div className="text-xs text-gray-500">{progress.toFixed(0)}%</div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Project Tasks Summary */}
                {project.tasks && project.tasks.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Tasks: {project.tasks.filter(t => t.status === 'completed').length}/{project.tasks.length}</span>
                      <span className="text-gray-600">
                        {project.target_completion_date && 
                          `Due: ${new Date(project.target_completion_date).toLocaleDateString()}`
                        }
                      </span>
                    </div>
                  </div>
                )}

                <div className="mt-4 flex space-x-2">
                  <button
                    onClick={() => setSelectedProject(project)}
                    className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 text-sm"
                  >
                    View Details
                  </button>
                  <button 
                    onClick={() => handleEditProject(project)}
                    className="bg-gray-200 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-300 text-sm"
                  >
                    Edit
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Project Detail Modal */}
      {selectedProject && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{selectedProject.name}</h2>
                  <p className="text-gray-600 mt-1">{selectedProject.description}</p>
                </div>
                <button
                  onClick={() => setSelectedProject(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>

              {/* Project Phase Timeline */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">IMPACT Phase Timeline</h3>
                <div className="flex items-center space-x-4 overflow-x-auto pb-2">
                  {IMPACT_PHASES.map((phase, index) => {
                    const isCurrent = selectedProject.current_phase === phase.id;
                    const isCompleted = IMPACT_PHASES.findIndex(p => p.id === selectedProject.current_phase) > index;
                    const Icon = phase.icon;
                    
                    return (
                      <div key={phase.id} className="flex items-center flex-shrink-0">
                        <div className={`flex flex-col items-center ${isCompleted ? 'text-green-600' : isCurrent ? 'text-blue-600' : 'text-gray-400'}`}>
                          <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                            isCompleted ? 'bg-green-100' : isCurrent ? 'bg-blue-100' : 'bg-gray-100'
                          }`}>
                            <Icon className="h-6 w-6" />
                          </div>
                          <span className="text-xs font-medium mt-1">{phase.name}</span>
                          {impactPhases[phase.id] && (
                            <span className="text-xs text-gray-500 text-center max-w-20">
                              {impactPhases[phase.id].newton_law?.split(' - ')[0]}
                            </span>
                          )}
                        </div>
                        {index < IMPACT_PHASES.length - 1 && (
                          <ArrowRight className={`h-4 w-4 mx-2 ${isCompleted ? 'text-green-600' : 'text-gray-300'}`} />
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Current Phase Details */}
              {impactPhases[selectedProject.current_phase] && (
                <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                  <h3 className="text-lg font-semibold text-blue-900 mb-2">
                    Current Phase: {impactPhases[selectedProject.current_phase].name}
                  </h3>
                  <p className="text-blue-800 mb-3">{impactPhases[selectedProject.current_phase].description}</p>
                  <div className="text-sm text-blue-700">
                    <strong>Newton's Law Application:</strong> {impactPhases[selectedProject.current_phase].newton_insight}
                  </div>
                </div>
              )}

              {/* Tasks for Current Phase */}
              {selectedProject.tasks && selectedProject.tasks.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-3">Current Phase Tasks</h3>
                  <div className="space-y-2">
                    {selectedProject.tasks
                      .filter(task => task.phase === selectedProject.current_phase)
                      .map(task => (
                        <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center">
                            <input
                              type="checkbox"
                              checked={task.status === 'completed'}
                              onChange={(e) => handleTaskUpdate(selectedProject.id, task.id, {
                                status: e.target.checked ? 'completed' : 'pending'
                              })}
                              className="mr-3 h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                            />
                            <div>
                              <h4 className="font-medium text-gray-800">{task.title}</h4>
                              <p className="text-sm text-gray-600">{task.description}</p>
                            </div>
                          </div>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            task.status === 'completed' ? 'bg-green-100 text-green-800' :
                            task.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {task.status?.replace('_', ' ')}
                          </span>
                        </div>
                      ))
                    }
                  </div>
                </div>
              )}

              {/* Enhancement 3: Detailed Project Management Features */}
              <div className="mb-6 border-t pt-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2" />
                  Advanced Project Management
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  <button
                    onClick={() => generateDetailedBudgetTracking(selectedProject.id)}
                    className="flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <Calendar className="h-4 w-4 mr-2" />
                    Budget Tracking
                  </button>
                  <button
                    onClick={() => generateAdvancedForecasting(selectedProject.id)}
                    className="flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Project Forecasting
                  </button>
                  <button
                    onClick={() => generateStakeholderCommunications(selectedProject.id)}
                    className="flex items-center justify-center px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Stakeholder Comms
                  </button>
                  <button
                    onClick={() => generateRiskMonitoring(selectedProject.id)}
                    className="flex items-center justify-center px-4 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
                  >
                    <AlertTriangle className="h-4 w-4 mr-2" />
                    Risk Monitoring
                  </button>
                  <button
                    onClick={() => generateManufacturingExcellenceTracking(selectedProject.id)}
                    className="flex items-center justify-center px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    <Award className="h-4 w-4 mr-2" />
                    Manufacturing Excellence
                  </button>
                </div>
              </div>

              {/* Enhancement 4: Advanced Project Workflow Management */}
              <div className="mb-6 border-t pt-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                    <Settings className="h-5 w-5 mr-2" />
                    Project Workflow Management
                  </h3>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setProjectEditMode(true)}
                      className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <Edit className="h-4 w-4 mr-2" />
                      Edit Project
                    </button>
                    <button
                      onClick={() => getWorkflowStatus(selectedProject.id)}
                      className="flex items-center px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Workflow Status
                    </button>
                  </div>
                </div>

                {/* IMPACT Phases Progress */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-800 mb-3">IMPACT Phases Progress</h4>
                  <div className="space-y-3">
                    {impactPhases.map((phase, index) => {
                      const phaseData = selectedProject.phases?.find(p => p.phase_name === phase.name) || {
                        phase_name: phase.name,
                        status: 'not_started',
                        completion_percentage: 0
                      };
                      
                      return (
                        <div key={index} className="bg-white rounded-lg p-4 border">
                          <div className="flex justify-between items-center mb-2">
                            <div className="flex items-center">
                              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold mr-3 ${
                                phaseData.status === 'completed' ? 'bg-green-500' :
                                phaseData.status === 'in_progress' ? 'bg-blue-500' :
                                phaseData.status === 'failed' ? 'bg-red-500' :
                                'bg-gray-400'
                              }`}>
                                {index + 1}
                              </div>
                              <div>
                                <h5 className="font-semibold text-gray-800">{phase.name}</h5>
                                <p className="text-sm text-gray-600">{phase.description}</p>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                phaseData.status === 'completed' ? 'bg-green-100 text-green-800' :
                                phaseData.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                                phaseData.status === 'failed' ? 'bg-red-100 text-red-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {phaseData.status?.replace('_', ' ')}
                              </span>
                              <button
                                onClick={() => generatePhaseIntelligence(selectedProject.id, phase.name)}
                                className="px-2 py-1 bg-purple-600 text-white text-xs rounded hover:bg-purple-700"
                              >
                                Get Intelligence
                              </button>
                              <button
                                onClick={() => openPhaseProgressModal(phaseData)}
                                className="px-2 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
                              >
                                Update Progress
                              </button>
                            </div>
                          </div>
                          
                          {/* Progress Bar */}
                          <div className="mt-2">
                            <div className="flex justify-between text-sm text-gray-600 mb-1">
                              <span>Progress</span>
                              <span>{phaseData.completion_percentage || 0}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full ${
                                  phaseData.status === 'completed' ? 'bg-green-500' :
                                  phaseData.status === 'in_progress' ? 'bg-blue-500' :
                                  phaseData.status === 'failed' ? 'bg-red-500' :
                                  'bg-gray-400'
                                }`}
                                style={{ width: `${phaseData.completion_percentage || 0}%` }}
                              ></div>
                            </div>
                          </div>
                          
                          {/* Phase Details */}
                          {phaseData.success_status && (
                            <div className="mt-2 text-sm">
                              <span className={`font-medium ${
                                phaseData.success_status === 'successful' ? 'text-green-600' :
                                phaseData.success_status === 'failed' ? 'text-red-600' :
                                'text-yellow-600'
                              }`}>
                                {phaseData.success_status === 'successful' ? '✓ Successful' :
                                 phaseData.success_status === 'failed' ? '✗ Failed' :
                                 '! Partially Successful'}
                              </span>
                              {phaseData.success_reason && (
                                <p className="text-gray-600 mt-1">{phaseData.success_reason}</p>
                              )}
                              {phaseData.failure_reason && (
                                <p className="text-red-600 mt-1">{phaseData.failure_reason}</p>
                              )}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderAdvancedAnalytics = () => {
    if (!advancedAnalytics) {
      return (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      );
    }

    const trendData = advancedAnalytics.trend_analysis?.data || [];
    const newtonData = advancedAnalytics.newton_laws_data || {};
    const dimensionData = advancedAnalytics.dimension_breakdown || {};
    const benchmarks = advancedAnalytics.organizational_benchmarks || {};

    // Prepare radar chart data
    const radarData = [{
      dimension: 'Change Mgmt',
      score: dimensionData.change_management_maturity || 0
    }, {
      dimension: 'Communication',
      score: dimensionData.communication_effectiveness || 0
    }, {
      dimension: 'Leadership',
      score: dimensionData.leadership_support || 0
    }, {
      dimension: 'Adaptability',
      score: dimensionData.workforce_adaptability || 0
    }, {
      dimension: 'Resources',
      score: dimensionData.resource_adequacy || 0
    }];

    // Newton's Laws data for visualization
    const newtonVisualizationData = [
      { law: 'Inertia', value: newtonData.average_inertia || 0, color: NEWTON_COLORS.inertia },
      { law: 'Force', value: newtonData.average_force_required || 0, color: NEWTON_COLORS.force },
      { law: 'Resistance', value: newtonData.average_resistance || 0, color: NEWTON_COLORS.reaction }
    ];

    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Advanced AI Analytics</h1>

        {/* Newton's Laws Visualization */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
            <Zap className="h-5 w-5 mr-2" />
            Newton's Laws Applied to Organizational Change
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={newtonVisualizationData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="law" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8884d8">
                    {newtonVisualizationData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-4">
              <div className="p-4 bg-red-50 rounded-lg border-l-4 border-red-400">
                <h3 className="font-semibold text-red-800">First Law: Organizational Inertia</h3>
                <p className="text-sm text-red-700">Average: {newtonData.average_inertia || 0} units</p>
                <p className="text-xs text-red-600 mt-1">Organizations at rest tend to stay at rest</p>
              </div>
              <div className="p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-400">
                <h3 className="font-semibold text-yellow-800">Second Law: Force Required</h3>
                <p className="text-sm text-yellow-700">Average: {newtonData.average_force_required || 0} units</p>
                <p className="text-xs text-yellow-600 mt-1">Change = Force applied / Organizational mass</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg border-l-4 border-purple-400">
                <h3 className="font-semibold text-purple-800">Third Law: Resistance</h3>
                <p className="text-sm text-purple-700">Average: {newtonData.average_resistance || 0} units</p>
                <p className="text-xs text-purple-600 mt-1">Every action produces equal opposite reaction</p>
              </div>
            </div>
          </div>
        </div>

        {/* Trend Analysis */}
        {trendData.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <TrendingUp className="h-5 w-5 mr-2" />
              Assessment Trends Over Time
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={(date) => new Date(date).toLocaleDateString()} />
                <YAxis />
                <Tooltip labelFormatter={(date) => new Date(date).toLocaleDateString()} />
                <Line type="monotone" dataKey="overall_score" stroke="#10b981" strokeWidth={2} name="Overall Score" />
                <Line type="monotone" dataKey="success_probability" stroke="#3b82f6" strokeWidth={2} name="Success Probability" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* 5-Dimension Radar Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Target className="h-5 w-5 mr-2" />
              Organizational Readiness Profile
            </h2>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="dimension" />
                <PolarRadiusAxis angle={90} domain={[0, 5]} />
                <Radar name="Score" dataKey="score" stroke="#10b981" fill="#10b981" fillOpacity={0.3} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Organizational Benchmarks */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Users className="h-5 w-5 mr-2" />
              Industry Benchmarks
            </h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span className="text-sm font-medium">Your Average</span>
                <span className="text-lg font-bold text-green-600">{benchmarks.industry_comparison?.your_average || 0}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span className="text-sm font-medium">Industry Average</span>
                <span className="text-lg font-bold text-blue-600">{benchmarks.industry_comparison?.industry_average || 0}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span className="text-sm font-medium">Top Quartile</span>
                <span className="text-lg font-bold text-purple-600">{benchmarks.industry_comparison?.top_quartile || 0}</span>
              </div>
              <div className="mt-4 p-4 bg-green-50 rounded-lg">
                <h3 className="font-semibold text-green-800">Maturity Level</h3>
                <p className="text-lg font-bold text-green-700">{benchmarks.maturity_level || 'Assessment Required'}</p>
                <p className="text-sm text-green-600">{benchmarks.industry_comparison?.performance_percentile || 0}th percentile</p>
              </div>
            </div>
          </div>
        </div>

        {/* Predictive Insights */}
        {advancedAnalytics.predictive_insights && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Shield className="h-5 w-5 mr-2" />
              AI-Powered Predictive Insights
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-700 mb-2">Trajectory Analysis</h3>
                <p className="text-sm text-gray-600 mb-2">Current trend: <span className="font-medium capitalize">{advancedAnalytics.predictive_insights.trajectory}</span></p>
                <p className="text-sm text-gray-600 mb-2">Predicted next score: <span className="font-bold text-green-600">{advancedAnalytics.predictive_insights.predicted_next_score}</span></p>
                <p className="text-sm text-gray-600">Confidence: <span className="font-medium">{advancedAnalytics.predictive_insights.confidence_level}%</span></p>
              </div>
              <div>
                <h3 className="font-semibold text-gray-700 mb-2">Strategic Recommendations</h3>
                <ul className="space-y-1">
                  {advancedAnalytics.predictive_insights.recommendations?.map((rec, index) => (
                    <li key={index} className="text-sm text-gray-600 flex items-start">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderAssessmentForm = () => (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Change Readiness Assessment</h2>
          <p className="text-lg text-gray-600 mb-6">
            Select an assessment type and evaluate your organization's readiness for transformation projects.
            Our systematic approach provides actionable insights for guaranteed implementation success.
          </p>
          
          {/* Assessment Type Selection */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-4">
              Select Assessment Type
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(assessmentTypes).map(([key, type]) => (
                <div 
                  key={key}
                  onClick={() => {
                    setSelectedAssessmentType(key);
                    initializeAssessmentData(key);
                  }}
                  className={`p-4 border rounded-lg cursor-pointer transition-all duration-200 ${
                    selectedAssessmentType === key 
                      ? 'border-green-500 bg-green-50 shadow-md' 
                      : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
                  }`}
                >
                  <div className="text-2xl mb-2">{type.icon}</div>
                  <h3 className="font-medium text-gray-900 mb-2">{type.name}</h3>
                  <p className="text-sm text-gray-600">{type.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {selectedAssessmentType && assessmentTypes[selectedAssessmentType] && (
          <form onSubmit={handleTypedAssessmentSubmit} className="space-y-8">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Project Name
              </label>
              <input
                type="text"
                value={assessmentData.project_name}
                onChange={(e) => setAssessmentData({...assessmentData, project_name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder={`Enter your ${assessmentTypes[selectedAssessmentType].name.toLowerCase()} project name`}
                required
              />
            </div>

            {/* Core Dimensions */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-6 border-b border-gray-200 pb-2">
                Core Readiness Dimensions
              </h3>
              {assessmentTypes[selectedAssessmentType]?.dimensions
                ?.filter(dim => dim.category === 'core')
                ?.map((dimension) => {
                  const dimensionData = assessmentData[dimension.id] || { score: 3, notes: '' };
                  return (
                    <div key={dimension.id} className="mb-8 p-6 bg-gray-50 rounded-lg">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h4 className="text-lg font-medium text-gray-900">{dimension.name}</h4>
                          <p className="text-sm text-gray-600 mt-1">{dimension.description}</p>
                        </div>
                      </div>
                      
                      <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Score (1=Poor, 5=Excellent)
                        </label>
                        <div className="flex space-x-4">
                          {[1, 2, 3, 4, 5].map((score) => (
                            <label key={score} className="flex items-center">
                              <input
                                type="radio"
                                name={`${dimension.id}_score`}
                                value={score}
                                checked={dimensionData.score === score}
                                onChange={(e) => setAssessmentData({
                                  ...assessmentData,
                                  [dimension.id]: { 
                                    ...dimensionData, 
                                    score: parseInt(e.target.value) 
                                  }
                                })}
                                className="mr-2 text-green-600"
                              />
                              <span className="text-sm">{score}</span>
                            </label>
                          ))}
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Notes (Optional)
                        </label>
                        <textarea
                          value={dimensionData.notes || ''}
                          onChange={(e) => setAssessmentData({
                            ...assessmentData,
                            [dimension.id]: { 
                              ...dimensionData, 
                              notes: e.target.value 
                            }
                          })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                          rows="2"
                          placeholder="Add any specific notes or context..."
                        />
                      </div>
                    </div>
                  );
                })}
            </div>

            {/* Specialized Dimensions */}
            {assessmentTypes[selectedAssessmentType]?.dimensions?.some(dim => dim.category === 'specialized') && (
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-6 border-b border-gray-200 pb-2">
                  Specialized Assessment Factors
                </h3>
                <p className="text-sm text-gray-600 mb-6">
                  These dimensions assess specialized considerations specific to {assessmentTypes[selectedAssessmentType]?.name?.toLowerCase()}.
                </p>
                
                {assessmentTypes[selectedAssessmentType]?.dimensions
                  ?.filter(dim => dim.category === 'specialized')
                  ?.map((dimension) => {
                      const dimensionData = assessmentData[dimension.id] || { score: 3, notes: '' };
                      return (
                        <div key={dimension.id} className="mb-8 p-6 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                          <div className="flex items-start justify-between mb-4">
                            <div>
                              <h4 className="text-lg font-medium text-gray-900">{dimension.name}</h4>
                              <p className="text-sm text-gray-600 mt-1">{dimension.description}</p>
                            </div>
                          </div>
                          
                          <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Score (1=Poor, 5=Excellent)
                            </label>
                            <div className="flex space-x-4">
                              {[1, 2, 3, 4, 5].map((score) => (
                                <label key={score} className="flex items-center">
                                  <input
                                    type="radio"
                                    name={`${dimension.id}_score`}
                                    value={score}
                                    checked={dimensionData.score === score}
                                    onChange={(e) => setAssessmentData({
                                      ...assessmentData,
                                      [dimension.id]: { 
                                        ...dimensionData, 
                                        score: parseInt(e.target.value) 
                                      }
                                    })}
                                    className="mr-2 text-blue-600"
                                  />
                                  <span className="text-sm">{score}</span>
                                </label>
                              ))}
                            </div>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Notes (Optional)
                            </label>
                            <textarea
                              value={dimensionData.notes || ''}
                              onChange={(e) => setAssessmentData({
                                ...assessmentData,
                                [dimension.id]: { 
                                  ...dimensionData, 
                                  notes: e.target.value 
                                }
                              })}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              rows="2"
                              placeholder="Add specialized context or considerations..."
                            />
                          </div>
                        </div>
                      );
                    })}
              </div>
            )}

            <div className="flex justify-center">
              <button
                type="submit"
                disabled={loading}
                className="bg-green-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Processing...' : `Complete ${assessmentTypes[selectedAssessmentType].name}`}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );

  const renderAssessmentsList = () => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Assessment Results</h2>
      
      {assessments.length === 0 ? (
        <div className="text-center py-8">
          <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No assessments completed yet.</p>
          <button
            onClick={() => setActiveTab('assessment')}
            className="mt-4 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700"
          >
            Create Your First Assessment
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {assessments.map(assessment => (
            <div key={assessment.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-gray-800">{assessment.project_name}</h3>
                <div className="flex space-x-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    assessment.overall_score >= 4 ? 'bg-green-100 text-green-800' :
                    assessment.overall_score >= 3 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {assessment.overall_score?.toFixed(1)}/5
                  </span>
                  <span className="px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                    {assessment.success_probability?.toFixed(1)}% Success
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div className="text-center p-3 bg-gray-50 rounded">
                  <p className="text-sm text-gray-600">Overall Score</p>
                  <p className="text-xl font-bold text-green-600">{assessment.overall_score?.toFixed(1)}/5</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded">
                  <p className="text-sm text-gray-600">Success Probability</p>
                  <p className="text-xl font-bold text-purple-600">{assessment.success_probability?.toFixed(1)}%</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded">
                  <p className="text-sm text-gray-600">Assessment Date</p>
                  <p className="text-lg font-semibold text-gray-800">
                    {new Date(assessment.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>

              {assessment.newton_analysis && (
                <div className="mb-4 p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-semibold text-blue-800 mb-2">Newton's Laws Analysis</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                    <div className="text-center">
                      <p className="font-medium text-red-700">Organizational Inertia</p>
                      <p className="text-lg font-bold text-red-600">{assessment.newton_analysis.inertia?.value || 0}</p>
                      <p className="text-xs text-red-500">{assessment.newton_analysis.inertia?.interpretation || 'N/A'}</p>
                    </div>
                    <div className="text-center">
                      <p className="font-medium text-yellow-700">Force Required</p>
                      <p className="text-lg font-bold text-yellow-600">{assessment.newton_analysis.force?.required || 0}</p>
                      <p className="text-xs text-yellow-500">units</p>
                    </div>
                    <div className="text-center">
                      <p className="font-medium text-purple-700">Expected Resistance</p>
                      <p className="text-lg font-bold text-purple-600">{assessment.newton_analysis.reaction?.resistance || 0}</p>
                      <p className="text-xs text-purple-500">units</p>
                    </div>
                  </div>
                </div>
              )}

              {assessment.ai_analysis && (
                <div className="mb-4">
                  <h4 className="font-semibold text-gray-800 mb-2 flex items-center">
                    <Zap className="h-4 w-4 mr-1" />
                    AI Analysis
                  </h4>
                  <div className="text-gray-700 bg-gray-50 p-4 rounded text-sm leading-relaxed">
                    {assessment.ai_analysis.substring(0, 300)}...
                  </div>
                </div>
              )}

              {assessment.recommendations && assessment.recommendations.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-semibold text-gray-800 mb-2 flex items-center">
                    <CheckCircle className="h-4 w-4 mr-1" />
                    AI Recommendations
                  </h4>
                  <ul className="space-y-2">
                    {assessment.recommendations.slice(0, 3).map((rec, index) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start">
                        <span className="inline-block w-5 h-5 bg-green-500 text-white rounded-full text-xs flex items-center justify-center mr-2 mt-0.5 flex-shrink-0">
                          {index + 1}
                        </span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* New Intelligence Features */}
              <div className="mt-6 border-t pt-4">
                <h4 className="font-semibold text-gray-800 mb-3 flex items-center">
                  <Lightbulb className="h-4 w-4 mr-1" />
                  Implementation Intelligence
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <button
                    onClick={() => generateImplementationPlan(assessment.id)}
                    className="flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Calendar className="h-4 w-4 mr-2" />
                    Generate Week-by-Week Plan
                  </button>
                  <button
                    onClick={() => generateCustomizedPlaybook(assessment.id)}
                    className="flex items-center justify-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    Generate Custom Playbook
                  </button>
                  <button
                    onClick={() => generatePredictiveAnalytics(assessment.id)}
                    className="flex items-center justify-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
                  >
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Predictive Analytics
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderAdminCenter = () => {
    if (!user || !user.is_admin) {
      return (
        <div className="text-center py-8">
          <p className="text-red-600">Access denied. Admin privileges required.</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Admin Header */}
        <div className="bg-white rounded-lg shadow p-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Admin Center</h1>
          <p className="text-gray-600">Manage users, projects, and platform settings</p>
        </div>

        {/* Admin Dashboard Stats */}
        {adminDashboard && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold text-gray-800 mb-2">Total Users</h3>
              <p className="text-3xl font-bold text-blue-600">{adminDashboard.user_statistics?.total_users || 0}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold text-gray-800 mb-2">Pending Approvals</h3>
              <p className="text-3xl font-bold text-yellow-600">{adminDashboard.user_statistics?.pending_approvals || 0}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold text-gray-800 mb-2">Active Projects</h3>
              <p className="text-3xl font-bold text-green-600">{adminDashboard.project_statistics?.active_projects || 0}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold text-gray-800 mb-2">Total Assessments</h3>
              <p className="text-3xl font-bold text-purple-600">{adminDashboard.assessment_statistics?.total_assessments || 0}</p>
            </div>
          </div>
        )}

        {/* User Management Section */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-800">User Management</h2>
              <div className="flex space-x-2">
                <button
                  onClick={() => setUserFilter('all')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    userFilter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  All ({allUsers.length})
                </button>
                <button
                  onClick={() => setUserFilter('pending')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    userFilter === 'pending' ? 'bg-yellow-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Pending ({pendingUsers.length})
                </button>
                <button
                  onClick={() => setUserFilter('approved')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    userFilter === 'approved' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Approved
                </button>
              </div>
            </div>
          </div>

          <div className="p-6">
            <div className="space-y-4">
              {(userFilter === 'all' ? allUsers : 
                userFilter === 'pending' ? pendingUsers : 
                allUsers.filter(u => u.status === 'approved')
              ).map((userItem) => (
                <div key={userItem.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">{userItem.full_name.charAt(0)}</span>
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-800">{userItem.full_name}</h3>
                      <p className="text-sm text-gray-600">{userItem.email}</p>
                      <p className="text-sm text-gray-500">{userItem.organization} • {userItem.role}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      userItem.status === 'approved' ? 'bg-green-100 text-green-800' :
                      userItem.status === 'pending_approval' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {userItem.status?.replace('_', ' ')}
                    </span>
                    {userItem.status === 'pending_approval' && (
                      <div className="space-x-2">
                        <button
                          onClick={() => approveUser(userItem.id, 'approve')}
                          className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => approveUser(userItem.id, 'reject', 'Admin decision')}
                          className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                        >
                          Reject
                        </button>
                      </div>
                    )}
                    {userItem.status === 'approved' && (
                      <button
                        onClick={() => {
                          setSelectedUser(userItem);
                          setShowProjectAssignment(true);
                        }}
                        className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                      >
                        Assign to Project
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Project Assignment Modal */}
        {showProjectAssignment && selectedUser && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-md w-full">
              <div className="p-6 border-b">
                <h3 className="text-lg font-semibold text-gray-800">Assign User to Project</h3>
                <p className="text-sm text-gray-600 mt-1">Assign {selectedUser.full_name} to a project</p>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Project</label>
                  <select
                    value={assignmentData.project_id}
                    onChange={(e) => setAssignmentData({...assignmentData, project_id: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select a project</option>
                    {Array.isArray(projects) && projects.map((project) => (
                      <option key={project.id} value={project.id}>{project.project_name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
                  <select
                    value={assignmentData.role}
                    onChange={(e) => setAssignmentData({...assignmentData, role: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="viewer">Viewer</option>
                    <option value="collaborator">Collaborator</option>
                    <option value="owner">Owner</option>
                  </select>
                </div>
              </div>
              <div className="p-6 border-t flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowProjectAssignment(false);
                    setSelectedUser(null);
                    setAssignmentData({project_id: '', user_id: '', role: 'collaborator', permissions: []});
                  }}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => assignUserToProject(assignmentData.project_id, selectedUser.id, assignmentData.role)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  disabled={!assignmentData.project_id}
                >
                  Assign
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Project Activities Modal */}
        {showProjectActivities && selectedProjectForActivities && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <div className="p-6 border-b">
                <h3 className="text-lg font-semibold text-gray-800">Project Activities</h3>
                <p className="text-sm text-gray-600 mt-1">Recent activities for this project</p>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {projectActivities.map((activity, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                      <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-xs font-semibold">{activity.user_name?.charAt(0) || 'U'}</span>
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-800">{activity.user_name || 'Unknown User'}</p>
                        <p className="text-sm text-gray-600">{activity.details}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(activity.timestamp).toLocaleDateString()} at {new Date(activity.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="p-6 border-t flex justify-end">
                <button
                  onClick={() => {
                    setShowProjectActivities(false);
                    setSelectedProjectForActivities(null);
                    setProjectActivities([]);
                  }}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderMainContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return renderDashboard();
      case 'assessment':
        return renderAssessmentForm();
      case 'assessments':
        return renderAssessmentsList();
      case 'analytics':
        return renderAdvancedAnalytics();
      case 'projects':
        return renderProjectWorkflow();
      case 'admin':
        return renderAdminCenter();
      default:
        return renderDashboard();
    }
  };

  if (!user) {
    return renderAuthForm();
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-green-600">IMPACT Methodology</h1>
            </div>
            
            <div className="flex space-x-4">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'dashboard' ? 'bg-green-600 text-white' : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActiveTab('projects')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'projects' ? 'bg-green-600 text-white' : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Projects
              </button>
              <button
                onClick={() => setActiveTab('assessment')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'assessment' ? 'bg-green-600 text-white' : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                New Assessment
              </button>
              <button
                onClick={() => setActiveTab('assessments')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'assessments' ? 'bg-green-600 text-white' : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Results
              </button>
              <button
                onClick={() => setActiveTab('analytics')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'analytics' ? 'bg-green-600 text-white' : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                AI Analytics
              </button>
              
              {user && user.is_admin && (
                <button
                  onClick={() => setActiveTab('admin')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    activeTab === 'admin' ? 'bg-red-600 text-white' : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  Admin Center
                </button>
              )}
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Welcome, {user.full_name}</span>
              <button
                onClick={logout}
                className="text-sm text-red-600 hover:text-red-800 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderMainContent()}
      </main>

      {/* Implementation Plan Modal */}
      {showImplementationPlan && implementationPlan && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-6xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800">Week-by-Week Implementation Plan</h2>
                <button
                  onClick={() => setShowImplementationPlan(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-blue-50 p-3 rounded">
                  <p className="font-semibold text-blue-800">Total Budget</p>
                  <p className="text-xl font-bold text-blue-600">${implementationPlan.summary?.total_budget?.toLocaleString() || 0}</p>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <p className="font-semibold text-green-800">Total Hours</p>
                  <p className="text-xl font-bold text-green-600">{implementationPlan.summary?.total_hours || 0}</p>
                </div>
                <div className="bg-yellow-50 p-3 rounded">
                  <p className="font-semibold text-yellow-800">Risk Level</p>
                  <p className="text-xl font-bold text-yellow-600">{implementationPlan.summary?.overall_risk_level || 'Unknown'}</p>
                </div>
                <div className="bg-purple-50 p-3 rounded">
                  <p className="font-semibold text-purple-800">Success Probability</p>
                  <p className="text-xl font-bold text-purple-600">{implementationPlan.summary?.success_probability || 0}%</p>
                </div>
              </div>
            </div>
            
            <div className="p-6">
              <div className="space-y-6">
                {Object.entries(implementationPlan.weeks || {}).map(([weekNum, week]) => (
                  <div key={weekNum} className="border rounded-lg p-4">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-lg font-semibold text-gray-800">
                        Week {weekNum}: {week.title}
                      </h3>
                      <div className="flex space-x-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          week.risk_level === 'High' ? 'bg-red-100 text-red-800' :
                          week.risk_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {week.risk_level} Risk
                        </span>
                        <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                          {week.phase}
                        </span>
                      </div>
                    </div>
                    
                    <p className="text-gray-700 mb-4">{week.description}</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-semibold text-gray-800 mb-2">Base Activities:</h4>
                        <ul className="text-sm space-y-1">
                          {week.base_activities?.map((activity, idx) => (
                            <li key={idx} className="flex items-start">
                              <span className="w-2 h-2 bg-green-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                              {activity}
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold text-gray-800 mb-2">Additional Activities:</h4>
                        <ul className="text-sm space-y-1">
                          {week.additional_activities?.map((activity, idx) => (
                            <li key={idx} className="flex items-start">
                              <span className="w-2 h-2 bg-blue-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                              {activity}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    
                    <div className="mt-4 flex justify-between items-center text-sm text-gray-600">
                      <span>Duration: {week.duration_hours} hours</span>
                      <span>Budget: ${week.final_budget?.toLocaleString() || 0}</span>
                      <span>IMPACT Phase: {week.impact_phase_alignment}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Customized Playbook Modal */}
      {showCustomizedPlaybook && customizedPlaybook && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800">Customized Change Management Playbook</h2>
                <button
                  onClick={() => setShowCustomizedPlaybook(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-blue-50 p-3 rounded">
                  <p className="font-semibold text-blue-800">Project</p>
                  <p className="text-sm font-medium text-blue-600">{customizedPlaybook.project_name}</p>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <p className="font-semibold text-green-800">Readiness Score</p>
                  <p className="text-xl font-bold text-green-600">{customizedPlaybook.overall_readiness_score}/5</p>
                </div>
                <div className="bg-yellow-50 p-3 rounded">
                  <p className="font-semibold text-yellow-800">Readiness Level</p>
                  <p className="text-sm font-medium text-yellow-600">{customizedPlaybook.readiness_level}</p>
                </div>
                <div className="bg-purple-50 p-3 rounded">
                  <p className="font-semibold text-purple-800">Success Probability</p>
                  <p className="text-xl font-bold text-purple-600">{customizedPlaybook.success_probability}%</p>
                </div>
              </div>
            </div>
            
            <div className="p-6">
              <div className="prose max-w-none">
                <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {customizedPlaybook.content}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Predictive Analytics Modal */}
      {showPredictiveAnalytics && predictiveAnalytics && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-7xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800">Predictive Analytics Dashboard</h2>
                <button
                  onClick={() => setShowPredictiveAnalytics(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-blue-50 p-3 rounded">
                  <p className="font-semibold text-blue-800">Project Outlook</p>
                  <p className="text-lg font-bold text-blue-600">{predictiveAnalytics.project_outlook?.overall_risk_level || 'Unknown'}</p>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <p className="font-semibold text-green-800">Success Probability</p>
                  <p className="text-xl font-bold text-green-600">{predictiveAnalytics.project_outlook?.success_probability || 0}%</p>
                </div>
                <div className="bg-orange-50 p-3 rounded">
                  <p className="font-semibold text-orange-800">Budget Risk</p>
                  <p className="text-lg font-bold text-orange-600">{predictiveAnalytics.budget_risk_analysis?.risk_level || 'Unknown'}</p>
                </div>
                <div className="bg-purple-50 p-3 rounded">
                  <p className="font-semibold text-purple-800">Timeline Risk</p>
                  <p className="text-lg font-bold text-purple-600">{predictiveAnalytics.timeline_optimization?.timeline_outlook || 'Unknown'}</p>
                </div>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Task Success Predictions */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                  <Target className="h-5 w-5 mr-2" />
                  Task Success Predictions
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-red-700 mb-3">Highest Risk Tasks</h4>
                    <div className="space-y-2">
                      {predictiveAnalytics.highest_risk_tasks?.slice(0, 3).map((task, idx) => (
                        <div key={idx} className="flex items-center justify-between p-2 bg-red-50 rounded">
                          <span className="text-sm font-medium">{task.task_description}</span>
                          <span className="text-sm font-bold text-red-600">{task.success_probability}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-green-700 mb-3">Lowest Risk Tasks</h4>
                    <div className="space-y-2">
                      {predictiveAnalytics.lowest_risk_tasks?.slice(0, 3).map((task, idx) => (
                        <div key={idx} className="flex items-center justify-between p-2 bg-green-50 rounded">
                          <span className="text-sm font-medium">{task.task_description}</span>
                          <span className="text-sm font-bold text-green-600">{task.success_probability}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Budget Risk Analysis */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                  <AlertTriangle className="h-5 w-5 mr-2" />
                  Budget Risk Analysis
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-3 bg-gray-50 rounded">
                    <p className="text-sm text-gray-600">Overrun Probability</p>
                    <p className="text-2xl font-bold text-orange-600">{predictiveAnalytics.budget_risk_analysis?.overrun_probability || 0}%</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded">
                    <p className="text-sm text-gray-600">Expected Overrun</p>
                    <p className="text-2xl font-bold text-red-600">{predictiveAnalytics.budget_risk_analysis?.expected_overrun_percentage || 0}%</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded">
                    <p className="text-sm text-gray-600">Risk-Adjusted Budget</p>
                    <p className="text-lg font-bold text-blue-600">${predictiveAnalytics.budget_risk_analysis?.risk_adjusted_budget?.toLocaleString() || 0}</p>
                  </div>
                </div>
              </div>

              {/* Scope Creep Analysis */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Scope Creep Analysis
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="text-center p-3 bg-yellow-50 rounded">
                      <p className="text-sm text-yellow-800">Scope Creep Probability</p>
                      <p className="text-2xl font-bold text-yellow-600">{predictiveAnalytics.scope_creep_analysis?.scope_creep_probability || 0}%</p>
                    </div>
                  </div>
                  <div>
                    <div className="text-center p-3 bg-purple-50 rounded">
                      <p className="text-sm text-purple-800">Expected Impact</p>
                      <p className="text-lg font-bold text-purple-600">{predictiveAnalytics.scope_creep_analysis?.expected_impact || 'Unknown'}</p>
                    </div>
                  </div>
                </div>
                <div className="mt-4">
                  <h4 className="font-medium text-gray-700 mb-2">Typical Scope Additions:</h4>
                  <ul className="space-y-1">
                    {predictiveAnalytics.scope_creep_analysis?.typical_scope_additions?.map((addition, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start">
                        <span className="w-2 h-2 bg-yellow-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                        {addition}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Recommended Actions */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                  <CheckCircle className="h-5 w-5 mr-2" />
                  Recommended Actions
                </h3>
                <div className="space-y-2">
                  {predictiveAnalytics.project_outlook?.recommended_actions?.map((action, idx) => (
                    <div key={idx} className="flex items-start p-3 bg-blue-50 rounded">
                      <span className="inline-block w-5 h-5 bg-blue-500 text-white rounded-full text-xs flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                        {idx + 1}
                      </span>
                      <span className="text-sm text-gray-700">{action}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Risk Monitoring Modal */}
      {showRiskMonitoring && riskMonitoring && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-5xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800">Real-Time Risk Monitoring</h2>
                <button
                  onClick={() => setShowRiskMonitoring(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-blue-50 p-3 rounded">
                  <p className="font-semibold text-blue-800">Project Progress</p>
                  <p className="text-xl font-bold text-blue-600">{riskMonitoring.current_status?.overall_progress || 0}%</p>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <p className="font-semibold text-green-800">Current Week</p>
                  <p className="text-xl font-bold text-green-600">Week {riskMonitoring.current_status?.current_week || 0}</p>
                </div>
                <div className="bg-orange-50 p-3 rounded">
                  <p className="font-semibold text-orange-800">Budget Utilization</p>
                  <p className="text-xl font-bold text-orange-600">{riskMonitoring.current_status?.budget_utilization || 0}%</p>
                </div>
                <div className="bg-purple-50 p-3 rounded">
                  <p className="font-semibold text-purple-800">Health Status</p>
                  <p className="text-lg font-bold text-purple-600">{riskMonitoring.current_status?.health_status || 'Unknown'}</p>
                </div>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Risk Alerts */}
              {riskMonitoring.risk_alerts && riskMonitoring.risk_alerts.length > 0 && (
                <div className="bg-white border rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                    <AlertTriangle className="h-5 w-5 mr-2" />
                    Active Risk Alerts
                  </h3>
                  <div className="space-y-3">
                    {riskMonitoring.risk_alerts.map((alert, idx) => (
                      <div key={idx} className={`p-3 rounded border-l-4 ${
                        alert.severity === 'High' ? 'bg-red-50 border-red-500' :
                        alert.severity === 'Medium' ? 'bg-yellow-50 border-yellow-500' :
                        'bg-blue-50 border-blue-500'
                      }`}>
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium text-gray-800">{alert.message}</p>
                            <p className="text-sm text-gray-600 mt-1">{alert.recommended_action}</p>
                          </div>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            alert.severity === 'High' ? 'bg-red-100 text-red-800' :
                            alert.severity === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {alert.severity}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Trend Analysis */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Trend Analysis
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-3 bg-gray-50 rounded">
                    <p className="text-sm text-gray-600">Budget Trend</p>
                    <p className="text-lg font-bold text-gray-800">{riskMonitoring.trend_analysis?.budget_trend || 'Unknown'}</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded">
                    <p className="text-sm text-gray-600">Schedule Trend</p>
                    <p className="text-lg font-bold text-gray-800">{riskMonitoring.trend_analysis?.schedule_trend || 'Unknown'}</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded">
                    <p className="text-sm text-gray-600">Scope Trend</p>
                    <p className="text-lg font-bold text-gray-800">{riskMonitoring.trend_analysis?.scope_trend || 'Unknown'}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enhancement 3 Modals */}

      {/* Detailed Budget Tracking Modal */}
      {showBudgetTracking && budgetTracking && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-7xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800">Detailed Budget Tracking</h2>
                <button
                  onClick={() => setShowBudgetTracking(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-blue-50 p-3 rounded">
                  <p className="font-semibold text-blue-800">Total Budget</p>
                  <p className="text-xl font-bold text-blue-600">${budgetTracking.budget_tracking?.overall_metrics?.total_budgeted?.toLocaleString() || 0}</p>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <p className="font-semibold text-green-800">Budget Utilization</p>
                  <p className="text-xl font-bold text-green-600">{budgetTracking.budget_tracking?.overall_metrics?.budget_utilization?.toFixed(1) || 0}%</p>
                </div>
                <div className="bg-orange-50 p-3 rounded">
                  <p className="font-semibold text-orange-800">Cost Performance</p>
                  <p className="text-xl font-bold text-orange-600">{budgetTracking.budget_tracking?.overall_metrics?.cost_performance_index || 1.0}</p>
                </div>
                <div className="bg-purple-50 p-3 rounded">
                  <p className="font-semibold text-purple-800">Budget Health</p>
                  <p className="text-lg font-bold text-purple-600">{budgetTracking.budget_tracking?.overall_metrics?.budget_health || 'Unknown'}</p>
                </div>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Task-Level Budget Breakdown */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Task-Level Budget Breakdown</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Week</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Task</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Budget</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Level</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phase</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {budgetTracking.budget_tracking?.task_level_budgets?.slice(0, 10).map((task, idx) => (
                        <tr key={idx}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Week {task.week}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{task.task_name}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${task.budgeted_amount?.toLocaleString() || 0}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              task.risk_level === 'High' ? 'bg-red-100 text-red-800' :
                              task.risk_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {task.risk_level}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{task.phase}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Budget Alerts */}
              {budgetTracking.budget_alerts && budgetTracking.budget_alerts.length > 0 && (
                <div className="bg-white border rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Budget Alerts</h3>
                  <div className="space-y-3">
                    {budgetTracking.budget_alerts.map((alert, idx) => (
                      <div key={idx} className={`p-3 rounded border-l-4 ${
                        alert.severity === 'High' ? 'bg-red-50 border-red-500' :
                        alert.severity === 'Medium' ? 'bg-yellow-50 border-yellow-500' :
                        'bg-blue-50 border-blue-500'
                      }`}>
                        <p className="font-medium text-gray-800">{alert.message}</p>
                        <p className="text-sm text-gray-600 mt-1">{alert.recommended_action}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Project Forecasting Modal */}
      {showProjectForecasting && projectForecasting && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-6xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800">Advanced Project Forecasting</h2>
                <button
                  onClick={() => setShowProjectForecasting(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-blue-50 p-3 rounded">
                  <p className="font-semibold text-blue-800">Success Score</p>
                  <p className="text-xl font-bold text-blue-600">{projectForecasting.overall_success_score || 0}%</p>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <p className="font-semibold text-green-800">On-Time Probability</p>
                  <p className="text-xl font-bold text-green-600">{projectForecasting.delivery_outcomes?.on_time_delivery || 0}%</p>
                </div>
                <div className="bg-orange-50 p-3 rounded">
                  <p className="font-semibold text-orange-800">Budget Compliance</p>
                  <p className="text-xl font-bold text-orange-600">{projectForecasting.delivery_outcomes?.budget_compliance || 0}%</p>
                </div>
                <div className="bg-purple-50 p-3 rounded">
                  <p className="font-semibold text-purple-800">Quality Achievement</p>
                  <p className="text-xl font-bold text-purple-600">{projectForecasting.delivery_outcomes?.quality_achievement || 0}%</p>
                </div>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Delivery Outcomes */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Delivery Outcomes Forecast</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">On-Time Delivery</span>
                      <span className="text-sm font-bold text-green-600">{projectForecasting.delivery_outcomes?.on_time_delivery || 0}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Budget Compliance</span>
                      <span className="text-sm font-bold text-blue-600">{projectForecasting.delivery_outcomes?.budget_compliance || 0}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Scope Completion</span>
                      <span className="text-sm font-bold text-purple-600">{projectForecasting.delivery_outcomes?.scope_completion || 0}%</span>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Quality Achievement</span>
                      <span className="text-sm font-bold text-orange-600">{projectForecasting.delivery_outcomes?.quality_achievement || 0}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Stakeholder Satisfaction</span>
                      <span className="text-sm font-bold text-indigo-600">{projectForecasting.delivery_outcomes?.stakeholder_satisfaction || 0}%</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Manufacturing Excellence Correlation */}
              {projectForecasting.manufacturing_excellence && (
                <div className="bg-white border rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Manufacturing Excellence Correlation</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-3 bg-blue-50 rounded">
                      <p className="text-sm text-blue-800">Correlation Strength</p>
                      <p className="text-xl font-bold text-blue-600">{projectForecasting.manufacturing_excellence.correlation_strength || 0}</p>
                    </div>
                    <div className="text-center p-3 bg-green-50 rounded">
                      <p className="text-sm text-green-800">Maintenance Potential</p>
                      <p className="text-xl font-bold text-green-600">{projectForecasting.manufacturing_excellence.maintenance_excellence_potential || 0}%</p>
                    </div>
                    <div className="text-center p-3 bg-orange-50 rounded">
                      <p className="text-sm text-orange-800">Manufacturing Readiness</p>
                      <p className="text-lg font-bold text-orange-600">{projectForecasting.manufacturing_excellence.manufacturing_readiness || 'Unknown'}</p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-700 mb-2">Excellence Pathway:</h4>
                    <ul className="space-y-1">
                      {projectForecasting.manufacturing_excellence.excellence_pathway?.map((step, idx) => (
                        <li key={idx} className="text-sm text-gray-600 flex items-start">
                          <span className="w-2 h-2 bg-blue-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                          {step}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Stakeholder Communications Modal */}
      {showStakeholderComms && stakeholderComms && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-5xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800">Stakeholder Communications</h2>
                <button
                  onClick={() => setShowStakeholderComms(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Executive Summary */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Executive Summary</h3>
                <div className="text-gray-700 whitespace-pre-wrap">
                  {stakeholderComms.executive_summary}
                </div>
              </div>

              {/* Stakeholder Messages */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Stakeholder-Specific Messages</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {stakeholderComms.stakeholder_messages && Object.entries(stakeholderComms.stakeholder_messages).map(([role, message]) => (
                    <div key={role} className="p-3 bg-gray-50 rounded">
                      <h4 className="font-medium text-gray-800 mb-2 capitalize">{role.replace('_', ' ')}</h4>
                      <p className="text-sm text-gray-600">{message}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Communication Schedule */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Communication Schedule</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-blue-50 rounded">
                    <p className="text-sm text-blue-800">Recommended Frequency</p>
                    <p className="text-lg font-bold text-blue-600">{stakeholderComms.recommended_frequency || 'Weekly'}</p>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded">
                    <p className="text-sm text-green-800">Next Communication</p>
                    <p className="text-lg font-bold text-green-600">
                      {stakeholderComms.next_communication_date ? 
                        new Date(stakeholderComms.next_communication_date).toLocaleDateString() : 
                        'TBD'
                      }
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Manufacturing Excellence Modal */}
      {showManufacturingExcellence && manufacturingExcellence && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-6xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800">Manufacturing Excellence Tracking</h2>
                <button
                  onClick={() => setShowManufacturingExcellence(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-blue-50 p-3 rounded">
                  <p className="font-semibold text-blue-800">Current Score</p>
                  <p className="text-xl font-bold text-blue-600">{manufacturingExcellence.maintenance_excellence?.current_score || 0}/5</p>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <p className="font-semibold text-green-800">ROI Percentage</p>
                  <p className="text-xl font-bold text-green-600">{manufacturingExcellence.roi_analysis?.roi_percentage || 0}%</p>
                </div>
                <div className="bg-orange-50 p-3 rounded">
                  <p className="font-semibold text-orange-800">Payback Period</p>
                  <p className="text-xl font-bold text-orange-600">{manufacturingExcellence.roi_analysis?.payback_period_months || 0} months</p>
                </div>
                <div className="bg-purple-50 p-3 rounded">
                  <p className="font-semibold text-purple-800">Business Case</p>
                  <p className="text-lg font-bold text-purple-600">{manufacturingExcellence.roi_analysis?.business_case_strength || 'Unknown'}</p>
                </div>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Performance Predictions */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Manufacturing Performance Predictions</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {manufacturingExcellence.performance_predictions && Object.entries(manufacturingExcellence.performance_predictions).map(([metric, value]) => (
                    <div key={metric} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <span className="text-sm font-medium text-gray-700 capitalize">{metric.replace(/_/g, ' ')}</span>
                      <span className="text-sm font-bold text-green-600">{value}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Manufacturing KPIs */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Manufacturing KPIs</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {manufacturingExcellence.manufacturing_kpis && Object.entries(manufacturingExcellence.manufacturing_kpis).map(([kpi, value]) => (
                    <div key={kpi} className="flex items-center justify-between p-3 bg-blue-50 rounded">
                      <span className="text-sm font-medium text-blue-700 capitalize">{kpi.replace(/_/g, ' ')}</span>
                      <span className="text-sm font-bold text-blue-600">{value}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* ROI Analysis */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">ROI Analysis</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-3 bg-green-50 rounded">
                    <p className="text-sm text-green-800">Annual Savings</p>
                    <p className="text-xl font-bold text-green-600">${manufacturingExcellence.roi_analysis?.estimated_annual_savings?.toLocaleString() || 0}</p>
                  </div>
                  <div className="text-center p-3 bg-blue-50 rounded">
                    <p className="text-sm text-blue-800">Investment</p>
                    <p className="text-xl font-bold text-blue-600">${manufacturingExcellence.roi_analysis?.implementation_investment?.toLocaleString() || 0}</p>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded">
                    <p className="text-sm text-purple-800">ROI</p>
                    <p className="text-xl font-bold text-purple-600">{manufacturingExcellence.roi_analysis?.roi_percentage || 0}%</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enhancement 4 Modals */}

      {/* Phase Intelligence Modal */}
      {showPhaseIntelligence && phaseIntelligence && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-6xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800">Phase Intelligence: {phaseIntelligence.phase_name}</h2>
                <button
                  onClick={() => setShowPhaseIntelligence(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-blue-50 p-3 rounded">
                  <p className="font-semibold text-blue-800">Phase Number</p>
                  <p className="text-xl font-bold text-blue-600">{phaseIntelligence.phase_number}/6</p>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <p className="font-semibold text-green-800">Success Probability</p>
                  <p className="text-xl font-bold text-green-600">{phaseIntelligence.phase_intelligence?.success_probability || 0}%</p>
                </div>
                <div className="bg-orange-50 p-3 rounded">
                  <p className="font-semibold text-orange-800">Duration</p>
                  <p className="text-xl font-bold text-orange-600">{phaseIntelligence.phase_intelligence?.typical_duration_weeks || 0} weeks</p>
                </div>
                <div className="bg-purple-50 p-3 rounded">
                  <p className="font-semibold text-purple-800">Budget %</p>
                  <p className="text-xl font-bold text-purple-600">{phaseIntelligence.phase_intelligence?.budget_percentage || 0}%</p>
                </div>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Key Activities */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Key Activities</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {phaseIntelligence.phase_intelligence?.key_activities?.map((activity, idx) => (
                    <div key={idx} className="flex items-center p-2 bg-blue-50 rounded">
                      <CheckCircle className="h-4 w-4 text-blue-600 mr-2" />
                      <span className="text-sm text-gray-700">{activity}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendations */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">AI Recommendations</h3>
                <div className="space-y-2">
                  {phaseIntelligence.phase_intelligence?.recommendations?.map((rec, idx) => (
                    <div key={idx} className="flex items-start p-3 bg-green-50 rounded">
                      <span className="inline-block w-5 h-5 bg-green-500 text-white rounded-full text-xs flex items-center justify-center mr-3 mt-0.5 flex-shrink-0">
                        {idx + 1}
                      </span>
                      <span className="text-sm text-gray-700">{rec}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Budget Recommendations */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Budget Recommendations</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-3 bg-blue-50 rounded">
                    <p className="text-sm text-blue-800">Recommended Budget</p>
                    <p className="text-xl font-bold text-blue-600">${phaseIntelligence.phase_intelligence?.budget_recommendations?.recommended_budget?.toLocaleString() || 0}</p>
                  </div>
                  <div className="text-center p-3 bg-yellow-50 rounded">
                    <p className="text-sm text-yellow-800">Risk Level</p>
                    <p className="text-xl font-bold text-yellow-600">{phaseIntelligence.phase_intelligence?.budget_recommendations?.risk_level || 'Unknown'}</p>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded">
                    <p className="text-sm text-purple-800">Contingency</p>
                    <p className="text-xl font-bold text-purple-600">{phaseIntelligence.phase_intelligence?.budget_recommendations?.contingency_percentage || 0}%</p>
                  </div>
                </div>
              </div>

              {/* Risks and Mitigations */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Risks and Mitigations</h3>
                <div className="space-y-3">
                  {phaseIntelligence.phase_intelligence?.risks_and_mitigations?.map((risk, idx) => (
                    <div key={idx} className="border-l-4 border-red-500 pl-4 py-2">
                      <p className="font-medium text-red-700">{risk.risk}</p>
                      <p className="text-sm text-gray-600 mt-1">{risk.mitigation}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Phase Progress Modal */}
      {showPhaseProgressModal && selectedPhaseForProgress && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800">Update Phase Progress: {selectedPhaseForProgress.phase_name}</h2>
                <button
                  onClick={() => setShowPhaseProgressModal(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              <form onSubmit={(e) => {
                e.preventDefault();
                if (phaseProgress.status === 'completed') {
                  completePhaseWithAnalysis(selectedProject.id, phaseProgress.phase_name, phaseProgress);
                } else {
                  updatePhaseProgress(selectedProject.id, phaseProgress.phase_name, phaseProgress);
                }
              }}>
                {/* Progress and Status */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Completion Percentage
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      value={phaseProgress.completion_percentage}
                      onChange={(e) => setPhaseProgress({...phaseProgress, completion_percentage: parseFloat(e.target.value)})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      value={phaseProgress.status}
                      onChange={(e) => setPhaseProgress({...phaseProgress, status: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="not_started">Not Started</option>
                      <option value="in_progress">In Progress</option>
                      <option value="completed">Completed</option>
                      <option value="failed">Failed</option>
                    </select>
                  </div>
                </div>

                {/* Success Status */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Success Status
                  </label>
                  <select
                    value={phaseProgress.success_status}
                    onChange={(e) => setPhaseProgress({...phaseProgress, success_status: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select Status</option>
                    <option value="successful">Successful</option>
                    <option value="partially_successful">Partially Successful</option>
                    <option value="failed">Failed</option>
                  </select>
                </div>

                {/* Success/Failure Reasons */}
                {phaseProgress.success_status === 'successful' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Success Reason
                    </label>
                    <textarea
                      value={phaseProgress.success_reason}
                      onChange={(e) => setPhaseProgress({...phaseProgress, success_reason: e.target.value})}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="What made this phase successful?"
                    />
                  </div>
                )}

                {phaseProgress.success_status === 'failed' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Failure Reason
                    </label>
                    <textarea
                      value={phaseProgress.failure_reason}
                      onChange={(e) => setPhaseProgress({...phaseProgress, failure_reason: e.target.value})}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="What caused this phase to fail?"
                    />
                  </div>
                )}

                {/* Lessons Learned */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Lessons Learned
                  </label>
                  <textarea
                    value={phaseProgress.lessons_learned}
                    onChange={(e) => setPhaseProgress({...phaseProgress, lessons_learned: e.target.value})}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="What did you learn from this phase?"
                  />
                </div>

                {/* Budget Spent */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Budget Spent ($)
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={phaseProgress.budget_spent}
                    onChange={(e) => setPhaseProgress({...phaseProgress, budget_spent: parseFloat(e.target.value) || 0})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Action Buttons */}
                <div className="flex justify-end space-x-4 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowPhaseProgressModal(false)}
                    className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className={`px-4 py-2 text-white rounded-md transition-colors ${
                      phaseProgress.status === 'completed' 
                        ? 'bg-green-600 hover:bg-green-700' 
                        : 'bg-blue-600 hover:bg-blue-700'
                    }`}
                  >
                    {phaseProgress.status === 'completed' ? 'Complete Phase with Analysis' : 'Update Progress'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Workflow Status Modal */}
      {showWorkflowStatus && workflowStatus && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-6xl max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800">Project Workflow Status</h2>
                <button
                  onClick={() => setShowWorkflowStatus(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-blue-50 p-3 rounded">
                  <p className="font-semibold text-blue-800">Overall Progress</p>
                  <p className="text-xl font-bold text-blue-600">{workflowStatus.workflow_status?.overall_progress || 0}%</p>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <p className="font-semibold text-green-800">Current Phase</p>
                  <p className="text-sm font-bold text-green-600">{workflowStatus.workflow_status?.current_phase || 'None'}</p>
                </div>
                <div className="bg-orange-50 p-3 rounded">
                  <p className="font-semibold text-orange-800">Budget Utilization</p>
                  <p className="text-xl font-bold text-orange-600">{workflowStatus.workflow_status?.budget_utilization || 0}%</p>
                </div>
                <div className="bg-purple-50 p-3 rounded">
                  <p className="font-semibold text-purple-800">Success Rate</p>
                  <p className="text-xl font-bold text-purple-600">{workflowStatus.workflow_status?.success_rate || 0}%</p>
                </div>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Phase Summary */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Phase Summary</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-3 bg-green-50 rounded">
                    <p className="text-sm text-green-800">Completed</p>
                    <p className="text-2xl font-bold text-green-600">{workflowStatus.workflow_status?.phase_summary?.completed_phases || 0}</p>
                  </div>
                  <div className="text-center p-3 bg-blue-50 rounded">
                    <p className="text-sm text-blue-800">In Progress</p>
                    <p className="text-2xl font-bold text-blue-600">{workflowStatus.workflow_status?.phase_summary?.in_progress_phases || 0}</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded">
                    <p className="text-sm text-gray-800">Not Started</p>
                    <p className="text-2xl font-bold text-gray-600">{workflowStatus.workflow_status?.phase_summary?.not_started_phases || 0}</p>
                  </div>
                  <div className="text-center p-3 bg-red-50 rounded">
                    <p className="text-sm text-red-800">Failed</p>
                    <p className="text-2xl font-bold text-red-600">{workflowStatus.workflow_status?.phase_summary?.failed_phases || 0}</p>
                  </div>
                </div>
              </div>

              {/* Phase Details */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Phase Details</h3>
                <div className="space-y-3">
                  {workflowStatus.workflow_status?.phases_detail?.map((phase, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <div className="flex items-center">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold mr-3 ${
                          phase.status === 'completed' ? 'bg-green-500' :
                          phase.status === 'in_progress' ? 'bg-blue-500' :
                          phase.status === 'failed' ? 'bg-red-500' :
                          'bg-gray-400'
                        }`}>
                          {idx + 1}
                        </div>
                        <div>
                          <p className="font-medium text-gray-800">{phase.phase_name}</p>
                          <p className="text-sm text-gray-600">{phase.completion_percentage || 0}% complete</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          phase.status === 'completed' ? 'bg-green-100 text-green-800' :
                          phase.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                          phase.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {phase.status?.replace('_', ' ')}
                        </span>
                        <p className="text-sm text-gray-600 mt-1">${phase.budget_spent || 0} spent</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* New Project Form Modal - Moved to main component level */}
      {showNewProjectForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Create New Project</h2>
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Project Name</label>
                <input
                  type="text"
                  value={newProjectData.name}
                  onChange={(e) => setNewProjectData({...newProjectData, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  placeholder="Enter project name"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  value={newProjectData.description}
                  onChange={(e) => setNewProjectData({...newProjectData, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  placeholder="Enter project description"
                  rows="3"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Target Completion Date</label>
                <input
                  type="date"
                  value={newProjectData.target_completion_date}
                  onChange={(e) => setNewProjectData({...newProjectData, target_completion_date: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Budget</label>
                <input
                  type="number"
                  value={newProjectData.budget}
                  onChange={(e) => setNewProjectData({...newProjectData, budget: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  placeholder="Enter budget amount"
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create Project'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowNewProjectForm(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Project Form Modal */}
      {showEditProjectForm && editingProject && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Edit Project</h2>
            <form onSubmit={handleUpdateProject} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Project Name</label>
                <input
                  type="text"
                  value={editProjectData.name}
                  onChange={(e) => setEditProjectData({...editProjectData, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter project name"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  value={editProjectData.description}
                  onChange={(e) => setEditProjectData({...editProjectData, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter project description"
                  rows="3"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Target Completion Date</label>
                <input
                  type="date"
                  value={editProjectData.target_completion_date}
                  onChange={(e) => setEditProjectData({...editProjectData, target_completion_date: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Budget</label>
                <input
                  type="number"
                  value={editProjectData.budget}
                  onChange={(e) => setEditProjectData({...editProjectData, budget: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter budget amount"
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Updating...' : 'Update Project'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowEditProjectForm(false);
                    setEditingProject(null);
                    setEditProjectData({
                      name: '',
                      description: '',
                      target_completion_date: '',
                      budget: '',
                      project_name: '',
                      client_organization: '',
                      objectives: [''],
                      scope: '',
                      total_budget: '',
                      estimated_end_date: ''
                    });
                  }}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;