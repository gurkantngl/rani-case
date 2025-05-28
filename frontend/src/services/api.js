import axios from 'axios';

// Backend API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API Services
export const apiService = {
  // Chat API
  askQuestion: async (message, approach = 'prompt') => {
    const response = await api.post('/api/ask', {
      message,
      approach
    });
    return response.data;
  },

  // Get chat history
  getChatHistory: async () => {
    const response = await api.get('/api/history');
    return response.data;
  },

  // Get system statistics
  getStats: async () => {
    const response = await api.get('/api/stats');
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },

  // Test multiple approaches
  testAllApproaches: async (message) => {
    const approaches = ['rag', 'prompt', 'hybrid'];
    const promises = approaches.map(approach => 
      apiService.askQuestion(message, approach)
        .catch(error => ({ error: error.message, approach }))
    );
    
    const results = await Promise.allSettled(promises);
    return results.map((result, index) => ({
      approach: approaches[index],
      ...result.value
    }));
  }
};

// Utility functions
export const utils = {
  // Format confidence score
  formatConfidence: (confidence) => {
    if (typeof confidence !== 'number') return '0%';
    return `${Math.round(confidence * 100)}%`;
  },

  // Get confidence color
  getConfidenceColor: (confidence) => {
    if (confidence > 0.7) return 'text-green-500';
    if (confidence > 0.4) return 'text-yellow-500';
    return 'text-red-500';
  },

  // Get confidence badge color
  getConfidenceBadgeColor: (confidence) => {
    if (confidence > 0.7) return 'bg-green-100 text-green-800';
    if (confidence > 0.4) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  },

  // Format response time
  formatResponseTime: (time) => {
    if (time < 1000) return `${time}ms`;
    return `${(time / 1000).toFixed(1)}s`;
  },

  // Detect scenario icon
  getScenarioIcon: (scenario) => {
    const icons = {
      'siparis_takip': '📦',
      'iade_degisim': '🔄',
      'urun_bilgisi': '🛋️',
      'kargo_sorgulama': '🚚',
      'genel_destek': '💬'
    };
    return icons[scenario] || '💬';
  },

  // Get approach color
  getApproachColor: (approach) => {
    const colors = {
      'rag': 'bg-blue-500',
      'prompt': 'bg-green-500',
      'hybrid': 'bg-purple-500'
    };
    return colors[approach] || 'bg-gray-500';
  }
};

export default api; 