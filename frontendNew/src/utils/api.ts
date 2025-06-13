import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  User, 
  AuthTokens, 
  LoginCredentials, 
  RegisterData, 
  Job, 
  JobFilters, 
  JobApplication, 
  Company, 
  JobStats,
  PaginatedResponse,
  Experience,
  Education,
  UserSkill,
  Skill,
  Post,
  PostFilters,
  Comment,
  PostShare,
  Hashtag,
  Notification,
  FeedStats,
  ConnectionRequest,
  Connection,
  Follow,
  UserRecommendation,
  NetworkMetrics
} from '../types';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: 'http://3.65.227.81:8000/api',
  timeout: 10000, // 10 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Debug mode
const DEBUG_API = process.env.NEXT_PUBLIC_DEBUG_API === 'true';

// Enhanced logging for debugging
if (DEBUG_API) {
  console.log('🌐 API Configuration:');
  console.log('- Base URL:', api.defaults.baseURL);
  console.log('- Timeout:', api.defaults.timeout);
  console.log('- Debug Mode: Enabled');
}

// Token management
export const tokenManager = {
  getAccessToken: (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('accessToken');
  },
  
  getRefreshToken: (): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('refreshToken');
  },
  
  setTokens: (tokens: AuthTokens): void => {
    if (typeof window === 'undefined') return;
    localStorage.setItem('accessToken', tokens.access);
    localStorage.setItem('refreshToken', tokens.refresh);
  },
  
  clearTokens: (): void => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  },
  
  isAuthenticated: (): boolean => {
    return !!tokenManager.getAccessToken();
  }
};

// Request interceptor to add auth token and detailed logging
api.interceptors.request.use(
  (config) => {
    const token = tokenManager.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Detailed logging for debugging
    if (DEBUG_API) {
      console.log('🚀 API Request:', {
        method: config.method?.toUpperCase(),
        url: config.url,
        baseURL: config.baseURL,
        fullURL: `${config.baseURL}${config.url}`,
        headers: {
          ...config.headers,
          Authorization: token ? `Bearer ${token.substring(0, 20)}...` : 'None'
        },
        data: config.data ?? 'No data',
        timestamp: new Date().toISOString()
      });
    }

    return config;
  },
  (error) => {
    if (DEBUG_API) {
      console.error('❌ Request Error:', error);
    }
    return Promise.reject(new Error(`Request failed: ${error.message}`));
  }
);

// Helper function to log API errors
const logApiError = (error: any) => {
  if (DEBUG_API) {
    console.error('❌ API Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      method: error.config?.method?.toUpperCase(),
      responseData: error.response?.data,
      message: error.message,
      timestamp: new Date().toISOString()
    });
  }
};

// Helper function to handle token refresh
const handleTokenRefresh = async (originalRequest: any): Promise<any> => {
  const refreshToken = tokenManager.getRefreshToken();
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  if (DEBUG_API) {
    console.log('🔄 Attempting token refresh...');
  }
  
  const response = await api.post('/auth/token/refresh/', {
    refresh: refreshToken
  });
  
  const newTokens: AuthTokens = response.data;
  tokenManager.setTokens(newTokens);
  
  if (DEBUG_API) {
    console.log('✅ Token refreshed successfully');
  }
  
  // Retry the original request with new token
  originalRequest.headers.Authorization = `Bearer ${newTokens.access}`;
  return axios(originalRequest);
};

// Helper function to handle logout redirect
const handleLogoutRedirect = () => {
  if (DEBUG_API) {
    console.log('🚫 Authentication failed, redirecting to login');
  }
  tokenManager.clearTokens();
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
};

// Response interceptor to handle token refresh and detailed logging
api.interceptors.response.use(
  (response) => {
    if (DEBUG_API) {
      console.log('✅ API Response:', {
        status: response.status,
        statusText: response.statusText,
        url: response.config.url,
        data: response.data,
        headers: response.headers,
        timestamp: new Date().toISOString()
      });
    }
    return response;
  },
  async (error) => {
    logApiError(error);
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        return await handleTokenRefresh(originalRequest);
      } catch (refreshError) {
        if (DEBUG_API) {
          console.error('❌ Token refresh failed:', refreshError);
        }
        handleLogoutRedirect();
        return Promise.reject(new Error(`Token refresh failed: ${refreshError}`));
      }
    }
    
    return Promise.reject(error instanceof Error ? error : new Error('API request failed'));
  }
);

