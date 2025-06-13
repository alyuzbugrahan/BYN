from django.db import models
from django.conf import settings


class ConnectionRequest(models.Model):
    REQUEST_STATUS = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_connection_requests')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_connection_requests')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'connection_requests'
        unique_together = ['sender', 'receiver']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['receiver', 'status', 'created_at']),
            models.Index(fields=['sender', 'status']),
        ]
    
    def __str__(self):
        return f"{self.sender.full_name} -> {self.receiver.full_name} ({self.status})"


class Connection(models.Model):
    """Represents an established connection between two users"""
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='connections_as_user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='connections_as_user2')
    connection_request = models.OneToOneField(ConnectionRequest, on_delete=models.CASCADE, related_name='connection')
    
    # Connection strength and interaction tracking
    interaction_count = models.IntegerField(default=0)
    last_interaction = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    connected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'connections'
        unique_together = ['user1', 'user2']
        ordering = ['-connected_at']
        indexes = [
            models.Index(fields=['user1', 'connected_at']),
            models.Index(fields=['user2', 'connected_at']),
        ]
    
    def __str__(self):
        return f"{self.user1.full_name} <-> {self.user2.full_name}"
    
    def get_other_user(self, user):
        """Get the other user in the connection"""
        if user == self.user1:
            return self.user2
        elif user == self.user2:
            return self.user1
        return None


class Follow(models.Model):
    """Represents a one-way follow relationship (like Twitter)"""
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'follows'
        unique_together = ['follower', 'following']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['follower', 'created_at']),
            models.Index(fields=['following', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.follower.full_name} follows {self.following.full_name}"


class Block(models.Model):
    """Represents a block relationship between users"""
    blocker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocked_users')
    blocked = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocked_by_users')
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blocks'
        unique_together = ['blocker', 'blocked']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.blocker.full_name} blocked {self.blocked.full_name}"


class UserRecommendation(models.Model):
    """Stores user recommendations for "People you may know" feature"""
    RECOMMENDATION_TYPES = [
        ('mutual_connections', 'Mutual Connections'),
        ('same_company', 'Same Company'),
        ('same_school', 'Same School'),
        ('similar_skills', 'Similar Skills'),
        ('location_based', 'Location Based'),
        ('industry_based', 'Industry Based'),
        ('email_contact', 'Email Contact'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    recommended_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommended_to')
    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPES)
    score = models.FloatField(default=0.0)  # Recommendation strength score
    
    # Interaction tracking
    is_dismissed = models.BooleanField(default=False)
    is_viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_recommendations'
        unique_together = ['user', 'recommended_user']
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_dismissed', 'score']),
            models.Index(fields=['recommendation_type', 'score']),
        ]
    
    def __str__(self):
        return f"Recommend {self.recommended_user.full_name} to {self.user.full_name} ({self.recommendation_type})"


class NetworkMetrics(models.Model):
    """Stores network statistics for users"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='network_metrics')
    
    # Connection counts
    connection_count = models.IntegerField(default=0)
    follower_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    
    # Network quality metrics
    mutual_connection_count = models.IntegerField(default=0)
    industry_connection_percentage = models.FloatField(default=0.0)
    
    # Profile visibility metrics
    profile_views_count = models.IntegerField(default=0)
    search_appearances_count = models.IntegerField(default=0)
    
    # Engagement metrics
    post_engagement_rate = models.FloatField(default=0.0)
    avg_connections_per_month = models.FloatField(default=0.0)
    
    # Last updated
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'network_metrics'
    
    def __str__(self):
        return f"Network metrics for {self.user.full_name}" 