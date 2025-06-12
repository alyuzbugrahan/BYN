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
  PostLike,
  PostShare,
  Hashtag,
  SavedPost,
  Notification,
  FeedStats,
  // Connections types
  ConnectionRequest,
  Connection,
  Follow,
  UserRecommendation,
  NetworkMetrics,

  // Premium types
  SubscriptionPlan,
  UserSubscription,
  PremiumFeature,
  BillingHistory,
  // Analytics types
  UserActivity,
  SessionAnalytics,
  UserInsights,
  PlatformMetrics,
  TrendingContent
} from '../types';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
export const tokenManager = {
  getAccessToken: (): string | null => {
    return localStorage.getItem('accessToken');
  },
  
  getRefreshToken: (): string | null => {
    return localStorage.getItem('refreshToken');
  },
  
  setTokens: (tokens: AuthTokens): void => {
    localStorage.setItem('accessToken', tokens.access);
    localStorage.setItem('refreshToken', tokens.refresh);
  },
  
  clearTokens: (): void => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  },
  
  isAuthenticated: (): boolean => {
    return !!tokenManager.getAccessToken();
  }
};

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = tokenManager.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = tokenManager.getRefreshToken();
      if (refreshToken) {
        try {
          const response = await axios.post('/api/auth/token/refresh/', {
            refresh: refreshToken
          });
          
          const newTokens = response.data;
          tokenManager.setTokens(newTokens);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${newTokens.access}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          tokenManager.clearTokens();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const response: AxiosResponse<AuthTokens> = await api.post('/auth/login/', credentials);
    return response.data;
  },
  
  register: async (userData: RegisterData): Promise<User> => {
    const response: AxiosResponse<User> = await api.post('/auth/register/', userData);
    return response.data;
  },
  
  logout: async (): Promise<void> => {
    await api.post('/auth/logout/');
    tokenManager.clearTokens();
  },
  
  getProfile: async (): Promise<User> => {
    const response: AxiosResponse<User> = await api.get('/auth/profile/');
    return response.data;
  },
  
  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response: AxiosResponse<User> = await api.put('/auth/profile/', userData);
    return response.data;
  },
  
  refreshToken: async (refreshToken: string): Promise<AuthTokens> => {
    const response: AxiosResponse<AuthTokens> = await api.post('/auth/token/refresh/', {
      refresh: refreshToken
    });
    return response.data;
  }
};