// Authentication API
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    if (DEBUG_API) {
      console.log('🔐 Login Request Started:', {
        email: credentials.email,
        passwordLength: credentials.password.length,
        timestamp: new Date().toISOString(),
        endpoint: '/auth/login/',
        method: 'POST'
      });
    }

    try {
      const response: AxiosResponse<AuthTokens> = await api.post('/auth/login/', credentials);
      
      if (DEBUG_API) {
        console.log('🔐 Login Response Received:', {
          status: response.status,
          hasAccessToken: !!response.data.access,
          hasRefreshToken: !!response.data.refresh,
          accessTokenLength: response.data.access?.length,
          refreshTokenLength: response.data.refresh?.length,
          timestamp: new Date().toISOString()
        });
      }

      return response.data;
    } catch (error: any) {
      if (DEBUG_API) {
        console.error('🔐 Login Failed:', {
          status: error.response?.status,
          statusText: error.response?.statusText,
          errorData: error.response?.data,
          message: error.message,
          timestamp: new Date().toISOString()
        });
      }
      throw error;
    }
  },

  register: async (userData: RegisterData): Promise<User> => {
    const response: AxiosResponse<User> = await api.post('/auth/register/', userData);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout/');
  },
  getProfile: async (): Promise<User> => {
    if (DEBUG_API) {
      console.log('👤 Profile Request Started:', {
        timestamp: new Date().toISOString(),
        endpoint: '/auth/profile/',
        method: 'GET',
        hasToken: !!tokenManager.getAccessToken()
      });
    }

    try {
      const response: AxiosResponse<User> = await api.get('/auth/profile/');
      
      if (DEBUG_API) {
        console.log('👤 Profile Response Received:', {
          status: response.status,
          userId: response.data.id,
          email: response.data.email,
          isCompanyUser: response.data.is_company_user,
          timestamp: new Date().toISOString()
        });
      }

      return response.data;
    } catch (error: any) {
      if (DEBUG_API) {
        console.error('👤 Profile Request Failed:', {
          status: error.response?.status,
          statusText: error.response?.statusText,
          errorData: error.response?.data,
          message: error.message,
          timestamp: new Date().toISOString()
        });
      }
      throw error;
    }
  },

  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response: AxiosResponse<User> = await api.patch('/auth/profile/', userData);
    return response.data;
  },

  changePassword: async (data: { old_password: string; new_password: string }): Promise<void> => {
    await api.post('/auth/change-password/', data);
  },

  requestPasswordReset: async (email: string): Promise<void> => {
    await api.post('/auth/password-reset/', { email });
  },

  confirmPasswordReset: async (data: { token: string; password: string }): Promise<void> => {
    await api.post('/auth/password-reset/confirm/', data);
  },
};

