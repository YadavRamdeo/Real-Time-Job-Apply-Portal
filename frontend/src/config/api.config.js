// API Configuration
const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/api',
  ENDPOINTS: {
    // Auth endpoints
    LOGIN: '/auth/login/',
    REGISTER: '/auth/register/',
    PROFILE: '/accounts/profile/',
    
    // Job endpoints
    JOBS: '/jobs/',
    
    // Resume endpoints
    RESUMES: '/resumes/',
    
    // Application endpoints (mapped to resumes app in backend)
    APPLICATIONS: '/resumes/applications/',
    
    // Notification endpoints
    NOTIFICATIONS: '/notifications/',
  },
  WEBSOCKET_URL: 'ws://localhost:8000/ws/notifications/'
};

export default API_CONFIG;