// Jobs API
export const jobsAPI = {
  getJobs: async (filters?: JobFilters): Promise<PaginatedResponse<Job>> => {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v));
          } else {
            params.append(key, value.toString());
          }
        }
      });
    }
    
    const response: AxiosResponse<PaginatedResponse<Job>> = await api.get(`/jobs/jobs/?${params}`);
    return response.data;
  },
  
  getJob: async (id: number): Promise<Job> => {
    const response: AxiosResponse<Job> = await api.get(`/jobs/jobs/${id}/`);
    return response.data;
  },
  
  getRecommendedJobs: async (): Promise<PaginatedResponse<Job>> => {
    const response: AxiosResponse<PaginatedResponse<Job>> = await api.get('/jobs/jobs/recommended/');
    return response.data;
  },
  
  getSavedJobs: async (): Promise<PaginatedResponse<Job>> => {
    const response: AxiosResponse<PaginatedResponse<Job>> = await api.get('/jobs/jobs/saved/');
    return response.data;
  },
  
  saveJob: async (jobId: number): Promise<void> => {
    await api.post(`/jobs/jobs/${jobId}/save/`);
  },
  
  unsaveJob: async (jobId: number): Promise<void> => {
    await api.delete(`/jobs/jobs/${jobId}/save/`);
  },
  
  applyForJob: async (jobId: number, applicationData: {
    cover_letter?: string;
    portfolio_url?: string;
  }): Promise<JobApplication> => {
    const response: AxiosResponse<JobApplication> = await api.post('/jobs/applications/', {
      job_id: jobId,
      ...applicationData
    });
    return response.data;
  },
  
  getApplications: async (): Promise<PaginatedResponse<JobApplication>> => {
    const response: AxiosResponse<PaginatedResponse<JobApplication>> = await api.get('/jobs/applications/');
    return response.data;
  },
  
  withdrawApplication: async (applicationId: number): Promise<JobApplication> => {
    const response: AxiosResponse<JobApplication> = await api.patch(`/jobs/applications/${applicationId}/withdraw/`);
    return response.data;
  },
  
  getJobStats: async (): Promise<JobStats> => {
    const response: AxiosResponse<JobStats> = await api.get('/jobs/stats/');
    return response.data;
  },

  createJob: async (jobData: {
    title: string;
    description: string;
    requirements?: string;
    responsibilities?: string;
    company_id: number;
    location: string;
    workplace_type: string;
    job_type: string;
    experience_level: string;
    category?: number;
    salary_min?: number;
    salary_max?: number;
    salary_currency?: string;
    salary_type?: string;
    skills_required?: number[];
    skills_preferred?: number[];
    application_deadline?: string;
  }): Promise<Job> => {
    const response: AxiosResponse<Job> = await api.post('/jobs/jobs/', jobData);
    return response.data;
  },

  updateJob: async (id: number, jobData: Partial<{
    title: string;
    description: string;
    requirements: string;
    responsibilities: string;
    location: string;
    workplace_type: string;
    job_type: string;
    experience_level: string;
    category: number;
    salary_min: number;
    salary_max: number;
    salary_currency: string;
    salary_type: string;
    skills_required: number[];
    skills_preferred: number[];
    application_deadline: string;
    is_active: boolean;
  }>): Promise<Job> => {
    const response: AxiosResponse<Job> = await api.put(`/jobs/jobs/${id}/`, jobData);
    return response.data;
  },

  deleteJob: async (id: number): Promise<void> => {
    await api.delete(`/jobs/jobs/${id}/`);
  },

  getMyJobs: async (): Promise<PaginatedResponse<Job>> => {
    const response: AxiosResponse<PaginatedResponse<Job>> = await api.get('/jobs/jobs/my-posts/');
    return response.data;
  },

  getJobCategories: async (): Promise<{ id: number; name: string; slug: string; description: string }[]> => {
    const response: AxiosResponse<{ id: number; name: string; slug: string; description: string }[]> = await api.get('/jobs/categories/');
    return response.data;
  }
};

// Users API
export const usersAPI = {
  getUsers: async (page?: number): Promise<PaginatedResponse<User>> => {
    const params = new URLSearchParams();
    if (page) params.append('page', page.toString());
    
    const response: AxiosResponse<PaginatedResponse<User>> = await api.get(`/users/users/?${params}`);
    return response.data;
  },
  
  searchUsers: async (query: string, page?: number): Promise<PaginatedResponse<User>> => {
    const params = new URLSearchParams({ q: query });
    if (page) params.append('page', page.toString());
    
    const response: AxiosResponse<PaginatedResponse<User>> = await api.get(`/users/search/?${params}`);
    return response.data;
  },
  
  getUserProfile: async (userId: number): Promise<User> => {
    const response: AxiosResponse<User> = await api.get(`/users/profile/${userId}/`);
    return response.data;
  },
  
  getExperiences: async (): Promise<Experience[]> => {
    const response: AxiosResponse<Experience[]> = await api.get('/users/experiences/');
    return response.data;
  },
  
  addExperience: async (experienceData: Omit<Experience, 'id'>): Promise<Experience> => {
    const response: AxiosResponse<Experience> = await api.post('/users/experiences/', experienceData);
    return response.data;
  },
  
  updateExperience: async (id: number, experienceData: Partial<Experience>): Promise<Experience> => {
    const response: AxiosResponse<Experience> = await api.put(`/users/experiences/${id}/`, experienceData);
    return response.data;
  },
  
  deleteExperience: async (id: number): Promise<void> => {
    await api.delete(`/users/experiences/${id}/`);
  },
  
  getEducation: async (): Promise<Education[]> => {
    const response: AxiosResponse<Education[]> = await api.get('/users/education/');
    return response.data;
  },
  
  addEducation: async (educationData: Omit<Education, 'id'>): Promise<Education> => {
    const response: AxiosResponse<Education> = await api.post('/users/education/', educationData);
    return response.data;
  },
  
  updateEducation: async (id: number, educationData: Partial<Education>): Promise<Education> => {
    const response: AxiosResponse<Education> = await api.put(`/users/education/${id}/`, educationData);
    return response.data;
  },
  
  deleteEducation: async (id: number): Promise<void> => {
    await api.delete(`/users/education/${id}/`);
  },
  
  getSkills: async (): Promise<UserSkill[]> => {
    const response: AxiosResponse<UserSkill[]> = await api.get('/users/skills/');
    return response.data;
  },
  
  addSkill: async (skillName: string): Promise<UserSkill> => {
    const response: AxiosResponse<UserSkill> = await api.post('/users/skills/', {
      skill_name: skillName
    });
    return response.data;
  },
  
  removeSkill: async (skillId: number): Promise<void> => {
    await api.delete(`/users/skills/${skillId}/`);
  }
};

