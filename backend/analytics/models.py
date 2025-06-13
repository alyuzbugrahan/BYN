from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid

User = get_user_model()

class UserActivity(models.Model):
    """
    Track detailed user activities for analytics
    """
    ACTIVITY_TYPES = (
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('profile_view', 'Profile View'),
        ('profile_edit', 'Profile Edit'),
        ('post_create', 'Post Created'),
        ('post_view', 'Post Viewed'),
        ('post_like', 'Post Liked'),
        ('post_share', 'Post Shared'),
        ('post_comment', 'Post Commented'),
        ('job_view', 'Job Viewed'),
        ('job_apply', 'Job Applied'),
        ('job_save', 'Job Saved'),
        ('company_follow', 'Company Followed'),
        ('user_follow', 'User Followed'),
        ('search', 'Search Performed'),
        ('message_send', 'Message Sent'),
        ('message_read', 'Message Read'),
        ('notification_click', 'Notification Clicked'),
        ('feed_scroll', 'Feed Scrolled'),
        ('page_visit', 'Page Visited'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Generic foreign key to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    duration = models.IntegerField(blank=True, null=True)  # in seconds
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['activity_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_activity_type_display()}"

class SessionAnalytics(models.Model):
    """
    Track user sessions for engagement metrics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_id = models.CharField(max_length=100, unique=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)  # in seconds
    
    # Device and browser info
    device_type = models.CharField(max_length=50, blank=True)  # mobile, desktop, tablet
    browser = models.CharField(max_length=100, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)
    screen_resolution = models.CharField(max_length=20, blank=True)
    
    # Location data
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    
    # Engagement metrics
    pages_visited = models.IntegerField(default=0)
    actions_performed = models.IntegerField(default=0)
    scroll_depth = models.FloatField(default=0.0)  # Average scroll depth
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Session {self.session_id[:8]}"

class ContentPerformance(models.Model):
    """
    Track performance metrics for content (posts, jobs, etc.)
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # View metrics
    total_views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)
    average_view_duration = models.FloatField(default=0.0)
    
    # Engagement metrics
    total_likes = models.IntegerField(default=0)
    total_comments = models.IntegerField(default=0)
    total_shares = models.IntegerField(default=0)
    total_saves = models.IntegerField(default=0)
    
    # Time-based metrics
    views_today = models.IntegerField(default=0)
    views_this_week = models.IntegerField(default=0)
    views_this_month = models.IntegerField(default=0)
    
    engagement_rate = models.FloatField(default=0.0)  # (likes + comments + shares) / views
    viral_score = models.FloatField(default=0.0)  # Custom algorithm for viral content
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['content_type', 'object_id']
    
    def __str__(self):
        return f"Performance for {self.content_object}"
    
    def update_engagement_rate(self):
        total_engagement = self.total_likes + self.total_comments + self.total_shares
        if self.total_views > 0:
            self.engagement_rate = (total_engagement / self.total_views) * 100
        else:
            self.engagement_rate = 0.0
        self.save()

class PlatformMetrics(models.Model):
    """
    Daily platform-wide metrics
    """
    date = models.DateField(unique=True)
    
    # User metrics
    total_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)  # Users who performed any action
    returning_users = models.IntegerField(default=0)
    
    # Content metrics
    posts_created = models.IntegerField(default=0)
    comments_created = models.IntegerField(default=0)
    likes_given = models.IntegerField(default=0)
    shares_made = models.IntegerField(default=0)
    
    # Job metrics
    jobs_posted = models.IntegerField(default=0)
    applications_submitted = models.IntegerField(default=0)
    
    # Engagement metrics
    messages_sent = models.IntegerField(default=0)
    connections_made = models.IntegerField(default=0)
    
    # Platform health
    average_session_duration = models.FloatField(default=0.0)
    bounce_rate = models.FloatField(default=0.0)
    user_retention_rate = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Platform metrics for {self.date}"

class UserInsights(models.Model):
    """
    Personalized insights for individual users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='insights')
    
    # Profile completion and optimization
    profile_completion_score = models.FloatField(default=0.0)
    profile_views_last_30_days = models.IntegerField(default=0)
    profile_views_growth = models.FloatField(default=0.0)  # % change from previous period
    
    # Content performance
    posts_engagement_rate = models.FloatField(default=0.0)
    top_performing_post_id = models.CharField(max_length=100, blank=True)
    content_reach_last_30_days = models.IntegerField(default=0)
    
    # Network insights
    network_size = models.IntegerField(default=0)
    network_growth_last_30_days = models.IntegerField(default=0)
    influential_connections_count = models.IntegerField(default=0)
    
    # Activity insights
    average_daily_activity = models.FloatField(default=0.0)
    most_active_hour = models.IntegerField(blank=True, null=True)  # 0-23
    most_active_day = models.IntegerField(blank=True, null=True)  # 0-6 (Mon-Sun)
    
    # Career insights
    job_market_score = models.FloatField(default=0.0)  # How attractive user is to recruiters
    skill_demand_score = models.FloatField(default=0.0)  # How in-demand user's skills are
    career_progression_score = models.FloatField(default=0.0)
    
    # Recommendations
    suggested_connections_count = models.IntegerField(default=0)
    suggested_skills_count = models.IntegerField(default=0)
    suggested_content_count = models.IntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Insights for {self.user.get_full_name()}"

class SearchAnalytics(models.Model):
    """
    Track search behavior and trends
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    query = models.CharField(max_length=500)
    search_type = models.CharField(max_length=20, choices=[
        ('people', 'People'),
        ('jobs', 'Jobs'),
        ('companies', 'Companies'),
        ('posts', 'Posts'),
        ('general', 'General'),
    ])
    results_count = models.IntegerField(default=0)
    clicked_result_position = models.IntegerField(blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Search: {self.query} ({self.search_type})"

class TrendingContent(models.Model):
    """
    Track trending hashtags, topics, and content
    """
    TREND_TYPES = (
        ('hashtag', 'Hashtag'),
        ('topic', 'Topic'),
        ('skill', 'Skill'),
        ('company', 'Company'),
        ('industry', 'Industry'),
    )
    
    trend_type = models.CharField(max_length=20, choices=TREND_TYPES)
    name = models.CharField(max_length=200)
    mention_count = models.IntegerField(default=0)
    growth_rate = models.FloatField(default=0.0)  # % growth in mentions
    geographic_concentration = models.CharField(max_length=100, blank=True)
    
    # Time-based metrics
    mentions_today = models.IntegerField(default=0)
    mentions_this_week = models.IntegerField(default=0)
    mentions_this_month = models.IntegerField(default=0)
    
    trend_score = models.FloatField(default=0.0)  # Algorithm-based trending score
    peak_time = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['trend_type', 'name']
        ordering = ['-trend_score']
    
    def __str__(self):
        return f"Trending {self.trend_type}: {self.name}"

class RecommendationLog(models.Model):
    """
    Track recommendation algorithm performance
    """
    RECOMMENDATION_TYPES = (
        ('people', 'People You May Know'),
        ('jobs', 'Recommended Jobs'),
        ('posts', 'Recommended Posts'),
        ('companies', 'Companies to Follow'),
        ('skills', 'Skills to Add'),
        ('courses', 'Recommended Courses'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    
    # Recommended content
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Algorithm metadata
    algorithm_version = models.CharField(max_length=50)
    confidence_score = models.FloatField()  # How confident the algorithm is
    reasoning = models.JSONField(default=dict)  # Why this was recommended
    
    # User interaction
    was_shown = models.BooleanField(default=False)
    was_clicked = models.BooleanField(default=False)
    was_dismissed = models.BooleanField(default=False)
    user_feedback = models.CharField(max_length=20, blank=True, choices=[
        ('helpful', 'Helpful'),
        ('not_relevant', 'Not Relevant'),
        ('already_known', 'Already Known'),
        ('not_interested', 'Not Interested'),
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    interacted_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Recommendation for {self.user.get_full_name()}: {self.recommendation_type}" 