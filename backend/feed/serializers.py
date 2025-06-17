from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from typing import List, Dict, Optional
from .models import (
    Post, Comment, PostLike, CommentLike, PostShare, 
    Hashtag, SavedPost, Notification, PostReport, FeedAlgorithm
)
from accounts.serializers import UserBasicSerializer
from jobs.serializers import JobBasicSerializer

User = get_user_model()


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ['id', 'name', 'posts_count', 'is_trending']


class PostLikeSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = PostLike
        fields = ['id', 'user', 'reaction_type', 'created_at']


class CommentLikeSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = CommentLike
        fields = ['id', 'user', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    likes = CommentLikeSerializer(many=True, read_only=True)
    mentioned_users = UserBasicSerializer(many=True, read_only=True)
    replies = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'content', 'image', 'parent', 'likes_count',
            'replies_count', 'created_at', 'updated_at', 'likes',
            'mentioned_users', 'replies', 'user_has_liked', 'is_reply',
            'can_edit', 'can_delete'
        ]
        read_only_fields = ['likes_count', 'replies_count', 'created_at', 'updated_at']
    
    @extend_schema_field(List[Dict])
    def get_replies(self, obj) -> List[Dict]:
        # Defensive: avoid schema and runtime errors if replies is not a related manager
        if getattr(self, 'swagger_fake_view', False):
            return []
        replies_manager = getattr(obj, 'replies', None)
        if replies_manager is not None and hasattr(replies_manager, 'all'):
            try:
                return CommentSerializer(replies_manager.all()[:5], many=True, context=self.context).data
            except Exception:
                return []
        return []
    
    @extend_schema_field(bool)
    def get_user_has_liked(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    @extend_schema_field(bool)
    def get_can_edit(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False
    
    @extend_schema_field(bool)
    def get_can_delete(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user or request.user.is_staff
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    mentioned_users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        many=True, 
        required=False
    )
    
    class Meta:
        model = Comment
        fields = ['content', 'image', 'parent', 'mentioned_users']
    
    def validate_content(self, value):
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Comment cannot be empty.")
        return value
    
    def create(self, validated_data):
        mentioned_users = validated_data.pop('mentioned_users', [])
        comment = Comment.objects.create(**validated_data)
        comment.mentioned_users.set(mentioned_users)
        return comment


class PostShareSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = PostShare
        fields = ['id', 'user', 'share_content', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    shared_job = JobBasicSerializer(read_only=True)
    hashtags = HashtagSerializer(many=True, read_only=True)
    mentioned_users = UserBasicSerializer(many=True, read_only=True)
    likes = PostLikeSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    shares = PostShareSerializer(many=True, read_only=True)
    
    # User-specific fields
    user_has_liked = serializers.SerializerMethodField()
    user_has_shared = serializers.SerializerMethodField()
    user_has_saved = serializers.SerializerMethodField()
    user_reaction_type = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    # Computed fields
    time_since_posted = serializers.SerializerMethodField()
    top_comments = serializers.SerializerMethodField()
    engagement_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'post_type', 'visibility',
            'image', 'video', 'document', 'article_title', 'article_url',
            'article_description', 'article_image', 'shared_job',
            'likes_count', 'comments_count', 'shares_count', 'views_count',
            'is_pinned', 'is_featured', 'hashtags', 'mentioned_users',
            'created_at', 'updated_at', 'likes', 'comments', 'shares',
            'user_has_liked', 'user_has_shared', 'user_has_saved',
            'user_reaction_type', 'can_edit', 'can_delete', 'time_since_posted',
            'top_comments', 'engagement_score', 'engagement_rate'
        ]
        read_only_fields = [
            'likes_count', 'comments_count', 'shares_count', 'views_count',
            'created_at', 'updated_at'
        ]
    
    @extend_schema_field(bool)
    def get_user_has_liked(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    @extend_schema_field(bool)
    def get_can_edit(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False
    
    @extend_schema_field(bool)
    def get_can_delete(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user or request.user.is_staff
        return False
    
    @extend_schema_field(bool)
    def get_user_has_shared(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shares.filter(user=request.user).exists()
        return False
    
    @extend_schema_field(bool)
    def get_user_has_saved(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.saved_by.filter(user=request.user).exists()
        return False
    
    @extend_schema_field(str)
    def get_user_reaction_type(self, obj) -> Optional[str]:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            like = obj.likes.filter(user=request.user).first()
            return like.reaction_type if like else None
        return None
    
    @extend_schema_field(str)
    def get_time_since_posted(self, obj) -> str:
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 365:
            return f"{diff.days // 365}y"
        elif diff.days > 30:
            return f"{diff.days // 30}mo"
        elif diff.days > 0:
            return f"{diff.days}d"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m"
        else:
            return "now"
    
    @extend_schema_field(List[Dict])
    def get_top_comments(self, obj) -> List[Dict]:
        top_comments = obj.comments.filter(parent=None).order_by('-likes_count')[:3]
        return CommentSerializer(top_comments, many=True, context=self.context).data
    
    @extend_schema_field(float)
    def get_engagement_score(self, obj) -> float:
        return float(obj.engagement_score)


class PostCreateSerializer(serializers.ModelSerializer):
    hashtags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True
    )
    mentioned_users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False
    )
    shared_job_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Post
        fields = [
            'content', 'post_type', 'visibility', 'image', 'video', 'document',
            'article_title', 'article_url', 'article_description', 'article_image',
            'hashtags', 'mentioned_users', 'shared_job_id'
        ]
    
    def validate_content(self, value):
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError("Post content cannot be empty.")
        if len(value) > 3000:
            raise serializers.ValidationError("Post content cannot exceed 3000 characters.")
        return value
    
    def validate(self, data):
        post_type = data.get('post_type', 'text')
        
        # Validate based on post type
        if post_type == 'article':
            if not data.get('article_url'):
                raise serializers.ValidationError("Article posts must include an article URL.")
        
        if post_type == 'job_share':
            if not data.get('shared_job_id'):
                raise serializers.ValidationError("Job share posts must include a job ID.")
        
        return data
    
    def create(self, validated_data):
        hashtags_data = validated_data.pop('hashtags', [])
        mentioned_users = validated_data.pop('mentioned_users', [])
        shared_job_id = validated_data.pop('shared_job_id', None)
        
        # Handle shared job
        if shared_job_id:
            from jobs.models import Job
            try:
                shared_job = Job.objects.get(id=shared_job_id)
                validated_data['shared_job'] = shared_job
            except Job.DoesNotExist:
                raise serializers.ValidationError("Invalid job ID for sharing.")
        
        post = Post.objects.create(**validated_data)
        
        # Handle hashtags
        for hashtag_name in hashtags_data:
            hashtag_name = hashtag_name.lower().strip('#').replace(' ', '')
            if hashtag_name:
                hashtag, created = Hashtag.objects.get_or_create(name=hashtag_name)
                hashtag.posts_count += 1
                hashtag.save()
                post.hashtags.add(hashtag)
        
        # Handle mentioned users
        post.mentioned_users.set(mentioned_users)
        
        return post


class PostUpdateSerializer(serializers.ModelSerializer):
    hashtags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True
    )
    mentioned_users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False
    )
    
    class Meta:
        model = Post
        fields = [
            'content', 'visibility', 'image', 'video', 'document',
            'article_title', 'article_url', 'article_description', 'article_image',
            'hashtags', 'mentioned_users'
        ]
    
    def update(self, instance, validated_data):
        hashtags_data = validated_data.pop('hashtags', None)
        mentioned_users = validated_data.pop('mentioned_users', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update hashtags if provided
        if hashtags_data is not None:
            # Remove old hashtags
            for hashtag in instance.hashtags.all():
                hashtag.posts_count = max(0, hashtag.posts_count - 1)
                hashtag.save()
            instance.hashtags.clear()
            
            # Add new hashtags
            for hashtag_name in hashtags_data:
                hashtag_name = hashtag_name.lower().strip('#').replace(' ', '')
                if hashtag_name:
                    hashtag, created = Hashtag.objects.get_or_create(name=hashtag_name)
                    hashtag.posts_count += 1
                    hashtag.save()
                    instance.hashtags.add(hashtag)
        
        # Update mentioned users if provided
        if mentioned_users is not None:
            instance.mentioned_users.set(mentioned_users)
        
        return instance


class PostLikeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ['reaction_type']


class PostShareCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostShare
        fields = ['share_content']


class SavedPostSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)
    
    class Meta:
        model = SavedPost
        fields = ['id', 'post', 'saved_at']


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserBasicSerializer(read_only=True)
    post = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'sender', 'notification_type', 'title', 'message',
            'is_read', 'created_at', 'action_url', 'post', 'comment'
        ]
    
    @extend_schema_field(Dict)
    def get_post(self, obj) -> Optional[Dict]:
        if obj.post:
            return {
                'id': obj.post.id,
                'content': obj.post.content[:100],
                'author': obj.post.author.full_name
            }
        return None
    
    @extend_schema_field(Dict)
    def get_comment(self, obj) -> Optional[Dict]:
        if obj.comment:
            return {
                'id': obj.comment.id,
                'content': obj.comment.content[:100],
                'author': obj.comment.author.full_name
            }
        return None


class PostReportSerializer(serializers.ModelSerializer):
    reporter = UserBasicSerializer(read_only=True)
    post = serializers.SerializerMethodField()
    
    class Meta:
        model = PostReport
        fields = [
            'id', 'reporter', 'reason', 'description', 'is_reviewed',
            'action_taken', 'created_at', 'post'
        ]
    
    def get_post(self, obj):
        return {
            'id': obj.post.id,
            'content': obj.post.content[:100],
            'author': obj.post.author.full_name
        }


class PostReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReport
        fields = ['reason', 'description']
    
    def validate_description(self, value):
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Please provide a detailed description (at least 10 characters).")
        return value


class FeedAlgorithmSerializer(serializers.ModelSerializer):
    muted_users = UserBasicSerializer(many=True, read_only=True)
    muted_hashtags = HashtagSerializer(many=True, read_only=True)
    
    class Meta:
        model = FeedAlgorithm
        fields = [
            'connection_weight', 'engagement_weight', 'recency_weight',
            'similarity_weight', 'trending_weight', 'show_promoted_content',
            'show_job_posts', 'show_company_updates', 'show_achievement_posts',
            'muted_users', 'muted_hashtags', 'updated_at'
        ]


class FeedAlgorithmUpdateSerializer(serializers.ModelSerializer):
    muted_users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False
    )
    muted_hashtags = serializers.PrimaryKeyRelatedField(
        queryset=Hashtag.objects.all(),
        many=True,
        required=False
    )
    
    class Meta:
        model = FeedAlgorithm
        fields = [
            'connection_weight', 'engagement_weight', 'recency_weight',
            'similarity_weight', 'trending_weight', 'show_promoted_content',
            'show_job_posts', 'show_company_updates', 'show_achievement_posts',
            'muted_users', 'muted_hashtags'
        ]
    
    def validate(self, data):
        # Ensure weights sum to approximately 1.0
        weights = [
            data.get('connection_weight', 0.3),
            data.get('engagement_weight', 0.2),
            data.get('recency_weight', 0.2),
            data.get('similarity_weight', 0.15),
            data.get('trending_weight', 0.15)
        ]
        
        total_weight = sum(weights)
        if not (0.8 <= total_weight <= 1.2):  # Allow some flexibility
            raise serializers.ValidationError(
                "Algorithm weights should sum to approximately 1.0. "
                f"Current sum: {total_weight:.2f}"
            )
        
        return data


class TrendingTopicsSerializer(serializers.Serializer):
    """Serializer for trending topics response"""
    hashtags = HashtagSerializer(many=True)
    topics = serializers.ListField(child=serializers.CharField())
    user_interests = serializers.ListField(child=serializers.CharField())


class FeedStatsSerializer(serializers.Serializer):
    """Serializer for feed statistics"""
    posts_today = serializers.IntegerField()
    posts_this_week = serializers.IntegerField()
    total_likes_received = serializers.IntegerField()
    total_comments_received = serializers.IntegerField()
    total_shares_received = serializers.IntegerField()
    engagement_rate = serializers.FloatField()
    top_performing_post = PostSerializer() 