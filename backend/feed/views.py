from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count, Avg, F, Case, When, IntegerField, FloatField
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import (
    Post, Comment, PostLike, CommentLike, PostShare, 
    Hashtag, SavedPost, Notification, PostReport, FeedAlgorithm, PostView
)
from .serializers import (
    PostSerializer, PostCreateSerializer, PostUpdateSerializer,
    CommentSerializer, CommentCreateSerializer, PostLikeCreateSerializer,
    PostShareCreateSerializer, HashtagSerializer, SavedPostSerializer,
    NotificationSerializer, PostReportCreateSerializer, FeedAlgorithmSerializer,
    FeedAlgorithmUpdateSerializer, TrendingTopicsSerializer, FeedStatsSerializer
)
from .filters import PostFilter, CommentFilter
from .permissions import IsOwnerOrReadOnly, CanInteractWithPost
from .utils import (
    get_client_ip, create_notification, get_feed_algorithm_score,
    track_post_view, get_trending_hashtags, get_user_interests
)

User = get_user_model()


class FeedPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FeedPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['content', 'author__first_name', 'author__last_name']
    ordering_fields = ['created_at', 'likes_count', 'comments_count', 'shares_count']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.select_related('author', 'shared_job__company').prefetch_related(
            'hashtags', 'mentioned_users', 'likes__user', 'comments__author', 'shares__user'
        )
        
        # Filter based on visibility and user connections
        if user.is_authenticated:
            # Get connected users
            from connections.views import get_user_connections
            connected_users = get_user_connections(user)
            
            # Apply visibility filters
            queryset = queryset.filter(
                Q(visibility='public') |
                Q(visibility='connections', author__in=connected_users) |
                Q(visibility='private', author=user) |
                Q(author=user)  # User can always see their own posts
            ).filter(is_approved=True)
        else:
            queryset = queryset.filter(visibility='public', is_approved=True)
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PostUpdateSerializer
        return PostSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(author=request.user, is_approved=True)
        
        # Create notifications for mentioned users
        for user in post.mentioned_users.all():
            create_notification(
                recipient=user,
                sender=request.user,
                notification_type='mention',
                title=f"{request.user.full_name} mentioned you in a post",
                message=f"You were mentioned in a post: {post.content[:100]}...",
                post=post,
                action_url=f"/feed/post/{post.id}/"
            )
        
        # Create notifications for connected users (only for public posts)
        if post.visibility == 'public':
            # Import here to avoid circular imports
            from connections.views import get_user_connections
            
            connected_users = get_user_connections(request.user)
            for connected_user in connected_users:
                # Don't notify if user is already mentioned
                if connected_user not in post.mentioned_users.all():
                    create_notification(
                        recipient=connected_user,
                        sender=request.user,
                        notification_type='connection_post',
                        title=f"{request.user.full_name} shared a new post",
                        message=f"Your connection {request.user.full_name} posted: {post.content[:100]}...",
                        post=post,
                        action_url=f"/feed/post/{post.id}/"
                    )
        
        # Return the created post using the read serializer
        read_serializer = PostSerializer(post, context={'request': request})
        headers = self.get_success_headers(read_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # This method is now handled by the custom create method above
        pass

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Track post view
        track_post_view(
            post=instance,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like or react to a post"""
        post = self.get_object()
        serializer = PostLikeCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            reaction_type = serializer.validated_data.get('reaction_type', 'like')
            
            # Toggle like/reaction
            like, created = PostLike.objects.get_or_create(
                user=request.user,
                post=post,
                defaults={'reaction_type': reaction_type}
            )
            
            if not created:
                if like.reaction_type == reaction_type:
                    # Remove like if same reaction
                    like.delete()
                    post.likes_count = max(0, post.likes_count - 1)
                    post.save()
                    return Response({'status': 'unliked'})
                else:
                    # Update reaction type
                    like.reaction_type = reaction_type
                    like.save()
                    return Response({'status': 'reaction_updated', 'reaction': reaction_type})
            else:
                # New like
                post.likes_count = F('likes_count') + 1
                post.save()
                
                # Create notification
                if post.author != request.user:
                    create_notification(
                        recipient=post.author,
                        sender=request.user,
                        notification_type='like',
                        title=f"{request.user.full_name} reacted to your post",
                        message=f"Your post received a {reaction_type} reaction",
                        post=post,
                        action_url=f"/feed/post/{post.id}/"
                    )
                
                return Response({'status': 'liked', 'reaction': reaction_type})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share a post"""
        post = self.get_object()
        serializer = PostShareCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            share, created = PostShare.objects.get_or_create(
                user=request.user,
                post=post,
                defaults={'share_content': serializer.validated_data.get('share_content', '')}
            )
            
            if created:
                post.shares_count = F('shares_count') + 1
                post.save()
                
                # Create notification
                if post.author != request.user:
                    create_notification(
                        recipient=post.author,
                        sender=request.user,
                        notification_type='share',
                        title=f"{request.user.full_name()} shared your post",
                        message=f"Your post was shared with additional comment: {share.share_content[:100]}",
                        post=post,
                        action_url=f"/feed/post/{post.id}/"
                    )
                
                return Response({'status': 'shared'})
            else:
                return Response({'status': 'already_shared'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'])
    def save(self, request, pk=None):
        """Save or unsave a post"""
        post = self.get_object()
        
        if request.method == 'POST':
            saved_post, created = SavedPost.objects.get_or_create(
                user=request.user,
                post=post
            )
            if created:
                return Response({'status': 'saved'})
            else:
                return Response({'status': 'already_saved'})
        
        elif request.method == 'DELETE':
            SavedPost.objects.filter(user=request.user, post=post).delete()
            return Response({'status': 'unsaved'})

    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        """Report a post"""
        post = self.get_object()
        serializer = PostReportCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            report, created = PostReport.objects.get_or_create(
                reporter=request.user,
                post=post,
                defaults={
                    'reason': serializer.validated_data['reason'],
                    'description': serializer.validated_data['description']
                }
            )
            
            if created:
                # Mark post as reported if multiple reports
                report_count = PostReport.objects.filter(post=post).count()
                if report_count >= 3:  # Auto-flag after 3 reports
                    post.is_reported = True
                    post.save()
                
                return Response({'status': 'reported'})
            else:
                return Response({'status': 'already_reported'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def feed(self, request):
        """Get personalized feed for user"""
        # For now, use the same queryset as regular posts to avoid filtering issues
        # TODO: Re-enable algorithm when feed preferences are properly set up
        queryset = self.get_queryset()
        
        # Simple ordering by creation date for now
        queryset = queryset.order_by('-created_at')
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def apply_feed_algorithm(self, queryset, user, feed_algo):
        """Apply machine learning-like feed algorithm"""
        
        # For now, skip connections query to avoid 500 errors
        # TODO: Implement proper connections model and restore this functionality
        connected_users = User.objects.none()  # Empty queryset
        
        # Calculate algorithm score for each post
        queryset = queryset.annotate(
            # Connection score (always 0 for now)
            connection_score=Case(
                When(author__in=connected_users, then=1.0),
                default=0.0,
                output_field=FloatField()
            ),
            
            # Engagement score (normalized)
            engagement_score=F('likes_count') + F('comments_count') * 2 + F('shares_count') * 3,
            
            # Recency score (posts in last 24h get higher score)
            recency_score=Case(
                When(created_at__gte=timezone.now() - timedelta(hours=24), then=1.0),
                When(created_at__gte=timezone.now() - timedelta(days=7), then=0.7),
                default=0.3,
                output_field=FloatField()
            ),
            
            # Calculate final algorithm score
            algorithm_score=(
                F('connection_score') * feed_algo.connection_weight +
                F('engagement_score') * feed_algo.engagement_weight +
                F('recency_score') * feed_algo.recency_weight
            )
        )
        
        # Apply content preferences
        if not feed_algo.show_job_posts:
            queryset = queryset.exclude(post_type='job_share')
        
        if not feed_algo.show_achievement_posts:
            queryset = queryset.exclude(post_type='achievement')
        
        # Exclude muted users and hashtags
        queryset = queryset.exclude(author__in=feed_algo.muted_users.all())
        queryset = queryset.exclude(hashtags__in=feed_algo.muted_hashtags.all())
        
        # Order by algorithm score
        return queryset.order_by('-algorithm_score', '-created_at')

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending posts"""
        # Posts trending in last 24 hours
        trending_posts = self.get_queryset().filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).annotate(
            trend_score=F('likes_count') + F('comments_count') * 2 + F('shares_count') * 3
        ).order_by('-trend_score')[:20]
        
        page = self.paginate_queryset(trending_posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(trending_posts, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CommentFilter
    search_fields = ['content', 'author__first_name', 'author__last_name']
    ordering_fields = ['created_at', 'likes_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Comment.objects.select_related('author', 'post').prefetch_related(
            'likes__user', 'mentioned_users', 'replies__author'
        ).filter(is_approved=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post_id = request.data.get('post')
        post = get_object_or_404(Post, id=post_id)
        comment = serializer.save(author=request.user, post=post, is_approved=True)

        # Update post comment count
        post.comments_count = F('comments_count') + 1
        post.save()

        # Create notifications
        if post.author != request.user:
            create_notification(
                recipient=post.author,
                sender=request.user,
                notification_type='comment',
                title=f"{request.user.full_name} commented on your post",
                message=f"New comment: {comment.content[:100]}...",
                post=post,
                comment=comment,
                action_url=f"/feed/post/{post.id}/"
            )

        # Notify mentioned users
        for user in comment.mentioned_users.all():
            create_notification(
                recipient=user,
                sender=request.user,
                notification_type='mention',
                title=f"{request.user.full_name} mentioned you in a comment",
                message=f"You were mentioned in a comment: {comment.content[:100]}...",
                post=post,
                comment=comment,
                action_url=f"/feed/post/{post.id}/"
            )

        # Refresh the comment from the database to include all related fields
        comment.refresh_from_db()

        # Return the created comment using the read serializer
        read_serializer = CommentSerializer(comment, context={'request': request})
        headers = self.get_success_headers(read_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # Now handled in the custom create method
        pass

    @action(detail=True, methods=['post', 'delete'])
    def like(self, request, pk=None):
        """Like or unlike a comment"""
        comment = self.get_object()
        
        if request.method == 'POST':
            like, created = CommentLike.objects.get_or_create(
                user=request.user,
                comment=comment
            )
            
            if created:
                comment.likes_count = F('likes_count') + 1
                comment.save()
                
                # Create notification
                if comment.author != request.user:
                    create_notification(
                        recipient=comment.author,
                        sender=request.user,
                        notification_type='like',
                        title=f"{request.user.full_name} liked your comment",
                        message=f"Your comment received a like: {comment.content[:100]}...",
                        comment=comment,
                        action_url=f"/feed/post/{comment.post.id}/"
                    )
                
                return Response({'status': 'liked'})
            else:
                return Response({'status': 'already_liked'})
        
        elif request.method == 'DELETE':
            CommentLike.objects.filter(user=request.user, comment=comment).delete()
            comment.likes_count = max(0, F('likes_count') - 1)
            comment.save()
            return Response({'status': 'unliked'})


class HashtagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['posts_count', 'name']
    ordering = ['-posts_count']

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending hashtags"""
        trending = get_trending_hashtags()
        serializer = self.get_serializer(trending, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get posts for a specific hashtag"""
        hashtag = self.get_object()
        posts = Post.objects.filter(hashtags=hashtag, is_approved=True).order_by('-created_at')
        
        # Use PostViewSet pagination
        paginator = FeedPagination()
        page = paginator.paginate_queryset(posts, request)
        
        from .serializers import PostSerializer
        serializer = PostSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


@extend_schema_view(
    list=extend_schema(description='List notifications'),
    retrieve=extend_schema(description='Get a specific notification'),
    mark_read=extend_schema(description='Mark a notification as read'),
    mark_all_read=extend_schema(description='Mark all notifications as read')
)
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FeedPagination
    ordering = ['-created_at']
    queryset = Notification.objects.none()  # Default empty queryset
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'marked_read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        count = self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({'status': 'all_marked_read', 'count': count})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})


@extend_schema_view(
    list=extend_schema(description='List saved posts'),
    retrieve=extend_schema(description='Get a specific saved post')
)
class SavedPostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SavedPostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FeedPagination
    ordering = ['-saved_at']
    queryset = SavedPost.objects.none()  # Default empty queryset
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return SavedPost.objects.none()
        return SavedPost.objects.filter(user=self.request.user).select_related('post', 'post__author')


@extend_schema_view(
    list=extend_schema(description='List feed algorithms'),
    create=extend_schema(description='Create a feed algorithm'),
    update=extend_schema(description='Update a feed algorithm'),
    destroy=extend_schema(description='Delete a feed algorithm')
)
class FeedAlgorithmViewSet(viewsets.ModelViewSet):
    serializer_class = FeedAlgorithmSerializer
    permission_classes = [IsAuthenticated]
    queryset = FeedAlgorithm.objects.none()  # Default empty queryset
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return FeedAlgorithm.objects.none()
        return FeedAlgorithm.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FeedAlgorithmUpdateSerializer
        return FeedAlgorithmSerializer

    def get_object(self):
        """Get or create user's feed algorithm"""
        obj, created = FeedAlgorithm.objects.get_or_create(user=self.request.user)
        return obj

    def list(self, request, *args, **kwargs):
        """Return user's feed algorithm"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Update feed algorithm (no separate create)"""
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update user's feed algorithm"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(FeedAlgorithmSerializer(instance, context={'request': request}).data)


# Analytics and Stats Views
class FeedAnalyticsViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedStatsSerializer
    
    @extend_schema(responses=FeedStatsSerializer)
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get feed statistics"""
        user = request.user
        
        # Get user's posts
        user_posts = Post.objects.filter(author=user)
        
        # Get posts from today and this week
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        posts_today = user_posts.filter(created_at__date=today).count()
        posts_this_week = user_posts.filter(created_at__date__gte=week_ago).count()
        
        # Get engagement stats
        total_likes = sum(post.likes_count for post in user_posts)
        total_comments = sum(post.comments_count for post in user_posts)
        total_shares = sum(post.shares_count for post in user_posts)
        
        # Calculate engagement rate
        total_posts = user_posts.count()
        engagement_rate = 0.0
        if total_posts > 0:
            total_engagement = total_likes + total_comments + total_shares
            engagement_rate = (total_engagement / total_posts) * 100
        
        # Get top performing post
        top_post = user_posts.order_by('-engagement_score').first()
        
        stats = {
            'posts_today': posts_today,
            'posts_this_week': posts_this_week,
            'total_likes_received': total_likes,
            'total_comments_received': total_comments,
            'total_shares_received': total_shares,
            'engagement_rate': round(engagement_rate, 2),
            'top_performing_post': PostSerializer(top_post, context={'request': request}).data if top_post else None
        }
        
        serializer = FeedStatsSerializer(stats)
        return Response(serializer.data)
    
    @extend_schema(responses=TrendingTopicsSerializer)
    @action(detail=False, methods=['get'])
    def trending_topics(self, request):
        """Get trending topics and hashtags"""
        # Get trending hashtags
        trending_hashtags = get_trending_hashtags()
        
        # Get user interests
        user_interests = get_user_interests(request.user)
        
        # Get general trending topics
        topics = [
            'Technology',
            'Business',
            'Marketing',
            'Career Development',
            'Remote Work'
        ]
        
        data = {
            'hashtags': trending_hashtags,
            'topics': topics,
            'user_interests': user_interests
        }
        
        serializer = TrendingTopicsSerializer(data)
        return Response(serializer.data) 