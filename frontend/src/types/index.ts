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
  document?: string;
  article_title?: string;
  article_url?: string;
  article_description?: string;
  article_image?: string;
  shared_job?: Job;
  hashtags: Hashtag[];
  mentioned_users: User[];
  likes_count: number;
  comments_count: number;
  shares_count: number;
  views_count: number;
  is_pinned: boolean;
  is_featured: boolean;
  is_reported: boolean;
  is_approved: boolean;
  created_at: string;
  updated_at: string;
  user_has_liked?: boolean;
  user_has_saved?: boolean;
  user_reaction?: string;
  can_edit?: boolean;
  can_delete?: boolean;
  engagement_rate: number;
  top_comments?: Comment[];
  engagement_score: number;
}

export interface Comment {
  id: number;
  post: number;
  author: User;
  content: string;
  parent?: number;
  likes_count: number;
  replies_count: number;
  created_at: string;
  updated_at: string;
  user_has_liked?: boolean;
  can_edit?: boolean;
  can_delete?: boolean;
  replies?: Comment[];
}

export interface PostLike {
  id: number;
  user: User;
  post: Post;
  reaction_type: 'like' | 'love' | 'celebrate' | 'support' | 'funny' | 'angry' | 'sad' | 'dislike';
  created_at: string;
}

export interface PostShare {
  id: number;
  user: User;
  post: Post;
  share_type: 'share' | 'repost';
  comment?: string;
  created_at: string;
}

export interface Hashtag {
  id: number;
  name: string;
  posts_count: number;
  is_trending: boolean;
  created_at: string;
}

export interface SavedPost {
  id: number;
  user: User;
  post: Post;
  created_at: string;
}

export interface Notification {
  id: number;
  recipient: User;
  sender: User;
  notification_type: 'like' | 'comment' | 'share' | 'mention' | 'follow' | 'connection_request' | 'job_application' | 'job_match';
  title: string;
  message: string;
  post?: Post;
  comment?: Comment;
  action_url?: string;
  is_read: boolean;
  created_at: string;
}

// Job types
export interface Job {
  id: number;
  title: string;
  slug: string;
  description: string;
  requirements?: string;
  responsibilities?: string;
  company: Company;
  location: string;
  workplace_type: 'remote' | 'on_site' | 'hybrid';
  job_type: 'full_time' | 'part_time' | 'contract' | 'internship';
  experience_level: 'intern' | 'entry' | 'associate' | 'mid' | 'senior' | 'executive';
  category?: JobCategory;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  salary_type?: 'yearly' | 'monthly' | 'hourly';
  skills_required: Skill[];
  skills_preferred: Skill[];
  is_active: boolean;
  is_featured: boolean;
  posted_by: User;
  application_deadline?: string;
  view_count: number;
  application_count: number;
  created_at: string;
  updated_at: string;
  is_saved?: boolean;
  has_applied?: boolean;
}

export interface JobCategory {
  id: number;
  name: string;
  slug: string;
  description?: string;
}

export interface JobApplication {
  id: number;
  job: Job;
  applicant: User;
  cover_letter?: string;
  resume?: string;
  portfolio_url?: string;
  status: 'submitted' | 'under_review' | 'interviewed' | 'hired' | 'rejected' | 'withdrawn';
  applied_date: string;
  status_updated_at?: string;
}

// Company types
export interface Company {
  id: number;
  name: string;
  slug: string;
  description?: string;
  website?: string;
  industry?: Industry;
  company_size: string;
  founded_year?: number;
  headquarters?: string;
  logo?: string;
  cover_image?: string;
  is_verified: boolean;
  follower_count: number;
  created_at: string;
  is_following?: boolean;
  job_count?: number;
}

export interface Industry {
  id: number;
  name: string;
}

// Skill types
export interface Skill {
  id: number;
  name: string;
}

export interface UserSkill {
  id: number;
  skill: Skill;
  user: User;
  created_at: string;
}

// Experience and Education types
export interface Experience {
  id: number;
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
  school: string;
  degree: string;
  field_of_study?: string;
  start_year: number;
  end_year?: number;
  description?: string;
}

// API Response types
export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface ApiError {
  message: string;
  detail?: string;
  errors?: Record<string, string[]>;
}

// Filter types
export interface JobFilters {
  search?: string;
  location?: string;
  company_name?: string;
  job_type?: string[];
  workplace_type?: string[];
  experience_level?: string[];
  skills?: string;
  salary_min?: number;
  salary_max?: number;
  posted_after?: string;
  is_featured?: boolean;
  ordering?: string;
  page?: number;
}

export interface PostFilters {
  search?: string;
  post_type?: string;
  hashtag?: string;
  author?: number;
  ordering?: string;
  page?: number;
}

// Statistics types
export interface JobStats {
  applications_sent: number;
  applications_pending: number;
  applications_under_review: number;
  saved_jobs: number;
  jobs_posted: number;
  active_jobs_posted: number;
  total_applications_received?: number;
  new_applications?: number;
}

export interface FeedStats {
  posts_today: number;
  posts_this_week: number;
  total_likes_received: number;
  total_comments_received: number;
  total_shares_received: number;
  engagement_rate: number;
  top_performing_post?: Post;
}

// Connections types
export interface ConnectionRequest {
  id: number;
  sender: User;
  receiver: User;
  message?: string;
  status: 'pending' | 'accepted' | 'declined' | 'withdrawn';
  created_at: string;
  updated_at: string;
  responded_at?: string;
}

export interface Connection {
  id: number;
  user1: User;
  user2: User;
  connection_request: ConnectionRequest;
  interaction_count: number;
  last_interaction?: string;
  connected_at: string;
}

