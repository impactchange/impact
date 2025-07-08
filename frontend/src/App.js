import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

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

  // Assessment states
  const [assessmentData, setAssessmentData] = useState({
    project_name: '',
    change_management_maturity: { score: 3, notes: '' },
    communication_effectiveness: { score: 3, notes: '' },
    leadership_support: { score: 3, notes: '' },
    workforce_adaptability: { score: 3, notes: '' },
    resource_adequacy: { score: 3, notes: '' }
  });

  // Dashboard states
  const [dashboardMetrics, setDashboardMetrics] = useState({});
  const [assessments, setAssessments] = useState([]);
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    if (token) {
      fetchUserProfile();
      fetchDashboardData();
    }
  }, [token]);

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
      setProjects(projectsRes.data);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
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
      
      setToken(response.data.token);
      setUser(response.data.user);
      localStorage.setItem('token', response.data.token);
      
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

  const handleAssessmentSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/assessments`, assessmentData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('Assessment completed successfully! AI analysis has been generated.');
      setAssessmentData({
        project_name: '',
        change_management_maturity: { score: 3, notes: '' },
        communication_effectiveness: { score: 3, notes: '' },
        leadership_support: { score: 3, notes: '' },
        workforce_adaptability: { score: 3, notes: '' },
        resource_adequacy: { score: 3, notes: '' }
      });
      
      fetchDashboardData();
      setActiveTab('assessments');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit assessment');
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
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
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Assessments</h3>
        <p className="text-3xl font-bold text-green-600">{dashboardMetrics.total_assessments || 0}</p>
      </div>
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-2">Active Projects</h3>
        <p className="text-3xl font-bold text-blue-600">{dashboardMetrics.total_projects || 0}</p>
      </div>
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-2">Avg Readiness Score</h3>
        <p className="text-3xl font-bold text-purple-600">{dashboardMetrics.average_readiness_score || 0}/5</p>
      </div>
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-2">Success Probability</h3>
        <p className="text-3xl font-bold text-orange-600">{dashboardMetrics.average_success_probability || 0}%</p>
      </div>
    </div>
  );

  const renderAssessmentForm = () => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Change Readiness Assessment</h2>
      <p className="text-gray-600 mb-6">
        Evaluate your organization's readiness for change using our scientifically-backed assessment framework.
      </p>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleAssessmentSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Project Name</label>
          <input
            type="text"
            value={assessmentData.project_name}
            onChange={(e) => setAssessmentData({...assessmentData, project_name: e.target.value})}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
            required
          />
        </div>

        {Object.keys(assessmentData).filter(key => key !== 'project_name').map(dimension => (
          <div key={dimension} className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-800 capitalize">
              {dimension.replace(/_/g, ' ')}
            </h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Score (1 = Poor, 5 = Excellent)
              </label>
              <div className="flex space-x-2">
                {[1, 2, 3, 4, 5].map(score => (
                  <button
                    key={score}
                    type="button"
                    onClick={() => setAssessmentData({
                      ...assessmentData,
                      [dimension]: {...assessmentData[dimension], score}
                    })}
                    className={`w-12 h-12 rounded-full font-semibold ${
                      assessmentData[dimension].score === score
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {score}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Notes (Optional)</label>
              <textarea
                value={assessmentData[dimension].notes}
                onChange={(e) => setAssessmentData({
                  ...assessmentData,
                  [dimension]: {...assessmentData[dimension], notes: e.target.value}
                })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                rows="2"
                placeholder="Additional context or observations..."
              />
            </div>
          </div>
        ))}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 disabled:opacity-50 font-semibold"
        >
          {loading ? 'Analyzing with AI...' : 'Submit Assessment'}
        </button>
      </form>
    </div>
  );

  const renderAssessmentsList = () => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Assessment Results</h2>
      
      {assessments.length === 0 ? (
        <p className="text-gray-600">No assessments completed yet.</p>
      ) : (
        <div className="space-y-4">
          {assessments.map(assessment => (
            <div key={assessment.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-lg font-semibold text-gray-800">{assessment.project_name}</h3>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  assessment.overall_score >= 4 ? 'bg-green-100 text-green-800' :
                  assessment.overall_score >= 3 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {assessment.overall_score?.toFixed(1)}/5
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-600">Success Probability</p>
                  <p className="text-lg font-semibold text-purple-600">
                    {assessment.success_probability?.toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Date</p>
                  <p className="text-lg font-semibold text-gray-800">
                    {new Date(assessment.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>

              {assessment.ai_analysis && (
                <div className="mb-4">
                  <h4 className="font-semibold text-gray-800 mb-2">AI Analysis</h4>
                  <p className="text-gray-700 bg-gray-50 p-3 rounded">{assessment.ai_analysis}</p>
                </div>
              )}

              {assessment.recommendations && assessment.recommendations.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-2">Recommendations</h4>
                  <ul className="list-disc list-inside text-gray-700 space-y-1">
                    {assessment.recommendations.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderMainContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>
            {renderDashboard()}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">IMPACT Methodology Overview</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {['Identify', 'Measure', 'Plan', 'Act', 'Control', 'Transform'].map(phase => (
                  <div key={phase} className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600 mb-2">{phase.charAt(0)}</div>
                    <div className="text-sm text-gray-700">{phase}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      case 'assessment':
        return renderAssessmentForm();
      case 'assessments':
        return renderAssessmentsList();
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
                className={`px-4 py-2 rounded-lg font-medium ${
                  activeTab === 'dashboard' ? 'bg-green-600 text-white' : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActiveTab('assessment')}
                className={`px-4 py-2 rounded-lg font-medium ${
                  activeTab === 'assessment' ? 'bg-green-600 text-white' : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                New Assessment
              </button>
              <button
                onClick={() => setActiveTab('assessments')}
                className={`px-4 py-2 rounded-lg font-medium ${
                  activeTab === 'assessments' ? 'bg-green-600 text-white' : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Results
              </button>
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Welcome, {user.full_name}</span>
              <button
                onClick={logout}
                className="text-sm text-red-600 hover:text-red-800"
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
    </div>
  );
}

export default App;