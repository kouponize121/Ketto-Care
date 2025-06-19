import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  MessageCircle, 
  Send, 
  User, 
  Settings, 
  LogOut, 
  Shield, 
  Users, 
  Ticket, 
  Heart,
  Mail,
  Brain,
  Upload,
  FileText,
  Eye,
  Edit,
  Trash2,
  Plus,
  Download,
  CheckCircle,
  AlertCircle,
  Clock,
  Filter
} from 'lucide-react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// AuthContext
const AuthContext = React.createContext();

const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Edit Ticket Modal Component (Shared)
const EditTicketModal = ({ editingTicket, setEditingTicket, updateTicket }) => {
  const [formData, setFormData] = useState({
    status: '',
    admin_notes: ''
  });

  useEffect(() => {
    if (editingTicket) {
      setFormData({
        status: editingTicket.status || '',
        admin_notes: editingTicket.admin_notes || ''
      });
    }
  }, [editingTicket]);

  const handleSubmit = (e) => {
    e.preventDefault();
    updateTicket(editingTicket.id, formData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  if (!editingTicket) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Edit Ticket</h3>
          <button
            onClick={() => setEditingTicket(null)}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-2">Ticket Details</h4>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div><strong>ID:</strong> {editingTicket.id}</div>
            <div><strong>Employee:</strong> {editingTicket.user_name}</div>
            <div><strong>Email:</strong> {editingTicket.user_email}</div>
            <div><strong>Category:</strong> {editingTicket.category}</div>
            <div><strong>Severity:</strong> {editingTicket.severity}</div>
            <div><strong>Created:</strong> {new Date(editingTicket.created_at).toLocaleString()}</div>
          </div>
          <div className="mt-3">
            <strong>Summary:</strong> {editingTicket.summary}
          </div>
          <div className="mt-3">
            <strong>Description:</strong> {editingTicket.description}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Admin Notes</label>
            <textarea
              name="admin_notes"
              value={formData.admin_notes}
              onChange={handleChange}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              placeholder="Add your notes here..."
            />
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setEditingTicket(null)}
              className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition"
            >
              Update Ticket
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// CSV Upload Modal Component (Shared)
const CsvUploadModal = ({ showCsvUpload, setShowCsvUpload, uploadCsv }) => {
  const [csvContent, setCsvContent] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleFileUpload = (file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      setCsvContent(e.target.result);
    };
    reader.readAsText(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'text/csv') {
      handleFileUpload(file);
    } else {
      alert('Please upload a CSV file');
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!csvContent) {
      alert('Please upload a CSV file');
      return;
    }
    uploadCsv(csvContent);
  };

  if (!showCsvUpload) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Upload Users CSV</h3>
          <button
            onClick={() => setShowCsvUpload(false)}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-2">CSV Format Requirements</h4>
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-blue-800 mb-2">Required columns: <strong>name, email</strong></p>
            <p className="text-sm text-blue-800 mb-2">Optional columns: password, role, designation, business_unit, reporting_manager</p>
            <p className="text-sm text-blue-600">Example: name,email,password,role,designation,business_unit,reporting_manager</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition ${
              dragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300'
            }`}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onDragEnter={() => setDragActive(true)}
            onDragLeave={() => setDragActive(false)}
          >
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="hidden"
              id="csv-upload"
            />
            <label
              htmlFor="csv-upload"
              className="cursor-pointer text-gray-600 hover:text-indigo-600"
            >
              <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p className="text-lg font-medium">Drop CSV file here or click to browse</p>
              <p className="text-sm text-gray-500 mt-2">Supports .csv files</p>
            </label>
          </div>

          {csvContent && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">CSV Content Preview</label>
              <textarea
                value={csvContent.split('\n').slice(0, 10).join('\n')}
                readOnly
                rows={8}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-sm"
              />
              <p className="text-xs text-gray-500 mt-1">Showing first 10 lines...</p>
            </div>
          )}

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={() => setShowCsvUpload(false)}
              className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!csvContent}
              className="flex-1 bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition"
            >
              Upload CSV
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    if (token && userData) {
      setUser(JSON.parse(userData));
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token, user } = response.data;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setUser(user);
      
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Landing Page Component
const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Heart className="h-8 w-8 text-indigo-600" />
              <h1 className="text-2xl font-bold text-gray-900">Ketto Care</h1>
            </div>
            <div className="space-x-4">
              <button
                onClick={() => navigate('/login')}
                className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition font-medium"
              >
                Login
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Your Mental Wellness & Support Companion
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Ketto Care provides comprehensive employee support through our AI assistant CareAI, 
            helping you navigate workplace challenges, mental health concerns, and HR requests with empathy and care.
          </p>
          <div className="flex justify-center mb-12">
            <img 
              src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=600&h=400&fit=crop"
              alt="Workplace Wellness"
              className="rounded-lg shadow-xl"
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            How Ketto Care Supports You
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-indigo-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Brain className="h-8 w-8 text-indigo-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4">AI-Powered Support</h3>
              <p className="text-gray-600">
                CareAI provides 24/7 empathetic support for workplace concerns, mental health guidance, and instant assistance.
              </p>
              <img 
                src="https://images.pexels.com/photos/5711031/pexels-photo-5711031.jpeg?w=300&h=200&fit=crop"
                alt="Professional Support"
                className="rounded-lg mt-4 mx-auto"
              />
            </div>
            
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Shield className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4">Grievance Management</h3>
              <p className="text-gray-600">
                Safely report workplace issues with automatic escalation to HR and transparent tracking of your concerns.
              </p>
              <img 
                src="https://images.pexels.com/photos/6520081/pexels-photo-6520081.jpeg?w=300&h=200&fit=crop"
                alt="Support Conversation"
                className="rounded-lg mt-4 mx-auto"
              />
            </div>
            
            <div className="text-center">
              <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Heart className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4">Wellness Focus</h3>
              <p className="text-gray-600">
                Dedicated mental health support, wellness resources, and a judgment-free space to discuss your wellbeing.
              </p>
              <img 
                src="https://images.pexels.com/photos/8546652/pexels-photo-8546652.jpeg?w=300&h=200&fit=crop"
                alt="Employee Wellbeing"
                className="rounded-lg mt-4 mx-auto"
              />
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            How the Process Works
          </h2>
          
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="bg-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4 text-xl font-bold">1</div>
              <h3 className="font-semibold mb-2">Chat with CareAI</h3>
              <p className="text-gray-600 text-sm">Share your concerns or questions with our AI assistant in a safe, private environment.</p>
            </div>
            
            <div className="text-center">
              <div className="bg-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4 text-xl font-bold">2</div>
              <h3 className="font-semibold mb-2">AI Assessment</h3>
              <p className="text-gray-600 text-sm">CareAI evaluates your concern and provides immediate support or escalates if needed.</p>
            </div>
            
            <div className="text-center">
              <div className="bg-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4 text-xl font-bold">3</div>
              <h3 className="font-semibold mb-2">Ticket Creation</h3>
              <p className="text-gray-600 text-sm">If escalation is needed, a ticket is automatically created and sent to appropriate admins.</p>
            </div>
            
            <div className="text-center">
              <div className="bg-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4 text-xl font-bold">4</div>
              <h3 className="font-semibold mb-2">Resolution</h3>
              <p className="text-gray-600 text-sm">Track your ticket status and receive updates until your concern is fully resolved.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Privacy & Trust */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">
            Your Privacy & Trust Matter
          </h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <Shield className="h-12 w-12 text-indigo-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-4">Confidential & Secure</h3>
              <p className="text-gray-600">
                All conversations are encrypted and confidential. Your personal information is protected with enterprise-grade security.
              </p>
            </div>
            <div>
              <Eye className="h-12 w-12 text-indigo-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-4">Transparent Process</h3>
              <p className="text-gray-600">
                Track every step of your ticket journey. Know exactly who has access to your information and when actions are taken.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-indigo-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">
            Ready to Get Support?
          </h2>
          <p className="text-xl text-indigo-100 mb-8">
            Join thousands of employees who have found comfort and resolution through Ketto Care.
          </p>
          <button
            onClick={() => navigate('/login/employee')}
            className="bg-white text-indigo-600 px-8 py-4 rounded-lg text-lg font-semibold hover:bg-gray-100 transition"
          >
            Start Chatting with CareAI
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Heart className="h-6 w-6 text-indigo-400" />
              <span className="text-lg font-semibold">Ketto Care</span>
            </div>
            <p className="text-gray-400">© 2025 Ketto Care. Supporting employee wellbeing.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Employee Registration Component
const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    designation: '',
    bu: '',
    reporting_manager: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post(`${API}/auth/register`, {
        ...formData,
        role: 'employee'
      });
      
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error) {
      console.error('Registration failed:', error);
      setError(error.response?.data?.detail || 'Registration failed. Please try again.');
    }
    setLoading(false);
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-xl shadow-xl w-full max-w-md text-center">
          <div className="text-green-600 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Registration Successful!</h1>
          <p className="text-gray-600 mb-4">Your employee account has been created successfully.</p>
          <p className="text-sm text-gray-500">Redirecting to login page...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12">
      <div className="bg-white p-8 rounded-xl shadow-xl w-full max-w-md">
        <div className="text-center mb-8">
          <Heart className="h-12 w-12 text-indigo-600 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900">
            Create Employee Account
          </h1>
          <p className="text-gray-600 mt-2">Join Ketto Care for workplace support</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Full Name *
            </label>
            <input
              type="text"
              name="name"
              required
              value={formData.name}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter your full name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email Address *
            </label>
            <input
              type="email"
              name="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter your work email"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password *
            </label>
            <input
              type="password"
              name="password"
              required
              value={formData.password}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Create a password"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Designation
            </label>
            <input
              type="text"
              name="designation"
              value={formData.designation}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Software Engineer, HR Manager, etc."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Business Unit
            </label>
            <input
              type="text"
              name="bu"
              value={formData.bu}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Engineering, HR, Sales, etc."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reporting Manager
            </label>
            <input
              type="text"
              name="reporting_manager"
              value={formData.reporting_manager}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Manager's name"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 focus:ring-4 focus:ring-indigo-200 disabled:opacity-50 transition font-medium"
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600 text-sm">
            Already have an account?{' '}
            <button
              onClick={() => navigate('/login')}
              className="text-indigo-600 hover:text-indigo-500 font-medium"
            >
              Sign In
            </button>
          </p>
        </div>

        <div className="mt-4 text-center">
          <button
            onClick={() => navigate('/')}
            className="text-gray-500 hover:text-gray-700 text-sm"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

// Login Component
const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Initialize admin user on first load
    axios.post(`${API}/init-admin`).catch(() => {});
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token, user } = response.data;
      
      // Store token and user data
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Auto-redirect based on user role
      if (user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/employee');
      }
    } catch (error) {
      console.error('Login failed:', error);
      setError('Invalid email or password. Please try again.');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-xl shadow-xl w-full max-w-md">
        <div className="text-center mb-8">
          <Heart className="h-12 w-12 text-indigo-600 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome to Ketto Care
          </h1>
          <p className="text-gray-600 mt-2">Sign in to access your dashboard</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter your email"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="Enter your password"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 focus:ring-4 focus:ring-indigo-200 disabled:opacity-50 transition font-medium"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600 text-sm">
            Don't have an account?{' '}
            <button
              onClick={() => navigate('/register')}
              className="text-indigo-600 hover:text-indigo-500 font-medium"
            >
              Create Employee Account
            </button>
          </p>
        </div>

        <div className="mt-4 text-center">
          <button
            onClick={() => navigate('/')}
            className="text-gray-500 hover:text-gray-700 text-sm"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
};

// Employee Dashboard
const EmployeeDashboard = () => {
  const { user, logout } = useAuth();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [tickets, setTickets] = useState([]);
  const [activeTab, setActiveTab] = useState('chat');
  const [chatLoading, setChatLoading] = useState(true);
  const [awaitingResolution, setAwaitingResolution] = useState(null); // {conversationId, messageId}
  const [editingTicket, setEditingTicket] = useState(null);
  const [showCsvUpload, setShowCsvUpload] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadTickets();
    loadChatHistory();
  }, [user.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadChatHistory = async () => {
    try {
      setChatLoading(true);
      const response = await axios.get(`${API}/chat/history/${user.id}`);
      const chatHistory = response.data;
      
      if (chatHistory.length === 0) {
        // Add welcome message only if no chat history
        setMessages([{
          id: 1,
          sender: 'ai',
          message: `Hello ${user.name}! I'm CareAI, your personal workplace wellness assistant. I'm here to help with any work-related concerns, mental health support, HR requests, or general workplace questions. How can I support you today?`,
          timestamp: new Date()
        }]);
      } else {
        // Convert chat history to frontend format
        const formattedMessages = chatHistory.map(msg => ({
          id: msg.id,
          sender: msg.sender,
          message: msg.message,
          timestamp: new Date(msg.timestamp),
          ticketCreated: msg.ticket_id ? true : false,
          ticketId: msg.ticket_id
        }));
        setMessages(formattedMessages);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
      // Add welcome message on error
      setMessages([{
        id: 1,
        sender: 'ai',
        message: `Hello ${user.name}! I'm CareAI, your personal workplace wellness assistant. I'm here to help with any work-related concerns, mental health support, HR requests, or general workplace questions. How can I support you today?`,
        timestamp: new Date()
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const loadTickets = async () => {
    try {
      const response = await axios.get(`${API}/tickets`);
      setTickets(response.data);
    } catch (error) {
      console.error('Failed to load tickets:', error);
    }
  };

  const handleResolution = async (conversationId, resolution) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/chat/resolution`, {
        conversation_id: conversationId,
        resolution: resolution // 'helpful' or 'need_help'
      });

      // Add system message with the response
      const systemMessage = {
        id: Date.now(),
        sender: 'ai',
        message: response.data.message,
        timestamp: new Date(),
        ticketCreated: response.data.ticket_created,
        ticketId: response.data.ticket_id
      };

      setMessages(prev => [...prev, systemMessage]);

      if (response.data.ticket_created) {
        loadTickets(); // Refresh tickets
      }
    } catch (error) {
      console.error('Resolution failed:', error);
      alert('Failed to process your response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const updateTicket = async (ticketId, updateData) => {
    try {
      await axios.put(`${API}/tickets/${ticketId}`, updateData);
      setEditingTicket(null);
      loadTickets();
      alert('Ticket updated successfully!');
    } catch (error) {
      console.error('Failed to update ticket:', error);
      alert('Failed to update ticket: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const markConversationReviewed = async (conversationId) => {
    try {
      await axios.put(`${API}/admin/ai-conversations/${conversationId}`, { admin_reviewed: true });
      loadChatHistory();
    } catch (error) {
      console.error('Failed to mark conversation as reviewed:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      message: newMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        message: newMessage,
        user_id: user.id
      });

      const aiMessage = {
        id: Date.now() + 1,
        sender: 'ai',
        message: response.data.response,
        timestamp: new Date(),
        ticketCreated: response.data.ticket_created,
        ticketId: response.data.ticket_id,
        showResolutionButtons: response.data.show_resolution_buttons,
        conversationId: response.data.conversation_id
      };

      setMessages(prev => [...prev, aiMessage]);

      if (response.data.ticket_created) {
        loadTickets(); // Refresh tickets
      }
    } catch (error) {
      console.error('Chat failed:', error);
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'ai',
        message: 'I apologize, but I\'m experiencing technical difficulties. Please try again or contact your HR team directly.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setNewMessage('');
    setLoading(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open': return 'bg-yellow-100 text-yellow-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-orange-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Heart className="h-8 w-8 text-indigo-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Ketto Care</h1>
                <p className="text-sm text-gray-600">Welcome back, {user.name}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setActiveTab('chat')}
                className={`px-4 py-2 rounded-lg transition ${
                  activeTab === 'chat' 
                    ? 'bg-indigo-600 text-white' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <MessageCircle className="h-4 w-4 inline mr-2" />
                Chat with CareAI
              </button>
              
              <button
                onClick={() => setActiveTab('tickets')}
                className={`px-4 py-2 rounded-lg transition ${
                  activeTab === 'tickets' 
                    ? 'bg-indigo-600 text-white' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Ticket className="h-4 w-4 inline mr-2" />
                My Tickets ({tickets.length})
              </button>
              
              <button
                onClick={logout}
                className="text-gray-600 hover:text-red-600 transition"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'chat' && (
          <div className="bg-white rounded-xl shadow-lg h-[600px] flex flex-col">
            {/* Chat Header */}
            <div className="p-6 border-b">
              <div className="flex items-center space-x-3">
                <div className="bg-indigo-100 rounded-full p-2">
                  <Brain className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">CareAI Assistant</h2>
                  <p className="text-sm text-gray-600">Here to support your workplace wellness</p>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {chatLoading ? (
                <div className="flex justify-center items-center h-full">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
                    <p className="mt-2 text-gray-600">Loading your conversation...</p>
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                          message.sender === 'user'
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="text-sm">{message.message}</p>
                        {message.ticketCreated && (
                          <div className="mt-2 p-2 bg-blue-50 rounded text-xs text-blue-800 border border-blue-200">
                            <Ticket className="h-3 w-3 inline mr-1" />
                            Ticket created: {message.ticketId}
                          </div>
                        )}
                        {message.showResolutionButtons && !loading && (
                          <div className="mt-3 flex space-x-2">
                            <button
                              onClick={() => handleResolution(message.conversationId, 'helpful')}
                              className="bg-green-600 text-white px-3 py-1 rounded text-xs hover:bg-green-700 transition"
                            >
                              This helps
                            </button>
                            <button
                              onClick={() => handleResolution(message.conversationId, 'need_help')}
                              className="bg-orange-600 text-white px-3 py-1 rounded text-xs hover:bg-orange-700 transition"
                            >
                              Still need help
                            </button>
                          </div>
                        )}
                        <p className="text-xs opacity-70 mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 rounded-lg px-4 py-3">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                </>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="p-6 border-t">
              <form onSubmit={sendMessage} className="flex space-x-3">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Share your concern or ask a question..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading || !newMessage.trim()}
                  className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition"
                >
                  <Send className="h-5 w-5" />
                </button>
              </form>
            </div>
          </div>
        )}

        {activeTab === 'tickets' && (
          <div className="bg-white rounded-xl shadow-lg">
            <div className="p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">My Support Tickets</h2>
              <p className="text-sm text-gray-600 mt-1">Track the status of your escalated concerns</p>
            </div>

            <div className="p-6">
              {tickets.length === 0 ? (
                <div className="text-center py-12">
                  <Ticket className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No tickets yet</h3>
                  <p className="text-gray-600">When CareAI escalates your concerns, tickets will appear here.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {tickets.map((ticket) => (
                    <div key={ticket.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(ticket.status)}`}>
                              {ticket.status.replace('_', ' ').toUpperCase()}
                            </span>
                            <span className="text-xs text-gray-500">
                              {ticket.category.toUpperCase()}
                            </span>
                            <span className={`text-xs font-medium ${getSeverityColor(ticket.severity)}`}>
                              {ticket.severity.toUpperCase()}
                            </span>
                          </div>
                          <h3 className="font-medium text-gray-900 mb-1">{ticket.summary}</h3>
                          <p className="text-sm text-gray-600 mb-2">{ticket.description}</p>
                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            <span>ID: {ticket.id}</span>
                            <span>Created: {new Date(ticket.created_at).toLocaleDateString()}</span>
                            <span>Updated: {new Date(ticket.updated_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <EditTicketModal 
              editingTicket={editingTicket}
              setEditingTicket={setEditingTicket}
              updateTicket={updateTicket}
            />
          </div>
        )}
      </main>
    </div>
  );
};

// Email Recipients Manager Component
const EmailRecipientsManager = () => {
  const [emailRecipients, setEmailRecipients] = useState({
    additional_recipients: [],
    excluded_admin_emails: []
  });
  const [additionalEmails, setAdditionalEmails] = useState('');
  const [excludedEmails, setExcludedEmails] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadEmailRecipients();
  }, []);

  const loadEmailRecipients = async () => {
    try {
      const response = await axios.get(`${API}/admin/email-recipients`);
      setEmailRecipients(response.data);
      
      // Convert arrays to comma-separated strings for display
      const additionalEmails = response.data.additional_recipients.map(r => r.email).join(', ');
      const excludedEmails = response.data.excluded_admin_emails.map(r => r.email).join(', ');
      
      setAdditionalEmails(additionalEmails);
      setExcludedEmails(excludedEmails);
    } catch (error) {
      console.error('Failed to load email recipients:', error);
    }
  };

  const saveEmailRecipients = async () => {
    setLoading(true);
    try {
      // Convert comma-separated strings to arrays
      const additionalArray = additionalEmails.split(',').map(email => email.trim()).filter(email => email);
      const excludedArray = excludedEmails.split(',').map(email => email.trim()).filter(email => email);

      await axios.post(`${API}/admin/email-recipients`, {
        additional_recipients: additionalArray,
        excluded_admin_emails: excludedArray
      });

      alert('Email recipients updated successfully!');
      loadEmailRecipients();
    } catch (error) {
      console.error('Failed to save email recipients:', error);
      alert('Failed to save email recipients: ' + (error.response?.data?.detail || 'Unknown error'));
    }
    setLoading(false);
  };

  return (
    <div>
      <h3 className="text-md font-semibold text-gray-900 mb-4">Email Recipients Management</h3>
      
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h4 className="text-sm font-medium text-blue-800 mb-2">How Email Notifications Work:</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• <strong>Automatic:</strong> All admin users receive ticket notifications</li>
          <li>• <strong>Additional Recipients:</strong> Extra emails that will also receive notifications</li>
          <li>• <strong>Excluded Admins:</strong> Admin users who should NOT receive notifications</li>
          <li>• <strong>Employee:</strong> The employee who created the ticket is automatically CC'd</li>
        </ul>
      </div>

      <div className="space-y-6">
        {/* Additional Recipients */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Additional Email Recipients
          </label>
          <p className="text-xs text-gray-500 mb-2">
            Add extra email addresses that should receive ticket notifications (e.g., external consultants, managers). 
            Separate multiple emails with commas.
          </p>
          <textarea
            value={additionalEmails}
            onChange={(e) => setAdditionalEmails(e.target.value)}
            placeholder="hr.consultant@external.com, manager@company.com, support@vendor.com"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            rows="3"
          />
          {emailRecipients.additional_recipients.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-600">Current additional recipients:</p>
              <div className="flex flex-wrap gap-2 mt-1">
                {emailRecipients.additional_recipients.map((recipient, index) => (
                  <span key={index} className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                    {recipient.email}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Excluded Admin Emails */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Excluded Admin Users
          </label>
          <p className="text-xs text-gray-500 mb-2">
            Specify admin users who should NOT receive email notifications. 
            Separate multiple emails with commas.
          </p>
          <textarea
            value={excludedEmails}
            onChange={(e) => setExcludedEmails(e.target.value)}
            placeholder="admin2@company.com, temp.admin@company.com"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            rows="2"
          />
          {emailRecipients.excluded_admin_emails.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-600">Currently excluded admin emails:</p>
              <div className="flex flex-wrap gap-2 mt-1">
                {emailRecipients.excluded_admin_emails.map((recipient, index) => (
                  <span key={index} className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs">
                    {recipient.email}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={saveEmailRecipients}
            disabled={loading}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 transition"
          >
            {loading ? 'Saving...' : 'Save Email Recipients'}
          </button>
          
          <button
            onClick={loadEmailRecipients}
            className="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition"
          >
            Reset Changes
          </button>
        </div>

        {/* Current Admin Users Display */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-800 mb-2">Current Admin Users (Auto-included unless excluded):</h4>
          <AdminUsersList />
        </div>
      </div>
    </div>
  );
};

// Component to display and manage current admin users
const AdminUsersList = () => {
  const [adminUsers, setAdminUsers] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingAdmin, setEditingAdmin] = useState(null);

  useEffect(() => {
    loadAdminUsers();
  }, []);

  const loadAdminUsers = async () => {
    try {
      const response = await axios.get(`${API}/admin/users`);
      const admins = response.data.filter(user => user.role === 'admin');
      setAdminUsers(admins);
    } catch (error) {
      console.error('Failed to load admin users:', error);
    }
  };

  const deleteAdminUser = async (userId) => {
    if (!confirm('Are you sure you want to delete this admin user?')) return;
    
    try {
      await axios.delete(`${API}/admin/users/${userId}`);
      alert('Admin user deleted successfully!');
      loadAdminUsers();
    } catch (error) {
      alert('Failed to delete admin user: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const handleEditAdmin = (admin) => {
    setEditingAdmin(admin);
    setShowAddModal(true);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-medium text-gray-800">Current Admin Users (Auto-included unless excluded):</h4>
        <button
          onClick={() => {
            setEditingAdmin(null);
            setShowAddModal(true);
          }}
          className="bg-indigo-600 text-white px-3 py-1 rounded text-xs hover:bg-indigo-700 transition"
        >
          + Add Admin User
        </button>
      </div>

      {adminUsers.length === 0 ? (
        <div className="text-gray-500 text-xs">No admin users found</div>
      ) : (
        <div className="space-y-2">
          {adminUsers.map((admin) => (
            <div key={admin.id} className="flex items-center justify-between bg-white border rounded-lg p-3">
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <span className="bg-indigo-100 text-indigo-800 px-2 py-1 rounded text-xs font-medium">
                    ADMIN
                  </span>
                  <div>
                    <div className="text-sm font-medium text-gray-900">{admin.name}</div>
                    <div className="text-xs text-gray-500">{admin.email}</div>
                    {admin.designation && (
                      <div className="text-xs text-gray-400">{admin.designation}</div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleEditAdmin(admin)}
                  className="bg-yellow-100 text-yellow-700 px-2 py-1 rounded text-xs hover:bg-yellow-200 transition"
                >
                  Edit
                </button>
                <button
                  onClick={() => deleteAdminUser(admin.id)}
                  className="bg-red-100 text-red-700 px-2 py-1 rounded text-xs hover:bg-red-200 transition"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit Admin Modal */}
      {showAddModal && (
        <AdminUserModal
          admin={editingAdmin}
          onClose={() => {
            setShowAddModal(false);
            setEditingAdmin(null);
          }}
          onSave={() => {
            setShowAddModal(false);
            setEditingAdmin(null);
            loadAdminUsers();
          }}
        />
      )}
    </div>
  );
};

// Admin User Add/Edit Modal
const AdminUserModal = ({ admin, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: admin?.name || '',
    email: admin?.email || '',
    designation: admin?.designation || '',
    bu: admin?.bu || '',
    reporting_manager: admin?.reporting_manager || '',
    password: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const submitData = {
        ...formData,
        role: 'admin'
      };

      // Remove password if editing and password is empty
      if (admin && !formData.password) {
        delete submitData.password;
      }

      if (admin) {
        // Edit existing admin
        await axios.put(`${API}/admin/users/${admin.id}`, submitData);
        alert('Admin user updated successfully!');
      } else {
        // Create new admin
        if (!formData.password) {
          alert('Password is required for new admin users');
          setLoading(false);
          return;
        }
        await axios.post(`${API}/admin/users`, submitData);
        alert('Admin user created successfully!');
      }
      
      onSave();
    } catch (error) {
      alert('Failed to save admin user: ' + (error.response?.data?.detail || 'Unknown error'));
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">
            {admin ? 'Edit Admin User' : 'Add New Admin User'}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Full Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email Address *
            </label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500"
              placeholder="john.doe@company.com"
              disabled={admin ? true : false} // Email cannot be changed for existing users
            />
            {admin && (
              <p className="text-xs text-gray-500 mt-1">Email cannot be changed for existing users</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Designation
            </label>
            <input
              type="text"
              value={formData.designation}
              onChange={(e) => setFormData({...formData, designation: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500"
              placeholder="HR Manager, IT Admin, etc."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Business Unit
            </label>
            <input
              type="text"
              value={formData.bu}
              onChange={(e) => setFormData({...formData, bu: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500"
              placeholder="HR, IT, Operations, etc."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password {admin ? '(leave blank to keep current)' : '*'}
            </label>
            <input
              type="password"
              required={!admin}
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500"
              placeholder={admin ? "Leave blank to keep current password" : "Enter password"}
            />
          </div>

          <div className="flex items-center justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
            >
              {loading ? 'Saving...' : (admin ? 'Update Admin' : 'Create Admin')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Admin Dashboard
const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('tickets');
  const [tickets, setTickets] = useState([]);
  const [users, setUsers] = useState([]);
  const [emailConfig, setEmailConfig] = useState({});
  const [gptConfig, setGptConfig] = useState({});
  const [emailTemplates, setEmailTemplates] = useState([]);
  const [aiConversations, setAiConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [showCsvUpload, setShowCsvUpload] = useState(false);
  const [editingTicket, setEditingTicket] = useState(null);
  const [showEmailTemplate, setShowEmailTemplate] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      console.log('Loading admin data...');
      const [ticketsRes, usersRes, emailRes, gptRes, templatesRes, conversationsRes] = await Promise.all([
        axios.get(`${API}/admin/tickets`),
        axios.get(`${API}/admin/users`),
        axios.get(`${API}/admin/email-config`),
        axios.get(`${API}/admin/gpt-config`),
        axios.get(`${API}/admin/email-templates`),
        axios.get(`${API}/admin/ai-conversations`)
      ]);
      
      console.log('Tickets loaded:', ticketsRes.data.length);
      console.log('Users loaded:', usersRes.data.length);
      
      setTickets(ticketsRes.data || []);
      setUsers(usersRes.data || []);
      setEmailConfig(emailRes.data || {});
      setGptConfig(gptRes.data || {});
      setEmailTemplates(templatesRes.data || []);
      setAiConversations(conversationsRes.data || []);
    } catch (error) {
      console.error('Failed to load admin data:', error);
      alert('Failed to load admin data. Please refresh the page.');
    }
  };

  const updateTicketStatus = async (ticketId, status) => {
    try {
      await axios.put(`${API}/admin/tickets/${ticketId}`, { status });
      loadData();
    } catch (error) {
      console.error('Failed to update ticket:', error);
    }
  };

  const createUser = async (userData) => {
    try {
      await axios.post(`${API}/admin/users`, userData);
      setShowCreateUser(false);
      loadData();
      alert('User created successfully!');
    } catch (error) {
      console.error('Failed to create user:', error);
      alert('Failed to create user: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const updateUser = async (userId, userData) => {
    try {
      await axios.put(`${API}/admin/users/${userId}`, userData);
      setEditingUser(null);
      loadData();
      alert('User updated successfully!');
    } catch (error) {
      console.error('Failed to update user:', error);
      alert('Failed to update user: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const updateTicket = async (ticketId, updateData) => {
    try {
      await axios.put(`${API}/admin/tickets/${ticketId}`, updateData);
      setEditingTicket(null);
      loadData();
      alert('Ticket updated successfully!');
    } catch (error) {
      console.error('Failed to update ticket:', error);
      alert('Failed to update ticket: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const markConversationReviewed = async (conversationId) => {
    try {
      await axios.put(`${API}/admin/ai-conversations/${conversationId}`, { admin_reviewed: true });
      loadData();
    } catch (error) {
      console.error('Failed to mark conversation as reviewed:', error);
    }
  };

  const uploadCsv = async (csvContent) => {
    try {
      const base64Content = btoa(csvContent);
      const response = await axios.post(`${API}/admin/upload-users`, base64Content, {
        headers: { 'Content-Type': 'application/json' }
      });
      setShowCsvUpload(false);
      loadData();
      alert(`CSV uploaded successfully! ${response.data.message}`);
    } catch (error) {
      console.error('Failed to upload CSV:', error);
      alert('Failed to upload CSV: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const deleteUser = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await axios.delete(`${API}/admin/users/${userId}`);
        loadData();
        alert('User deleted successfully!');
      } catch (error) {
        console.error('Failed to delete user:', error);
        alert('Failed to delete user');
      }
    }
  };

  const saveEmailConfig = async (config) => {
    try {
      await axios.post(`${API}/admin/email-config`, config);
      alert('Email configuration saved successfully!');
    } catch (error) {
      console.error('Failed to save email config:', error);
      alert('Failed to save email configuration');
    }
  };

  const saveGptConfig = async (config) => {
    try {
      await axios.post(`${API}/admin/gpt-config`, config);
      alert('GPT configuration saved and tested successfully!');
      loadData();
    } catch (error) {
      console.error('Failed to save GPT config:', error);
      alert('Failed to save GPT configuration: ' + error.response?.data?.detail);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open': return 'bg-yellow-100 text-yellow-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-orange-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  // Create User Modal Component
  const CreateUserModal = () => {
    const [formData, setFormData] = useState({
      name: '',
      email: '',
      password: '',
      role: 'employee',
      designation: '',
      business_unit: '',
      reporting_manager: ''
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      createUser(formData);
    };

    const handleChange = (e) => {
      setFormData({
        ...formData,
        [e.target.name]: e.target.value
      });
    };

    if (!showCreateUser) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Create New User</h3>
            <button
              onClick={() => setShowCreateUser(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="employee">Employee</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Designation</label>
              <input
                type="text"
                name="designation"
                value={formData.designation}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Business Unit</label>
              <input
                type="text"
                name="business_unit"
                value={formData.business_unit}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Reporting Manager</label>
              <input
                type="text"
                name="reporting_manager"
                value={formData.reporting_manager}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={() => setShowCreateUser(false)}
                className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition"
              >
                Create User
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  // Edit User Modal Component
  const EditUserModal = () => {
    const [formData, setFormData] = useState({
      name: '',
      role: 'employee',
      designation: '',
      business_unit: '',
      reporting_manager: '',
      password: '',
      confirmPassword: ''
    });

    // Initialize form data when editing user changes
    useEffect(() => {
      if (editingUser) {
        setFormData({
          name: editingUser.name || '',
          role: editingUser.role || 'employee',
          designation: editingUser.designation || '',
          business_unit: editingUser.business_unit || '',
          reporting_manager: editingUser.reporting_manager || '',
          password: '',
          confirmPassword: ''
        });
      }
    }, [editingUser]);

    const handleSubmit = (e) => {
      e.preventDefault();
      
      // Validate password confirmation if password is being changed
      if (formData.password && formData.password !== formData.confirmPassword) {
        alert('Passwords do not match');
        return;
      }

      // Prepare update data (exclude confirmPassword and empty password)
      const updateData = {
        name: formData.name,
        role: formData.role,
        designation: formData.designation,
        business_unit: formData.business_unit,
        reporting_manager: formData.reporting_manager
      };

      // Only include password if it's being changed
      if (formData.password) {
        updateData.password = formData.password;
      }

      updateTicket(editingUser.id, updateData);
    };

    const handleChange = (e) => {
      setFormData({
        ...formData,
        [e.target.name]: e.target.value
      });
    };

    if (!editingUser) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Edit User</h3>
            <button
              onClick={() => setEditingUser(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email (Read-only)</label>
              <input
                type="email"
                value={editingUser.email}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-600"
                disabled
              />
              <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="employee">Employee</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Designation</label>
              <input
                type="text"
                name="designation"
                value={formData.designation}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Business Unit</label>
              <input
                type="text"
                name="business_unit"
                value={formData.business_unit}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Reporting Manager</label>
              <input
                type="text"
                name="reporting_manager"
                value={formData.reporting_manager}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Reset Password (Optional)</h4>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  placeholder="Leave blank to keep current password"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  placeholder="Confirm new password"
                />
              </div>
            </div>

            <div className="flex space-x-3 pt-4">
              <button
                type="button"
                onClick={() => setEditingUser(null)}
                className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition"
              >
                Update User
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Shield className="h-8 w-8 text-indigo-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Admin Dashboard</h1>
                <p className="text-sm text-gray-600">Ketto Care Management</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Welcome, {user.name}</span>
              <button
                onClick={logout}
                className="text-gray-600 hover:text-red-600 transition"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'tickets', label: 'Tickets', icon: Ticket },
              { id: 'ai-conversations', label: 'AI Conversations', icon: MessageCircle },
              { id: 'users', label: 'Users', icon: Users },
              { id: 'email', label: 'Email Config', icon: Mail },
              { id: 'gpt', label: 'AI Config', icon: Brain }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-2 border-b-2 transition ${
                  activeTab === tab.id
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'tickets' && (
          <div className="bg-white rounded-xl shadow-lg">
            <div className="p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">Support Tickets</h2>
              <p className="text-sm text-gray-600 mt-1">Manage and respond to employee concerns</p>
            </div>

            <div className="p-6">
              {tickets.length === 0 ? (
                <div className="text-center py-12">
                  <Ticket className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No tickets</h3>
                  <p className="text-gray-600">All employee concerns will appear here.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {tickets.map((ticket) => (
                    <div key={ticket.id} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(ticket.status)}`}>
                              {ticket.status.replace('_', ' ').toUpperCase()}
                            </span>
                            <span className="text-xs text-gray-500">
                              {ticket.category.toUpperCase()}
                            </span>
                            <span className={`text-xs font-medium ${getSeverityColor(ticket.severity)}`}>
                              {ticket.severity.toUpperCase()}
                            </span>
                          </div>
                          <h3 className="font-medium text-gray-900 mb-2">{ticket.summary}</h3>
                          <p className="text-sm text-gray-600 mb-3">{ticket.description}</p>
                          <div className="flex items-center space-x-4 text-xs text-gray-500 mb-3">
                            <span>Employee: {ticket.user_name} ({ticket.user_email})</span>
                            <span>ID: {ticket.id}</span>
                            <span>Created: {new Date(ticket.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        <select
                          value={ticket.status}
                          onChange={(e) => updateTicketStatus(ticket.id, e.target.value)}
                          className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-indigo-500"
                        >
                          <option value="open">Open</option>
                          <option value="in_progress">In Progress</option>
                          <option value="resolved">Resolved</option>
                        </select>
                        
                        <button 
                          onClick={() => setEditingTicket(ticket)}
                          className="text-blue-600 hover:text-blue-700 text-sm"
                        >
                          Add Note
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <EditTicketModal 
              editingTicket={editingTicket}
              setEditingTicket={setEditingTicket}
              updateTicket={updateTicket}
            />
          </div>
        )}

        {activeTab === 'ai-conversations' && (
          <div className="bg-white rounded-xl shadow-lg">
            <div className="p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">AI Conversations</h2>
              <p className="text-sm text-gray-600 mt-1">Track all employee interactions with CareAI</p>
            </div>

            <div className="p-6">
              {aiConversations.length === 0 ? (
                <div className="text-center py-12">
                  <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No AI conversations</h3>
                  <p className="text-gray-600">Employee conversations with CareAI will appear here.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {aiConversations.map((conversation) => (
                    <div key={conversation.id} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              conversation.resolution_status === 'resolved' 
                                ? 'bg-green-100 text-green-800'
                                : conversation.resolution_status === 'escalated'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {conversation.resolution_status.toUpperCase()}
                            </span>
                            {conversation.ticket_id && (
                              <span className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                                Ticket: {conversation.ticket_id}
                              </span>
                            )}
                            {!conversation.admin_reviewed && (
                              <span className="text-xs text-red-600 bg-red-50 px-2 py-1 rounded">
                                NEW
                              </span>
                            )}
                          </div>
                          <h3 className="font-medium text-gray-900 mb-2">
                            {conversation.user_name} ({conversation.user_email})
                          </h3>
                          <div className="space-y-2 text-sm">
                            <div>
                              <strong className="text-gray-700">Initial Concern:</strong>
                              <p className="text-gray-600 mt-1">{conversation.initial_concern}</p>
                            </div>
                            <div>
                              <strong className="text-gray-700">AI Solution:</strong>
                              <p className="text-gray-600 mt-1">{conversation.ai_solution_provided}</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-4 text-xs text-gray-500 mt-3">
                            <span>ID: {conversation.id}</span>
                            <span>Created: {new Date(conversation.created_at).toLocaleDateString()}</span>
                            <span>Updated: {new Date(conversation.updated_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        {!conversation.admin_reviewed && (
                          <button
                            onClick={() => markConversationReviewed(conversation.id)}
                            className="text-indigo-600 hover:text-indigo-700 text-sm bg-indigo-50 px-3 py-1 rounded"
                          >
                            Mark as Reviewed
                          </button>
                        )}
                        
                        {conversation.ticket_id && (
                          <button
                            onClick={() => setActiveTab('tickets')}
                            className="text-blue-600 hover:text-blue-700 text-sm"
                          >
                            View Ticket
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'ai-conversations' && (
          <div className="bg-white rounded-xl shadow-lg">
            <div className="p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">AI Conversations</h2>
              <p className="text-sm text-gray-600 mt-1">Track all employee interactions with CareAI</p>
            </div>

            <div className="p-6">
              {aiConversations.length === 0 ? (
                <div className="text-center py-12">
                  <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No AI conversations</h3>
                  <p className="text-gray-600">Employee conversations with CareAI will appear here.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {aiConversations.map((conversation) => (
                    <div key={conversation.id} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              conversation.resolution_status === 'resolved' 
                                ? 'bg-green-100 text-green-800'
                                : conversation.resolution_status === 'escalated'
                                ? 'bg-blue-100 text-blue-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {conversation.resolution_status.toUpperCase()}
                            </span>
                            {conversation.ticket_id && (
                              <span className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                                Ticket: {conversation.ticket_id}
                              </span>
                            )}
                            {!conversation.admin_reviewed && (
                              <span className="text-xs text-red-600 bg-red-50 px-2 py-1 rounded">
                                NEW
                              </span>
                            )}
                          </div>
                          <h3 className="font-medium text-gray-900 mb-2">
                            {conversation.user_name} ({conversation.user_email})
                          </h3>
                          <div className="space-y-2 text-sm">
                            <div>
                              <strong className="text-gray-700">Initial Concern:</strong>
                              <p className="text-gray-600 mt-1">{conversation.initial_concern}</p>
                            </div>
                            <div>
                              <strong className="text-gray-700">AI Solution:</strong>
                              <p className="text-gray-600 mt-1">{conversation.ai_solution_provided}</p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-4 text-xs text-gray-500 mt-3">
                            <span>ID: {conversation.id}</span>
                            <span>Created: {new Date(conversation.created_at).toLocaleDateString()}</span>
                            <span>Updated: {new Date(conversation.updated_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        {!conversation.admin_reviewed && (
                          <button
                            onClick={() => markConversationReviewed(conversation.id)}
                            className="text-indigo-600 hover:text-indigo-700 text-sm bg-indigo-50 px-3 py-1 rounded"
                          >
                            Mark as Reviewed
                          </button>
                        )}
                        
                        {conversation.ticket_id && (
                          <button
                            onClick={() => setActiveTab('tickets')}
                            className="text-blue-600 hover:text-blue-700 text-sm"
                          >
                            View Ticket
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="bg-white rounded-xl shadow-lg">
            <div className="p-6 border-b flex justify-between items-center">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">User Management</h2>
                <p className="text-sm text-gray-600 mt-1">Manage employee accounts</p>
              </div>
              <div className="flex space-x-3">
                <button
                  className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
                  onClick={() => setShowCreateUser(true)}
                >
                  <Plus className="h-4 w-4 inline mr-2" />
                  Add User
                </button>
                <button
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
                  onClick={() => setShowCsvUpload(true)}
                >
                  <Upload className="h-4 w-4 inline mr-2" />
                  Upload CSV
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Department
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{user.name}</div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.business_unit || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <button 
                          className="text-indigo-600 hover:text-indigo-900"
                          onClick={() => setEditingUser(user)}
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => deleteUser(user.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <CreateUserModal />
            <EditUserModal />
            <CsvUploadModal 
              showCsvUpload={showCsvUpload}
              setShowCsvUpload={setShowCsvUpload}
              uploadCsv={uploadCsv}
            />
          </div>
        )}

        {activeTab === 'email' && (
          <div className="bg-white rounded-xl shadow-lg">
            <div className="p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">Email Configuration</h2>
              <p className="text-sm text-gray-600 mt-1">Configure SMTP settings and notification recipients</p>
            </div>

            <div className="p-6 space-y-8">
              {/* SMTP Configuration */}
              <div>
                <h3 className="text-md font-semibold text-gray-900 mb-4">SMTP Settings</h3>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    const config = {
                      smtp_server: formData.get('smtp_server'),
                      smtp_port: parseInt(formData.get('smtp_port')),
                      smtp_username: formData.get('smtp_username'),
                      smtp_password: formData.get('smtp_password')
                    };
                    saveEmailConfig(config);
                  }}
                  className="space-y-6"
                >
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        SMTP Server
                      </label>
                      <input
                        type="text"
                        name="smtp_server"
                        defaultValue={emailConfig.smtp_server || ''}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                        placeholder="smtp.gmail.com"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        SMTP Port
                      </label>
                      <input
                        type="number"
                        name="smtp_port"
                        defaultValue={emailConfig.smtp_port || ''}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                        placeholder="587"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Username
                      </label>
                      <input
                        type="email"
                        name="smtp_username"
                        defaultValue={emailConfig.smtp_username || ''}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                        placeholder="your-email@gmail.com"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Password
                      </label>
                      <input
                        type="password"
                        name="smtp_password"
                        defaultValue={emailConfig.smtp_password || ''}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                        placeholder="App Password"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition"
                  >
                    Save SMTP Settings
                  </button>
                </form>
              </div>

              {/* Email Recipients Management */}
              <div className="border-t pt-8">
                <EmailRecipientsManager />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'gpt' && (
          <div className="bg-white rounded-xl shadow-lg">
            <div className="p-6 border-b">
              <h2 className="text-lg font-semibold text-gray-900">AI Configuration</h2>
              <p className="text-sm text-gray-600 mt-1">Configure OpenAI GPT-4 API settings</p>
            </div>

            <div className="p-6">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  const formData = new FormData(e.target);
                  const config = {
                    api_key: formData.get('api_key')
                  };
                  saveGptConfig(config);
                }}
                className="space-y-6"
              >
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    name="api_key"
                    defaultValue={gptConfig.api_key || ''}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    placeholder="sk-..."
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">OpenAI Platform</a>
                  </p>
                </div>

                {gptConfig.last_tested_at && (
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-sm text-green-800">
                        API key tested successfully on {new Date(gptConfig.last_tested_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                )}

                <button
                  type="submit"
                  className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition"
                >
                  Save & Test API Key
                </button>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/" replace />;
  }

  if (adminOnly && user.role !== 'admin') {
    return <Navigate to="/employee" replace />;
  }

  return children;
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="App">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/employee"
              element={
                <ProtectedRoute>
                  <EmployeeDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute adminOnly={true}>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />
            {/* Legacy route redirects */}
            <Route path="/login/employee" element={<Navigate to="/login" replace />} />
            <Route path="/login/admin" element={<Navigate to="/login" replace />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;