// Companies API
export const companiesAPI = {
  getCompanies: async (params?: string): Promise<PaginatedResponse<Company>> => {
    const response: AxiosResponse<PaginatedResponse<Company>> = await api.get(`/companies/companies/?${params || ''}`);
    return response.data;
  },
  
  getCompany: async (id: number): Promise<Company> => {
    const response: AxiosResponse<Company> = await api.get(`/companies/companies/${id}/`);
    return response.data;
  },
  
  followCompany: async (companyId: number): Promise<void> => {
    await api.post(`/companies/companies/${companyId}/follow/`);
  },
  
  unfollowCompany: async (companyId: number): Promise<void> => {
    await api.delete(`/companies/companies/${companyId}/unfollow/`);
  },

  getMyCompanies: async (): Promise<Company[]> => {
    const response: AxiosResponse<Company[]> = await api.get('/companies/companies/my-companies/');
    return response.data;
  },

  getFilterOptions: async (): Promise<{ industries: string[]; company_sizes: string[] }> => {
    const response: AxiosResponse<{ industries: string[]; company_sizes: string[] }> = await api.get('/companies/filter-options/');
    return response.data;
  }
};

// Feed API
export const feedAPI = {
  // Posts
  getFeed: async (filters?: PostFilters): Promise<PaginatedResponse<Post>> => {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    
    const response: AxiosResponse<PaginatedResponse<Post>> = await api.get(`/feed/posts/feed/?${params}`);
    return response.data;
  },
  
  getPosts: async (filters?: PostFilters): Promise<PaginatedResponse<Post>> => {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    
    const response: AxiosResponse<PaginatedResponse<Post>> = await api.get(`/feed/posts/?${params}`);
    return response.data;
  },
  
  getPost: async (id: number): Promise<Post> => {
    const response: AxiosResponse<Post> = await api.get(`/feed/posts/${id}/`);
    return response.data;
  },
  
  createPost: async (postData: {
    content: string;
    post_type?: string;
    visibility?: string;
    image?: File;
    video?: File;
    document?: File;
    hashtags?: string[];
    mentioned_users?: number[];
  }): Promise<Post> => {
    const formData = new FormData();
    formData.append('content', postData.content);
    if (postData.post_type) formData.append('post_type', postData.post_type);
    if (postData.visibility) formData.append('visibility', postData.visibility);
    if (postData.image) formData.append('image', postData.image);
    if (postData.video) formData.append('video', postData.video);
    if (postData.document) formData.append('document', postData.document);
    if (postData.hashtags) formData.append('hashtags', JSON.stringify(postData.hashtags));
    if (postData.mentioned_users) formData.append('mentioned_users', JSON.stringify(postData.mentioned_users));
    
    const response: AxiosResponse<Post> = await api.post('/feed/posts/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  updatePost: async (id: number, postData: Partial<Post>): Promise<Post> => {
    const response: AxiosResponse<Post> = await api.patch(`/feed/posts/${id}/`, postData);
    return response.data;
  },
  
  deletePost: async (id: number): Promise<void> => {
    await api.delete(`/feed/posts/${id}/`);
  },
  
  getTrendingPosts: async (): Promise<PaginatedResponse<Post>> => {
    const response: AxiosResponse<PaginatedResponse<Post>> = await api.get('/feed/posts/trending/');
    return response.data;
  },
  
  // Post interactions
  likePost: async (postId: number, reactionType: string = 'like'): Promise<any> => {
    const response: AxiosResponse<any> = await api.post(`/feed/posts/${postId}/like/`, {
      reaction_type: reactionType
    });
    return response.data;
  },
  
  unlikePost: async (postId: number): Promise<any> => {
    // Backend uses the same endpoint for both like and unlike
    const response: AxiosResponse<any> = await api.post(`/feed/posts/${postId}/like/`, {
      reaction_type: 'like'
    });
    return response.data;
  },
  
  sharePost: async (postId: number, comment?: string): Promise<PostShare> => {
    const response: AxiosResponse<PostShare> = await api.post(`/feed/posts/${postId}/share/`, {
      comment,
      share_type: 'share'
    });
    return response.data;
  },
  
  savePost: async (postId: number): Promise<SavedPost> => {
    const response: AxiosResponse<SavedPost> = await api.post(`/feed/posts/${postId}/save/`);
    return response.data;
  },
  
  unsavePost: async (postId: number): Promise<void> => {
    await api.delete(`/feed/posts/${postId}/save/`);
  },
  
  getSavedPosts: async (): Promise<PaginatedResponse<Post>> => {
    const response: AxiosResponse<PaginatedResponse<Post>> = await api.get('/feed/saved-posts/');
    return response.data;
  },
  
  // Comments
  getComments: async (postId: number): Promise<PaginatedResponse<Comment>> => {
    const response: AxiosResponse<PaginatedResponse<Comment>> = await api.get(`/feed/comments/?post=${postId}`);
    return response.data;
  },
  
  createComment: async (postId: number, content: string, parentId?: number): Promise<Comment> => {
    const response: AxiosResponse<Comment> = await api.post(`/feed/comments/`, {
      post: postId,
      content,
      parent: parentId
    });
    return response.data;
  },
  
  updateComment: async (commentId: number, content: string): Promise<Comment> => {
    const response: AxiosResponse<Comment> = await api.patch(`/feed/comments/${commentId}/`, {
      content
    });
    return response.data;
  },
  
  deleteComment: async (commentId: number): Promise<void> => {
    await api.delete(`/feed/comments/${commentId}/`);
  },
  
  likeComment: async (commentId: number): Promise<any> => {
    const response: AxiosResponse<any> = await api.post(`/feed/comments/${commentId}/like/`);
    return response.data;
  },
  
  unlikeComment: async (commentId: number): Promise<any> => {
    const response: AxiosResponse<any> = await api.delete(`/feed/comments/${commentId}/like/`);
    return response.data;
  },
  
  // Hashtags
  getTrendingHashtags: async (): Promise<Hashtag[]> => {
    const response: AxiosResponse<Hashtag[]> = await api.get('/feed/hashtags/trending/');
    return response.data;
  },
  
  getHashtagPosts: async (hashtagId: number): Promise<PaginatedResponse<Post>> => {
    const response: AxiosResponse<PaginatedResponse<Post>> = await api.get(`/feed/hashtags/${hashtagId}/posts/`);
    return response.data;
  },
  
  // Notifications
  getNotifications: async (): Promise<PaginatedResponse<Notification>> => {
    const response: AxiosResponse<PaginatedResponse<Notification>> = await api.get('/feed/notifications/');
    return response.data;
  },
  
  markNotificationAsRead: async (notificationId: number): Promise<Notification> => {
    const response: AxiosResponse<Notification> = await api.patch(`/feed/notifications/${notificationId}/mark_read/`);
    return response.data;
  },
  
  markAllNotificationsAsRead: async (): Promise<void> => {
    await api.post('/feed/notifications/mark_all_read/');
  },
  
  // Analytics
  getFeedStats: async (): Promise<FeedStats> => {
    const response: AxiosResponse<FeedStats> = await api.get('/feed/analytics/stats/');
    return response.data;
  }
};

// Connections API
export const connectionsAPI = {
  // Connection Requests
  getConnectionRequests: async (): Promise<PaginatedResponse<ConnectionRequest>> => {
    const response: AxiosResponse<PaginatedResponse<ConnectionRequest>> = await api.get('/connections/requests/');
    return response.data;
  },

  sendConnectionRequest: async (userId: number, message?: string): Promise<ConnectionRequest> => {
    const response: AxiosResponse<ConnectionRequest> = await api.post('/connections/requests/', {
      receiver_id: userId,
      message
    });
    return response.data;
  },

  respondToConnectionRequest: async (requestId: number, action: 'accept' | 'decline'): Promise<ConnectionRequest> => {
    const response: AxiosResponse<ConnectionRequest> = await api.post(`/connections/requests/${requestId}/respond/`, {
      action
    });
    return response.data;
  },

  withdrawConnectionRequest: async (requestId: number): Promise<void> => {
    await api.delete(`/connections/requests/${requestId}/`);
  },

  // Connections
  getConnections: async (page?: number): Promise<PaginatedResponse<Connection>> => {
    const params = new URLSearchParams();
    if (page) params.append('page', page.toString());
    
    const response: AxiosResponse<PaginatedResponse<Connection>> = await api.get(`/connections/connections/?${params}`);
    return response.data;
  },

  removeConnection: async (connectionId: number): Promise<void> => {
    await api.delete(`/connections/connections/${connectionId}/remove/`);
  },

  // Following
  followUser: async (userId: number): Promise<Follow> => {
    const response: AxiosResponse<Follow> = await api.post('/connections/follow/', {
      following_id: userId
    });
    return response.data;
  },

  unfollowUser: async (userId: number): Promise<void> => {
    await api.delete(`/connections/follow/${userId}/`);
  },

  getFollowers: async (userId?: number): Promise<PaginatedResponse<Follow>> => {
    const endpoint = userId ? `/connections/users/${userId}/followers/` : '/connections/my-followers/';
    const response: AxiosResponse<PaginatedResponse<Follow>> = await api.get(endpoint);
    return response.data;
  },

  getFollowing: async (userId?: number): Promise<PaginatedResponse<Follow>> => {
    const endpoint = userId ? `/connections/users/${userId}/following/` : '/connections/my-following/';
    const response: AxiosResponse<PaginatedResponse<Follow>> = await api.get(endpoint);
    return response.data;
  },

  // Recommendations
  getUserRecommendations: async (): Promise<PaginatedResponse<UserRecommendation>> => {
    const response: AxiosResponse<PaginatedResponse<UserRecommendation>> = await api.get('/connections/recommendations/');
    return response.data;
  },

  dismissRecommendation: async (recommendationId: number): Promise<void> => {
    await api.patch(`/connections/recommendations/${recommendationId}/dismiss/`);
  },

  // Network Metrics
  getNetworkMetrics: async (): Promise<NetworkMetrics> => {
    const response: AxiosResponse<NetworkMetrics> = await api.get('/connections/network-metrics/');
    return response.data;
  }
};



// Premium API
export const premiumAPI = {
  // Subscription Plans
  getSubscriptionPlans: async (): Promise<SubscriptionPlan[]> => {
    const response: AxiosResponse<SubscriptionPlan[]> = await api.get('/premium/plans/');
    return response.data;
  },

  getSubscriptionPlan: async (planId: number): Promise<SubscriptionPlan> => {
    const response: AxiosResponse<SubscriptionPlan> = await api.get(`/premium/plans/${planId}/`);
    return response.data;
  },

  // User Subscription
  getUserSubscription: async (): Promise<UserSubscription> => {
    const response: AxiosResponse<UserSubscription> = await api.get('/premium/subscription/');
    return response.data;
  },

  createSubscription: async (subscriptionData: {
    plan_id: number;
    billing_cycle: 'monthly' | 'yearly';
    promo_code?: string;
  }): Promise<UserSubscription> => {
    const response: AxiosResponse<UserSubscription> = await api.post('/premium/subscription/', subscriptionData);
    return response.data;
  },

  updateSubscription: async (subscriptionData: {
    plan_id?: number;
    billing_cycle?: 'monthly' | 'yearly';
    auto_renew?: boolean;
  }): Promise<UserSubscription> => {
    const response: AxiosResponse<UserSubscription> = await api.patch('/premium/subscription/', subscriptionData);
    return response.data;
  },

  cancelSubscription: async (): Promise<UserSubscription> => {
    const response: AxiosResponse<UserSubscription> = await api.post('/premium/subscription/cancel/');
    return response.data;
  },

  reactivateSubscription: async (): Promise<UserSubscription> => {
    const response: AxiosResponse<UserSubscription> = await api.post('/premium/subscription/reactivate/');
    return response.data;
  },

  // Features
  getPremiumFeatures: async (): Promise<PremiumFeature[]> => {
    const response: AxiosResponse<PremiumFeature[]> = await api.get('/premium/features/');
    return response.data;
  },

  checkFeatureAccess: async (featureCode: string): Promise<{ has_access: boolean; reason?: string }> => {
    const response: AxiosResponse<{ has_access: boolean; reason?: string }> = await api.get(`/premium/features/${featureCode}/access/`);
    return response.data;
  },

  // Billing
  getBillingHistory: async (): Promise<PaginatedResponse<BillingHistory>> => {
    const response: AxiosResponse<PaginatedResponse<BillingHistory>> = await api.get('/premium/billing/history/');
    return response.data;
  },

  downloadInvoice: async (invoiceId: string): Promise<Blob> => {
    const response = await api.get(`/premium/billing/invoices/${invoiceId}/download/`, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Usage Tracking
  getUsageStats: async (): Promise<{
    profile_views_used: number;
    inmails_used: number;
    monthly_limit: number;
    reset_date: string;
  }> => {
    const response = await api.get('/premium/usage/');
    return response.data;
  }
};

// Analytics API
export const analyticsAPI = {
  // User Analytics
  getUserInsights: async (): Promise<UserInsights> => {
    const response: AxiosResponse<UserInsights> = await api.get('/analytics/insights/');
    return response.data;
  },

  getUserActivity: async (filters?: {
    activity_type?: string;
    date_from?: string;
    date_to?: string;
    page?: number;
  }): Promise<PaginatedResponse<UserActivity>> => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    
    const response: AxiosResponse<PaginatedResponse<UserActivity>> = await api.get(`/analytics/activity/?${params}`);
    return response.data;
  },

  getSessionAnalytics: async (sessionId?: string): Promise<SessionAnalytics[]> => {
    const params = sessionId ? `?session_id=${sessionId}` : '';
    const response: AxiosResponse<SessionAnalytics[]> = await api.get(`/analytics/sessions/${params}`);
    return response.data;
  },

  // Content Analytics
  getContentPerformance: async (contentType: 'post' | 'job', contentId: number): Promise<{
    views: number;
    likes: number;
    comments: number;
    shares: number;
    engagement_rate: number;
    demographics: Record<string, any>;
    timeline: Array<{ date: string; views: number; engagement: number }>;
  }> => {
    const response = await api.get(`/analytics/content/${contentType}/${contentId}/performance/`);
    return response.data;
  },

  // Platform Analytics (for admins)
  getPlatformMetrics: async (dateFrom?: string, dateTo?: string): Promise<PlatformMetrics[]> => {
    const params = new URLSearchParams();
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    
    const response: AxiosResponse<PlatformMetrics[]> = await api.get(`/analytics/platform/?${params}`);
    return response.data;
  },

  getTrendingContent: async (trendType?: string): Promise<TrendingContent[]> => {
    const params = trendType ? `?trend_type=${trendType}` : '';
    const response: AxiosResponse<TrendingContent[]> = await api.get(`/analytics/trending/${params}`);
    return response.data;
  },

  // Profile Analytics
  getProfileViews: async (days: number = 30): Promise<{
    total_views: number;
    unique_viewers: number;
    growth_percentage: number;
    timeline: Array<{ date: string; views: number }>;
    viewer_demographics: Record<string, any>;
  }> => {
    const response = await api.get(`/analytics/profile/views/?days=${days}`);
    return response.data;
  },

  getSearchAppearances: async (days: number = 30): Promise<{
    total_appearances: number;
    unique_searches: number;
    top_keywords: Array<{ keyword: string; count: number }>;
    timeline: Array<{ date: string; appearances: number }>;
  }> => {
    const response = await api.get(`/analytics/profile/search-appearances/?days=${days}`);
    return response.data;
  },

  // Engagement Analytics
  getEngagementMetrics: async (days: number = 30): Promise<{
    posts_engagement: {
      total_likes: number;
      total_comments: number;
      total_shares: number;
      average_engagement_rate: number;
    };
    network_growth: {
      new_connections: number;
      new_followers: number;
      connection_acceptance_rate: number;
    };
    content_reach: {
      total_impressions: number;
      unique_reach: number;
      viral_posts: number;
    };
  }> => {
    const response = await api.get(`/analytics/engagement/?days=${days}`);
    return response.data;
  }
};

export default api; 