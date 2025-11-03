// API Configuration (supports overrides via environment variables for Docker/dev)
const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';
const WS_BASE = process.env.REACT_APP_WS_URL || (
  API_BASE.replace(/^http/, 'ws').replace(/\/api$/, '') + '/ws/notifications/'
);

const API_CONFIG = {
  BASE_URL: API_BASE,
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

    // Notification endpoints (optional REST fallback)
    NOTIFICATIONS: '/notifications/',
  },
  WEBSOCKET_URL: WS_BASE,
};

export default API_CONFIG;
