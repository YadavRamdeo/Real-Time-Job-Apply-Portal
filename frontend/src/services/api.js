import axios from 'axios';
import API_CONFIG from '../config/api.config';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      // Django token auth expects "Token <key>"
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Authentication services
export const login = (username, password) => {
  return api.post(API_CONFIG.ENDPOINTS.LOGIN, { username, password });
};

export const register = (userData) => {
  return api.post(API_CONFIG.ENDPOINTS.REGISTER, userData);
};

export const getUserProfile = () => {
  return api.get(API_CONFIG.ENDPOINTS.PROFILE);
};

export const updateUserProfile = (profileData) => {
  // Backend expects update at /accounts/profile/update/
  return api.put(`${API_CONFIG.ENDPOINTS.PROFILE}update/`, profileData);
};

// Job services
export const getJobs = (params) => {
  return api.get(API_CONFIG.ENDPOINTS.JOBS, { params });
};

export const searchLiveJobs = (params) => {
  return api.get(`${API_CONFIG.ENDPOINTS.JOBS}search/`, { params });
};

export const getJobById = (id) => {
  return api.get(`${API_CONFIG.ENDPOINTS.JOBS}${id}/`);
};

// Resume matching via backend jobs endpoint
export const findMatchingJobs = (resumeId, threshold = 0.6) => {
  return api.get(`/jobs/matching/${resumeId}/`, {
    params: { threshold }
  });
};

// Resume services
export const getResumes = () => {
  return api.get(API_CONFIG.ENDPOINTS.RESUMES);
};

export const getResumeById = (id) => {
  return api.get(`${API_CONFIG.ENDPOINTS.RESUMES}${id}/`);
};

export const uploadResume = (formData) => {
  return api.post(`${API_CONFIG.ENDPOINTS.RESUMES}upload/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const parseResume = (resumeId) => {
  return api.post(`${API_CONFIG.ENDPOINTS.RESUME_PARSE}${resumeId}/`);
};

// Application services
export const getApplications = () => {
  return api.get('/resumes/applications/');
};

export const applyToJob = (jobId, resumeId, coverLetter = '') => {
  // Backend apply endpoint lives under /jobs/apply/<job_id>/
  return api.post(`/jobs/apply/${jobId}/`, {
    resume_id: resumeId,
    cover_letter: coverLetter
  });
};

export const updateApplicationStatus = (applicationId, status) => {
  return api.put(`/resumes/applications/${applicationId}/status/`, {
    status
  });
};

// Notification services (backend routes may not be wired; keep for future)
export const getNotifications = () => {
  return api.get(API_CONFIG.ENDPOINTS.NOTIFICATIONS);
};

export const markNotificationAsRead = (notificationId) => {
  return api.patch(`${API_CONFIG.ENDPOINTS.NOTIFICATIONS}${notificationId}/`, {
    read: true
  });
};

// Export the API instance
export default api;
