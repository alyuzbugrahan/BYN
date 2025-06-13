from rest_framework import serializers
from accounts.serializers import UserBasicSerializer
from .models import ConnectionRequest, Connection, Follow, UserRecommendation, NetworkMetrics


class ConnectionRequestSerializer(serializers.ModelSerializer):
    sender = UserBasicSerializer(read_only=True)
    receiver = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = ConnectionRequest
        fields = ['id', 'sender', 'receiver', 'message', 'status', 'created_at', 'updated_at', 'responded_at']
        read_only_fields = ['id', 'sender', 'receiver', 'status', 'created_at', 'updated_at', 'responded_at']


class ConnectionSerializer(serializers.ModelSerializer):
    user1 = UserBasicSerializer(read_only=True)
    user2 = UserBasicSerializer(read_only=True)
    connection_request = ConnectionRequestSerializer(read_only=True)
    other_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Connection
        fields = ['id', 'user1', 'user2', 'other_user', 'connection_request', 'interaction_count', 
                 'last_interaction', 'connected_at']
        read_only_fields = ['id', 'user1', 'user2', 'connection_request', 'interaction_count', 
                           'last_interaction', 'connected_at']
    
    def get_other_user(self, obj):
        """Get the other user in the connection relative to the current user"""
        request = self.context.get('request')
        if request and request.user:
            other_user = obj.get_other_user(request.user)
            if other_user:
                return UserBasicSerializer(other_user).data
        return None


class FollowSerializer(serializers.ModelSerializer):
    follower = UserBasicSerializer(read_only=True)
    following = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'follower', 'following', 'created_at']


class UserRecommendationSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    recommended_user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = UserRecommendation
        fields = ['id', 'user', 'recommended_user', 'recommendation_type', 'score', 
                 'is_dismissed', 'is_viewed', 'viewed_at', 'dismissed_at', 'created_at']
        read_only_fields = ['id', 'user', 'recommended_user', 'recommendation_type', 'score', 
                           'is_dismissed', 'is_viewed', 'viewed_at', 'dismissed_at', 'created_at']


class NetworkMetricsSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = NetworkMetrics
        fields = ['id', 'user', 'connection_count', 'follower_count', 'following_count',
                 'mutual_connection_count', 'industry_connection_percentage', 
                 'profile_views_count', 'search_appearances_count', 'post_engagement_rate',
                 'avg_connections_per_month', 'last_calculated']
        read_only_fields = ['id', 'user', 'connection_count', 'follower_count', 'following_count',
                           'mutual_connection_count', 'industry_connection_percentage', 
                           'profile_views_count', 'search_appearances_count', 'post_engagement_rate',
                           'avg_connections_per_month', 'last_calculated'] 