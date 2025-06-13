from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone


class Post(models.Model):
    POST_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('article', 'Article'),
        ('poll', 'Poll'),
        ('job_share', 'Job Share'),
        ('achievement', 'Achievement'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('connections', 'Connections Only'),
        ('private', 'Private'),
    ]
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=3000)
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='text')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    
    # Media fields
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    document = models.FileField(upload_to='posts/documents/', blank=True, null=True)
    
    # Article/Link sharing
    article_title = models.CharField(max_length=300, blank=True)
    article_url = models.URLField(blank=True)
    article_description = models.TextField(max_length=500, blank=True)
    article_image = models.URLField(blank=True)
    
    # Job sharing
    shared_job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, blank=True, null=True, related_name='shared_posts')
    
    # Engagement metrics
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    
    # Flags and moderation
    is_pinned = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    
    # SEO and discovery
    hashtags = models.ManyToManyField('Hashtag', blank=True)
    mentioned_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='mentioned_in_posts')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['post_type', '-created_at']),
            models.Index(fields=['visibility', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.author.full_name} - {self.post_type} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def get_absolute_url(self):
        return f"/feed/post/{self.pk}/"
    
    @property
    def engagement_rate(self):
        """Calculate engagement rate as percentage"""
        if self.views_count == 0:
            return 0
        total_engagement = self.likes_count + self.comments_count + self.shares_count
        return (total_engagement / self.views_count) * 100
    
    def can_view(self, user):
        """Check if user can view this post based on visibility settings"""
        if self.visibility == 'public':
            return True
        elif self.visibility == 'private':
            return user == self.author
        elif self.visibility == 'connections':
            # Check if user is connected to author
            return user == self.author or user.received_connections.filter(
                sender=self.author, status='accepted'
            ).exists() or user.sent_connections.filter(
                receiver=self.author, status='accepted'
            ).exists()
        return False


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='replies'
    )
    
    # Media in comments
    image = models.ImageField(upload_to='comments/images/', blank=True, null=True)
    
    # Engagement
    likes_count = models.PositiveIntegerField(default=0)
    replies_count = models.PositiveIntegerField(default=0)
    
    # Moderation
    is_reported = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    
    mentioned_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='mentioned_in_comments')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['parent', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.full_name} on {self.post}"
    
    @property
    def is_reply(self):
        return self.parent is not None


class Like(models.Model):
    """Generic like model that can be used for posts, comments, etc."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    
    # Generic foreign key to allow liking different types of content
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'likes'
        unique_together = ['user', 'content_type', 'object_id']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} liked {self.content_object}"


class PostView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    view_duration = models.PositiveIntegerField(default=0)  # in seconds
    
    class Meta:
        db_table = 'post_views'
        indexes = [
            models.Index(fields=['post', '-viewed_at']),
            models.Index(fields=['user', '-viewed_at']),
        ]
    
    def __str__(self):
        viewer = self.user.full_name if self.user else "Anonymous"
        return f"{viewer} viewed {self.post}"


class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    posts_count = models.PositiveIntegerField(default=0)
    is_trending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'hashtags'
        ordering = ['-posts_count', 'name']
    
    def __str__(self):
        return f"#{self.name}"
    
    def save(self, *args, **kwargs):
        self.name = self.name.lower().replace(' ', '')
        super().save(*args, **kwargs)


class PostHashtag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'post_hashtags'
        unique_together = ['post', 'hashtag']


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'Post Like'),
        ('comment', 'Comment'),
        ('share', 'Post Share'),
        ('follow', 'New Follower'),
        ('mention', 'Mention'),
        ('job_application', 'Job Application'),
        ('connection_request', 'Connection Request'),
        ('post_approved', 'Post Approved'),
        ('system', 'System Notification'),
    ]
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200, default='Notification')
    message = models.TextField(max_length=500, default='You have a new notification')
    
    # Related objects
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    
    # URL for action
    action_url = models.URLField(blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_sent_email = models.BooleanField(default=False)
    is_sent_push = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"Notification for {self.recipient.full_name}: {self.title}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class PostReport(models.Model):
    REPORT_REASONS = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('misinformation', 'Misinformation'),
        ('copyright', 'Copyright Violation'),
        ('violence', 'Violence or Threats'),
        ('hate_speech', 'Hate Speech'),
        ('fake_news', 'Fake News'),
        ('other', 'Other'),
    ]
    
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(max_length=500, blank=True)
    is_reviewed = models.BooleanField(default=False)
    action_taken = models.CharField(max_length=100, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['reporter', 'post']
    
    def __str__(self):
        return f"Report by {self.reporter.full_name} - {self.reason}"


class SavedPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.full_name} saved {self.post}"


class FeedAlgorithm(models.Model):
    """Model to store feed algorithm weights and preferences per user"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feed_preferences')
    
    # Algorithm weights (0.0 to 1.0)
    connection_weight = models.FloatField(default=0.3)  # Posts from connections
    engagement_weight = models.FloatField(default=0.2)  # Highly engaged posts
    recency_weight = models.FloatField(default=0.2)     # Recent posts
    similarity_weight = models.FloatField(default=0.15) # Similar interests
    trending_weight = models.FloatField(default=0.15)   # Trending content
    
    # User preferences
    show_promoted_content = models.BooleanField(default=True)
    show_job_posts = models.BooleanField(default=True)
    show_company_updates = models.BooleanField(default=True)
    show_achievement_posts = models.BooleanField(default=True)
    
    # Feed filters
    muted_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='muted_by')
    muted_hashtags = models.ManyToManyField(Hashtag, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Feed preferences for {self.user.full_name}"


class PostLike(models.Model):
    REACTION_TYPES = [
        ('like', '👍 Like'),
        ('love', '❤️ Love'),
        ('laugh', '😂 Laugh'),
        ('wow', '😮 Wow'),
        ('sad', '😢 Sad'),
        ('angry', '😠 Angry'),
        ('celebrate', '🎉 Celebrate'),
        ('support', '🤝 Support'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES, default='like')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} {self.reaction_type} {self.post}"


class CommentLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'comment']
    
    def __str__(self):
        return f"{self.user.full_name} likes comment by {self.comment.author.full_name}"


class PostShare(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    share_content = models.TextField(max_length=500, blank=True)  # Optional comment when sharing
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} shared {self.post}" 