// Jobs API
export const jobsAPI = {
  getJobs: async (filters?: JobFilters): Promise<PaginatedResponse<Job>> => {
    const response: AxiosResponse<PaginatedResponse<Job>> = await api.get('/jobs/', { params: filters });
    return response.data;
  },

  getJob: async (id: number): Promise<Job> => {
    const response: AxiosResponse<Job> = await api.get(`/jobs/${id}/`);
    return response.data;
  },

  createJob: async (jobData: Partial<Job>): Promise<Job> => {
    const response: AxiosResponse<Job> = await api.post('/jobs/', jobData);
    return response.data;
  },

  updateJob: async (id: number, jobData: Partial<Job>): Promise<Job> => {
    const response: AxiosResponse<Job> = await api.patch(`/jobs/${id}/`, jobData);
    return response.data;
  },

  deleteJob: async (id: number): Promise<void> => {
    await api.delete(`/jobs/${id}/`);
  },

  applyForJob: async (jobId: number, applicationData: { cover_letter: string; resume?: File }): Promise<JobApplication> => {
    const formData = new FormData();
    formData.append('cover_letter', applicationData.cover_letter);
    if (applicationData.resume) {
      formData.append('resume', applicationData.resume);
    }

    const response: AxiosResponse<JobApplication> = await api.post(`/jobs/${jobId}/apply/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getJobApplications: async (jobId?: number): Promise<PaginatedResponse<JobApplication>> => {
    const url = jobId ? `/jobs/${jobId}/applications/` : '/jobs/applications/';
    const response: AxiosResponse<PaginatedResponse<JobApplication>> = await api.get(url);
    return response.data;
  },

  updateApplicationStatus: async (applicationId: number, status: string): Promise<JobApplication> => {
    const response: AxiosResponse<JobApplication> = await api.patch(`/jobs/applications/${applicationId}/`, { status });
    return response.data;
  },

  saveJob: async (jobId: number): Promise<void> => {
    await api.post(`/jobs/${jobId}/save/`);
  },

  unsaveJob: async (jobId: number): Promise<void> => {
    await api.delete(`/jobs/${jobId}/save/`);
  },

  getSavedJobs: async (): Promise<PaginatedResponse<Job>> => {
    const response: AxiosResponse<PaginatedResponse<Job>> = await api.get('/jobs/saved/');
    return response.data;
  },

  getJobStats: async (): Promise<JobStats> => {
    const response: AxiosResponse<JobStats> = await api.get('/jobs/stats/');
    return response.data;
  },

  getRecommendedJobs: async (): Promise<PaginatedResponse<Job>> => {
    const response: AxiosResponse<PaginatedResponse<Job>> = await api.get('/jobs/recommended/');
    return response.data;
  },
};

// Companies API
export const companiesAPI = {
  getCompanies: async (filters?: any): Promise<PaginatedResponse<Company>> => {
    const response: AxiosResponse<PaginatedResponse<Company>> = await api.get('/companies/', { params: filters });
    return response.data;
  },

  getCompany: async (id: number): Promise<Company> => {
    const response: AxiosResponse<Company> = await api.get(`/companies/${id}/`);
    return response.data;
  },

  createCompany: async (companyData: Partial<Company>): Promise<Company> => {
    const response: AxiosResponse<Company> = await api.post('/companies/', companyData);
    return response.data;
  },

  updateCompany: async (id: number, companyData: Partial<Company>): Promise<Company> => {
    const response: AxiosResponse<Company> = await api.patch(`/companies/${id}/`, companyData);
    return response.data;
  },

  followCompany: async (companyId: number): Promise<void> => {
    await api.post(`/companies/${companyId}/follow/`);
  },

  unfollowCompany: async (companyId: number): Promise<void> => {
    await api.delete(`/companies/${companyId}/follow/`);
  },
};

// Feed API
export const feedAPI = {
  getPosts: async (filters?: PostFilters): Promise<PaginatedResponse<Post>> => {
    const response: AxiosResponse<PaginatedResponse<Post>> = await api.get('/feed/posts/', { params: filters });
    return response.data;
  },

  getPost: async (id: number): Promise<Post> => {
    const response: AxiosResponse<Post> = await api.get(`/feed/posts/${id}/`);
    return response.data;
  },

  createPost: async (postData: Partial<Post>): Promise<Post> => {
    const response: AxiosResponse<Post> = await api.post('/feed/posts/', postData);
    return response.data;
  },

  updatePost: async (id: number, postData: Partial<Post>): Promise<Post> => {
    const response: AxiosResponse<Post> = await api.patch(`/feed/posts/${id}/`, postData);
    return response.data;
  },

  deletePost: async (id: number): Promise<void> => {
    await api.delete(`/feed/posts/${id}/`);
  },

  likePost: async (postId: number): Promise<{ status: string }> => {
    const response: AxiosResponse<{ status: string }> = await api.post(`/feed/posts/${postId}/like/`);
    return response.data;
  },

  sharePost: async (postId: number, comment?: string): Promise<PostShare> => {
    const response: AxiosResponse<PostShare> = await api.post(`/feed/posts/${postId}/share/`, { comment });
    return response.data;
  },

  savePost: async (postId: number): Promise<void> => {
    await api.post(`/feed/posts/${postId}/save/`);
  },

  unsavePost: async (postId: number): Promise<void> => {
    await api.delete(`/feed/posts/${postId}/save/`);
  },

  getComments: async (postId: number): Promise<PaginatedResponse<Comment>> => {
    const response: AxiosResponse<PaginatedResponse<Comment>> = await api.get(`/feed/posts/${postId}/comments/`);
    return response.data;
  },

  createComment: async (postId: number, content: string, parentId?: number): Promise<Comment> => {
    const response: AxiosResponse<Comment> = await api.post(`/feed/posts/${postId}/comments/`, {
      content,
      parent: parentId,
    });
    return response.data;
  },

  updateComment: async (commentId: number, content: string): Promise<Comment> => {
    const response: AxiosResponse<Comment> = await api.patch(`/feed/comments/${commentId}/`, { content });
    return response.data;
  },

  deleteComment: async (commentId: number): Promise<void> => {
    await api.delete(`/feed/comments/${commentId}/`);
  },

  likeComment: async (commentId: number): Promise<{ status: string }> => {
    const response: AxiosResponse<{ status: string }> = await api.post(`/feed/comments/${commentId}/like/`);
    return response.data;
  },

  getFeedStats: async (): Promise<FeedStats> => {
    const response: AxiosResponse<FeedStats> = await api.get('/feed/stats/');
    return response.data;
  },

  getTrendingHashtags: async (): Promise<Hashtag[]> => {
    const response: AxiosResponse<Hashtag[]> = await api.get('/feed/hashtags/trending/');
    return response.data;
  },
};

// Connections API
export const connectionsAPI = {
  getConnections: async (): Promise<PaginatedResponse<Connection>> => {
    const response: AxiosResponse<PaginatedResponse<Connection>> = await api.get('/connections/');
    return response.data;
  },

  sendConnectionRequest: async (userId: number, message?: string): Promise<ConnectionRequest> => {
    const response: AxiosResponse<ConnectionRequest> = await api.post('/connections/requests/', {
      receiver: userId,
      message,
    });
    return response.data;
  },

  getConnectionRequests: async (): Promise<PaginatedResponse<ConnectionRequest>> => {
    const response: AxiosResponse<PaginatedResponse<ConnectionRequest>> = await api.get('/connections/requests/');
    return response.data;
  },

  respondToConnectionRequest: async (requestId: number, action: 'accept' | 'reject'): Promise<ConnectionRequest> => {
    const response: AxiosResponse<ConnectionRequest> = await api.patch(`/connections/requests/${requestId}/`, {
      status: action === 'accept' ? 'accepted' : 'rejected',
    });
    return response.data;
  },

  removeConnection: async (connectionId: number): Promise<void> => {
    await api.delete(`/connections/${connectionId}/`);
  },

  getUserRecommendations: async (): Promise<UserRecommendation[]> => {
    const response: AxiosResponse<UserRecommendation[]> = await api.get('/connections/recommendations/');
    return response.data;
  },

  getNetworkMetrics: async (): Promise<NetworkMetrics> => {
    const response: AxiosResponse<NetworkMetrics> = await api.get('/connections/metrics/');
    return response.data;
  },

  followUser: async (userId: number): Promise<Follow> => {
    const response: AxiosResponse<Follow> = await api.post('/connections/follow/', { following: userId });
    return response.data;
  },

  unfollowUser: async (userId: number): Promise<void> => {
    await api.delete(`/connections/follow/${userId}/`);
  },
};

// Notifications API
export const notificationsAPI = {
  getNotifications: async (): Promise<PaginatedResponse<Notification>> => {
    const response: AxiosResponse<PaginatedResponse<Notification>> = await api.get('/notifications/');
    return response.data;
  },

  markAsRead: async (notificationId: number): Promise<void> => {
    await api.patch(`/notifications/${notificationId}/`, { is_read: true });
  },

  markAllAsRead: async (): Promise<void> => {
    await api.post('/notifications/mark-all-read/');
  },

  deleteNotification: async (notificationId: number): Promise<void> => {
    await api.delete(`/notifications/${notificationId}/`);
  },
};

// Users API
export const usersAPI = {
  getUsers: async (filters?: any): Promise<PaginatedResponse<User>> => {
    const response: AxiosResponse<PaginatedResponse<User>> = await api.get('/users/', { params: filters });
    return response.data;
  },

  getUser: async (id: number): Promise<User> => {
    const response: AxiosResponse<User> = await api.get(`/users/${id}/`);
    return response.data;
  },

  getUserExperience: async (userId: number): Promise<Experience[]> => {
    const response: AxiosResponse<Experience[]> = await api.get(`/users/${userId}/experience/`);
    return response.data;
  },

  addExperience: async (experienceData: Partial<Experience>): Promise<Experience> => {
    const response: AxiosResponse<Experience> = await api.post('/users/experience/', experienceData);
    return response.data;
  },

  updateExperience: async (id: number, experienceData: Partial<Experience>): Promise<Experience> => {
    const response: AxiosResponse<Experience> = await api.patch(`/users/experience/${id}/`, experienceData);
    return response.data;
  },

  deleteExperience: async (id: number): Promise<void> => {
    await api.delete(`/users/experience/${id}/`);
  },

  getUserEducation: async (userId: number): Promise<Education[]> => {
    const response: AxiosResponse<Education[]> = await api.get(`/users/${userId}/education/`);
    return response.data;
  },

  addEducation: async (educationData: Partial<Education>): Promise<Education> => {
    const response: AxiosResponse<Education> = await api.post('/users/education/', educationData);
    return response.data;
  },

  updateEducation: async (id: number, educationData: Partial<Education>): Promise<Education> => {
    const response: AxiosResponse<Education> = await api.patch(`/users/education/${id}/`, educationData);
    return response.data;
  },

  deleteEducation: async (id: number): Promise<void> => {
    await api.delete(`/users/education/${id}/`);
  },

  getUserSkills: async (userId: number): Promise<UserSkill[]> => {
    const response: AxiosResponse<UserSkill[]> = await api.get(`/users/${userId}/skills/`);
    return response.data;
  },

  addSkill: async (skillData: Partial<UserSkill>): Promise<UserSkill> => {
    const response: AxiosResponse<UserSkill> = await api.post('/users/skills/', skillData);
    return response.data;
  },

  updateSkill: async (id: number, skillData: Partial<UserSkill>): Promise<UserSkill> => {
    const response: AxiosResponse<UserSkill> = await api.patch(`/users/skills/${id}/`, skillData);
    return response.data;
  },

  deleteSkill: async (id: number): Promise<void> => {
    await api.delete(`/users/skills/${id}/`);
  },

  getSkills: async (): Promise<Skill[]> => {
    const response: AxiosResponse<Skill[]> = await api.get('/skills/');
    return response.data;
  },
};

// Search API
export const searchAPI = {
  search: async (query: string, filters?: any): Promise<any> => {
    const response = await api.get('/search/', { params: { q: query, ...filters } });
    return response.data;
  },

  searchUsers: async (query: string, filters?: any): Promise<PaginatedResponse<User>> => {
    const response: AxiosResponse<PaginatedResponse<User>> = await api.get('/search/users/', { 
      params: { q: query, ...filters } 
    });
    return response.data;
  },

  searchJobs: async (query: string, filters?: JobFilters): Promise<PaginatedResponse<Job>> => {
    const response: AxiosResponse<PaginatedResponse<Job>> = await api.get('/search/jobs/', { 
      params: { q: query, ...filters } 
    });
    return response.data;
  },

  searchCompanies: async (query: string, filters?: any): Promise<PaginatedResponse<Company>> => {
    const response: AxiosResponse<PaginatedResponse<Company>> = await api.get('/search/companies/', { 
      params: { q: query, ...filters } 
    });
    return response.data;
  },
};

// Connectivity test function
export const testAPIConnection = async (): Promise<{ connected: boolean; error?: string; details?: any }> => {
  try {
    console.log('🔍 Testing API connectivity...');
    console.log('Target URL:', api.defaults.baseURL);
    
    // First try a simple health check or any endpoint that doesn't require auth
    const response = await axios.get(`${api.defaults.baseURL}/auth/login/`, {
      timeout: 5000,
      method: 'OPTIONS', // CORS preflight check
    });
    
    console.log('✅ API connectivity test successful:', {
      status: response.status,
      headers: response.headers
    });
    
    return { connected: true };
  } catch (error: any) {
    console.error('❌ API connectivity test failed:', {
      message: error.message,
      code: error.code,
      response: error.response?.data,
      status: error.response?.status
    });
    
    return { 
      connected: false, 
      error: error.message,
      details: {
        code: error.code,
        status: error.response?.status,
        data: error.response?.data
      }
    };
  }
};

export default api;