export interface Follow {
  id: number;
  follower: User;
  following: User;
  created_at: string;
}

export interface UserRecommendation {
  id: number;
  user: User;
  recommended_user: User;
  recommendation_type: 'mutual_connections' | 'same_company' | 'same_school' | 'similar_skills' | 'location_based' | 'industry_based' | 'email_contact';
  score: number;
  is_dismissed: boolean;
  is_viewed: boolean;
  viewed_at?: string;
  dismissed_at?: string;
  created_at: string;
}

export interface NetworkMetrics {
  user: User;
  connection_count: number;
  follower_count: number;
  following_count: number;
  mutual_connection_count: number;
  industry_connection_percentage: number;
  profile_views_count: number;
  search_appearances_count: number;
  post_engagement_rate: number;
  avg_connections_per_month: number;
  last_calculated: string;
}



// Premium types
export interface SubscriptionPlan {
  id: number;
  name: string;
  plan_type: 'free' | 'basic' | 'premium' | 'business' | 'sales_navigator' | 'recruiter';
  description: string;
  monthly_price: string;
  yearly_price: string;
  yearly_discount_percentage: number;
  profile_views_per_month: number;
  inmails_per_month: number;
  search_results_per_search: number;
  advanced_search_filters: boolean;
  can_see_who_viewed_profile: boolean;
  can_see_full_name_of_viewers: boolean;
  priority_customer_support: boolean;
  learning_access: boolean;
  insights_and_analytics: boolean;
  company_page_analytics: boolean;
  lead_generation_tools: boolean;
  competitor_insights: boolean;
  recruiter_search_tools: boolean;
  talent_pipeline: boolean;
  advanced_reporting: boolean;
  is_active: boolean;
  display_order: number;
  created_at: string;
  yearly_savings: string;
}

export interface UserSubscription {
  id: string;
  user: User;
  plan: SubscriptionPlan;
  status: 'active' | 'cancelled' | 'expired' | 'paused' | 'pending' | 'trial';
  billing_cycle: 'monthly' | 'yearly' | 'lifetime';
  start_date: string;
  end_date?: string;
  trial_end_date?: string;
  next_billing_date?: string;
  profile_views_used: number;
  inmails_used: number;
  last_usage_reset: string;
  stripe_subscription_id?: string;
  stripe_customer_id?: string;
  auto_renew: boolean;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  days_remaining?: number;
  is_trial: boolean;
}

export interface PremiumFeature {
  id: number;
  name: string;
  feature_type: 'profile' | 'search' | 'messaging' | 'analytics' | 'learning' | 'business';
  description: string;
  code: string;
  available_plans: SubscriptionPlan[];
  is_active: boolean;
  created_at: string;
}

export interface BillingHistory {
  id: string;
  subscription: string;
  transaction_type: 'payment' | 'refund' | 'credit' | 'proration';
  amount: string;
  currency: string;
  status: 'succeeded' | 'failed' | 'pending' | 'refunded';
  stripe_payment_intent_id?: string;
  stripe_invoice_id?: string;
  description?: string;
  billing_period_start?: string;
  billing_period_end?: string;
  created_at: string;
}

// Analytics types
export interface UserActivity {
  id: string;
  user: User;
  activity_type: 'login' | 'logout' | 'profile_view' | 'profile_edit' | 'post_create' | 'post_view' | 'post_like' | 'post_share' | 'post_comment' | 'job_view' | 'job_apply' | 'job_save' | 'company_follow' | 'user_follow' | 'search' | 'message_send' | 'message_read' | 'notification_click' | 'feed_scroll' | 'page_visit';
  timestamp: string;
  metadata: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  session_id?: string;
  duration?: number;
}

export interface SessionAnalytics {
  id: string;
  user: User;
  session_id: string;
  start_time: string;
  end_time?: string;
  duration?: number;
  device_type?: string;
  browser?: string;
  operating_system?: string;
  screen_resolution?: string;
  country?: string;
  city?: string;
  timezone?: string;
  pages_visited: number;
  actions_performed: number;
  scroll_depth: number;
}

export interface UserInsights {
  user: User;
  profile_completion_score: number;
  profile_views_last_30_days: number;
  profile_views_growth: number;
  posts_engagement_rate: number;
  top_performing_post_id?: string;
  content_reach_last_30_days: number;
  network_size: number;
  network_growth_last_30_days: number;
  influential_connections_count: number;
  average_daily_activity: number;
  most_active_hour?: number;
  most_active_day?: number;
  job_market_score: number;
  skill_demand_score: number;
  career_progression_score: number;
  suggested_connections_count: number;
  suggested_skills_count: number;
  suggested_content_count: number;
  last_updated: string;
}

export interface PlatformMetrics {
  date: string;
  total_users: number;
  new_users: number;
  active_users: number;
  returning_users: number;
  posts_created: number;
  comments_created: number;
  likes_given: number;
  shares_made: number;
  jobs_posted: number;
  applications_submitted: number;
  messages_sent: number;
  connections_made: number;
  average_session_duration: number;
  bounce_rate: number;
  user_retention_rate: number;
  created_at: string;
}

export interface TrendingContent {
  id: number;
  trend_type: 'hashtag' | 'topic' | 'skill' | 'company' | 'industry';
  name: string;
  mention_count: number;
  growth_rate: number;
  geographic_concentration?: string;
  mentions_today: number;
  mentions_this_week: number;
  mentions_this_month: number;
  trend_score: number;
  peak_time?: string;
  created_at: string;
  updated_at: string;
} 