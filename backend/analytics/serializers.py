from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserActivity, SessionAnalytics, ContentPerformance, PlatformMetrics,
    UserInsights, SearchAnalytics, TrendingContent, RecommendationLog
)

class UserActivitySerializer(serializers.ModelSerializer):
    activity_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'user_name', 'activity_type', 'activity_display',
            'timestamp', 'metadata', 'ip_address', 'duration'
        ]

class SessionAnalyticsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    session_duration_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = SessionAnalytics
        fields = [
            'id', 'user', 'user_name', 'session_id', 'start_time', 'end_time',
            'duration', 'session_duration_formatted', 'device_type', 'browser',
            'operating_system', 'country', 'city', 'pages_visited',
            'actions_performed', 'scroll_depth'
        ]
    
    def get_session_duration_formatted(self, obj):
        if obj.duration:
            hours = obj.duration // 3600
            minutes = (obj.duration % 3600) // 60
            seconds = obj.duration % 60
            if hours:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        return "N/A"

class ContentPerformanceSerializer(serializers.ModelSerializer):
    content_title = serializers.SerializerMethodField()
    engagement_rate_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentPerformance
        fields = [
            'id', 'content_type', 'object_id', 'content_title', 'total_views',
            'unique_views', 'average_view_duration', 'total_likes', 'total_comments',
            'total_shares', 'total_saves', 'engagement_rate', 'engagement_rate_formatted',
            'viral_score', 'views_today', 'views_this_week', 'views_this_month'
        ]
    
    def get_content_title(self, obj):
        if obj.content_object:
            if hasattr(obj.content_object, 'title'):
                return obj.content_object.title
            elif hasattr(obj.content_object, 'content'):
                return obj.content_object.content[:50] + "..." if len(obj.content_object.content) > 50 else obj.content_object.content
            elif hasattr(obj.content_object, 'name'):
                return obj.content_object.name
        return f"{obj.content_type.model} #{obj.object_id}"
    
    def get_engagement_rate_formatted(self, obj):
        return f"{obj.engagement_rate:.2f}%"

class PlatformMetricsSerializer(serializers.ModelSerializer):
    user_growth_rate = serializers.SerializerMethodField()
    engagement_score = serializers.SerializerMethodField()
    
    class Meta:
        model = PlatformMetrics
        fields = [
            'date', 'total_users', 'new_users', 'active_users', 'returning_users',
            'posts_created', 'comments_created', 'likes_given', 'shares_made',
            'jobs_posted', 'applications_submitted', 'messages_sent',
            'connections_made', 'average_session_duration', 'bounce_rate',
            'user_retention_rate', 'user_growth_rate', 'engagement_score'
        ]
    
    def get_user_growth_rate(self, obj):
        if obj.total_users > 0:
            return (obj.new_users / obj.total_users) * 100
        return 0
    
    def get_engagement_score(self, obj):
        if obj.active_users > 0:
            total_actions = obj.posts_created + obj.comments_created + obj.likes_given + obj.shares_made
            return (total_actions / obj.active_users) * 100
        return 0

class UserInsightsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    profile_completion_percentage = serializers.SerializerMethodField()
    network_growth_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = UserInsights
        fields = [
            'user', 'user_name', 'profile_completion_score', 'profile_completion_percentage',
            'profile_views_last_30_days', 'profile_views_growth', 'posts_engagement_rate',
            'content_reach_last_30_days', 'network_size', 'network_growth_last_30_days',
            'network_growth_rate', 'influential_connections_count', 'average_daily_activity',
            'most_active_hour', 'most_active_day', 'job_market_score', 'skill_demand_score',
            'career_progression_score', 'suggested_connections_count', 'suggested_skills_count',
            'suggested_content_count', 'last_updated'
        ]
    
    def get_profile_completion_percentage(self, obj):
        return f"{obj.profile_completion_score:.1f}%"
    
    def get_network_growth_rate(self, obj):
        if obj.network_size > 0:
            return (obj.network_growth_last_30_days / obj.network_size) * 100
        return 0

class SearchAnalyticsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    search_type_display = serializers.CharField(source='get_search_type_display', read_only=True)
    
    class Meta:
        model = SearchAnalytics
        fields = [
            'id', 'user', 'user_name', 'query', 'search_type', 'search_type_display',
            'results_count', 'clicked_result_position', 'timestamp'
        ]

class TrendingContentSerializer(serializers.ModelSerializer):
    trend_type_display = serializers.CharField(source='get_trend_type_display', read_only=True)
    growth_rate_formatted = serializers.SerializerMethodField()
    trend_status = serializers.SerializerMethodField()
    
    class Meta:
        model = TrendingContent
        fields = [
            'id', 'trend_type', 'trend_type_display', 'name', 'mention_count',
            'growth_rate', 'growth_rate_formatted', 'geographic_concentration',
            'mentions_today', 'mentions_this_week', 'mentions_this_month',
            'trend_score', 'trend_status', 'peak_time', 'updated_at'
        ]
    
    def get_growth_rate_formatted(self, obj):
        return f"{obj.growth_rate:+.1f}%"
    
    def get_trend_status(self, obj):
        if obj.growth_rate > 50:
            return "🔥 Hot"
        elif obj.growth_rate > 20:
            return "📈 Rising"
        elif obj.growth_rate > 0:
            return "🟢 Growing"
        elif obj.growth_rate > -10:
            return "⚪ Stable"
        else:
            return "📉 Declining"

class RecommendationLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    recommendation_type_display = serializers.CharField(source='get_recommendation_type_display', read_only=True)
    feedback_display = serializers.CharField(source='get_user_feedback_display', read_only=True)
    content_title = serializers.SerializerMethodField()
    
    class Meta:
        model = RecommendationLog
        fields = [
            'id', 'user', 'user_name', 'recommendation_type', 'recommendation_type_display',
            'content_title', 'algorithm_version', 'confidence_score', 'reasoning',
            'was_shown', 'was_clicked', 'was_dismissed', 'user_feedback',
            'feedback_display', 'created_at', 'interacted_at'
        ]
    
    def get_content_title(self, obj):
        if obj.content_object:
            if hasattr(obj.content_object, 'get_full_name'):
                return obj.content_object.get_full_name()
            elif hasattr(obj.content_object, 'title'):
                return obj.content_object.title
            elif hasattr(obj.content_object, 'name'):
                return obj.content_object.name
            elif hasattr(obj.content_object, 'content'):
                return obj.content_object.content[:50] + "..."
        return f"{obj.content_type.model} #{obj.object_id}"

class ActivitySummarySerializer(serializers.Serializer):
    """Summary of user activity for dashboard"""
    total_activities = serializers.IntegerField()
    activities_today = serializers.IntegerField()
    activities_this_week = serializers.IntegerField()
    most_common_activity = serializers.CharField()
    activity_breakdown = serializers.DictField()
    peak_activity_hour = serializers.IntegerField()

class EngagementMetricsSerializer(serializers.Serializer):
    """Engagement metrics for content creators"""
    total_content_views = serializers.IntegerField()
    average_engagement_rate = serializers.FloatField()
    top_performing_content = serializers.ListField()
    engagement_by_day = serializers.DictField()
    audience_demographics = serializers.DictField()

class PlatformStatsSerializer(serializers.Serializer):
    """Overall platform statistics"""
    total_users = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    total_posts = serializers.IntegerField()
    total_connections = serializers.IntegerField()
    trending_topics = serializers.ListField()
    top_industries = serializers.ListField()
    growth_metrics = serializers.DictField() 