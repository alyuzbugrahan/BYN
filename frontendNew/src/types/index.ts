// User types
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  headline?: string;
  current_position?: string;
  location?: string;
  industry?: string;
  experience_level?: 'intern' | 'entry' | 'associate' | 'mid' | 'senior' | 'executive';
  profile_picture?: string;
  profile_picture_url?: string;
  cover_image?: string;
  about?: string;
  phone_number?: string;
  website?: string;
  date_joined: string;
  last_login?: string;
  is_company_user?: boolean;
}

// Authentication types
export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
}

// Feed/Social Media types
export interface Post {
  id: number;
  author: User;
  content: string;
  post_type: 'text' | 'image' | 'video' | 'article' | 'poll' | 'job_share' | 'achievement';
  visibility: 'public' | 'connections' | 'private';
  image?: string;
  video?: string;
  article_url?: string;
  poll_options?: PollOption[];
  created_at: string;
  updated_at: string;
  likes_count: number;
  comments_count: number;
  shares_count: number;
  user_has_liked: boolean;
  user_has_saved: boolean;
  hashtags: Hashtag[];
}

export interface PollOption {
  id: number;
  text: string;
  votes_count: number;
  user_has_voted: boolean;
}

export interface Comment {
  id: number;
  post: number;
  author: User;
  content: string;
  created_at: string;
  updated_at: string;
  likes_count: number;
  user_has_liked: boolean;
  parent?: number;
  replies?: Comment[];
  can_edit?: boolean;
  can_delete?: boolean;
}

export interface PostLike {
  id: number;
  user: User;
  post: number;
  created_at: string;
}

export interface PostShare {
  id: number;
  user: User;
  post: number;
  comment?: string;
  created_at: string;
}

export interface Hashtag {
  id: number;
  name: string;
  posts_count: number;
}

export interface SavedPost {
  id: number;
  user: number;
  post: Post;
  saved_at: string;
}

export interface PostFilters {
  search?: string;
  post_type?: string;
  author?: number;
  hashtag?: string;
  date_from?: string;
  date_to?: string;
  ordering?: string;
}

// Job types
export interface Job {
  id: number;
  title: string;
  company: Company;
  location: string;
  job_type: 'full_time' | 'part_time' | 'contract' | 'internship' | 'freelance';
  employment_type: 'remote' | 'on_site' | 'hybrid';
  experience_level: 'intern' | 'entry' | 'associate' | 'mid' | 'senior' | 'executive';
  description: string;
  requirements: string;
  benefits?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  skills_required: Skill[];
  posted_date: string;
  deadline?: string;
  is_active: boolean;
  applications_count: number;
  user_has_applied: boolean;
  user_has_saved: boolean;
  created_by: User;
  category?: string;
}

export interface JobApplication {
  id: number;
  job: Job;
  applicant: User;
  cover_letter: string;
  resume?: string;
  status: 'pending' | 'reviewing' | 'interview' | 'accepted' | 'rejected';
  applied_date: string;
  updated_date: string;
  interview_date?: string;
  feedback?: string;
}

export interface JobFilters {
  search?: string;
  location?: string;
  job_type?: string;
  employment_type?: string;
  experience_level?: string;
  salary_min?: number;
  salary_max?: number;
  company?: number;
  skills?: string;
  date_posted?: string;
  ordering?: string;
}

export interface JobStats {
  applications_sent: number;
  applications_pending: number;
  applications_under_review: number;
  saved_jobs: number;
  jobs_posted: number;
  active_jobs_posted: number;
}

// Company types
export interface Company {
  id: number;
  name: string;
  description: string;
  industry: string;
  size: 'startup' | 'small' | 'medium' | 'large' | 'enterprise';
  location: string;
  website?: string;
  logo?: string;
  cover_image?: string;
  founded_year?: number;
  employees_count?: number;
  created_by: User;
  created_at: string;
  followers_count: number;
  user_is_following: boolean;
}

// Skills and Experience
export interface Skill {
  id: number;
  name: string;
  category?: string;
}

export interface UserSkill {
  id: number;
  user: number;
  skill: Skill;
  proficiency_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  years_of_experience?: number;
  endorsed_count: number;
}

export interface Experience {
  id: number;
  user: number;
  title: string;
  company: string;
  location?: string;
  start_date: string;
  end_date?: string;
  is_current: boolean;
  description?: string;
}

export interface Education {
  id: number;
  user: number;
  institution: string;
  degree: string;
  field_of_study: string;
  start_date: string;
  end_date?: string;
  is_current: boolean;
  grade?: string;
  description?: string;
}

// Connection types
export interface ConnectionRequest {
  id: number;
  sender: User;
  receiver: User;
  message?: string;
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
  updated_at: string;
}

export interface Connection {
  id: number;
  user1: User;
  user2: User;
  connected_at: string;
}

export interface Follow {
  id: number;
  follower: User;
  following: User;
  created_at: string;
}

export interface UserRecommendation {
  user: User;
  mutual_connections: number;
  common_interests: string[];
  recommendation_score: number;
}

export interface NetworkMetrics {
  connections_count: number;
  followers_count: number;
  following_count: number;
  mutual_connections: number;
  profile_views: number;
  search_appearances: number;
}

// Notification types
export interface Notification {
  id: number;
  user: number;
  type: 'like' | 'comment' | 'share' | 'follow' | 'connection_request' | 'job_application' | 'job_update';
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  related_object_id?: number;
  related_object_type?: string;
  action_url?: string;
}

// Feed Stats
export interface FeedStats {
  total_posts: number;
  total_likes: number;
  total_comments: number;
  total_shares: number;
  trending_hashtags: Hashtag[];
}

// API Response types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
}

// Form types
export interface ContactForm {
  name: string;
  email: string;
  subject: string;
  message: string;
}

export interface SearchFilters {
  query?: string;
  type?: 'users' | 'jobs' | 'companies' | 'posts';
  location?: string;
  industry?: string;
  experience_level?: string;
}

export interface SearchResults {
  users: User[];
  jobs: Job[];
  companies: Company[];
  posts: Post[];
  total_count: number;
}
