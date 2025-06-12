from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from datetime import timedelta
import re

User = get_user_model()


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_notification(recipient, sender, notification_type, title, message, 
                       post=None, comment=None, action_url=''):
    """Create a notification for user"""
    from .models import Notification
    
    # Avoid duplicate notifications
    existing = Notification.objects.filter(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        post=post,
        comment=comment,
        created_at__gte=timezone.now() - timedelta(minutes=5)
    ).exists()
    
    if not existing:
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            post=post,
            comment=comment,
            action_url=action_url
        )
        return notification
    return None


def track_post_view(post, user=None, ip_address='', user_agent='', view_duration=0):
    """Track a post view for analytics"""
    from .models import PostView
    
    # Avoid duplicate views from same user/IP in short time
    recent_threshold = timezone.now() - timedelta(minutes=30)
    
    if user:
        recent_view = PostView.objects.filter(
            post=post,
            user=user,
            viewed_at__gte=recent_threshold
        ).exists()
    else:
        recent_view = PostView.objects.filter(
            post=post,
            ip_address=ip_address,
            viewed_at__gte=recent_threshold
        ).exists()
    
    if not recent_view:
        view = PostView.objects.create(
            post=post,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            view_duration=view_duration
        )
        
        # Update post view count
        post.views_count += 1
        post.save(update_fields=['views_count'])
        
        return view
    return None


def get_trending_hashtags(limit=20):
    """Get trending hashtags based on recent activity"""
    from .models import Hashtag
    
    # Get hashtags trending in last 7 days
    week_ago = timezone.now() - timedelta(days=7)
    
    trending = Hashtag.objects.filter(
        post__created_at__gte=week_ago
    ).annotate(
        recent_posts_count=Count('post', filter=Q(post__created_at__gte=week_ago))
    ).filter(
        recent_posts_count__gte=3  # Minimum 3 posts to be trending
    ).order_by('-recent_posts_count', '-posts_count')[:limit]
    
    return trending


def get_user_interests(user, limit=10):
    """Get user interests based on their activity"""
    from .models import Post, PostLike, Comment, Hashtag
    
    # Get hashtags from user's posts
    user_hashtags = Hashtag.objects.filter(
        post__author=user
    ).annotate(
        usage_count=Count('post', filter=Q(post__author=user))
    ).order_by('-usage_count')[:limit//2]
    
    # Get hashtags from posts user liked
    liked_hashtags = Hashtag.objects.filter(
        post__likes__user=user
    ).annotate(
        like_count=Count('post', filter=Q(post__likes__user=user))
    ).order_by('-like_count')[:limit//2]
    
    # Combine and deduplicate
    all_hashtags = list(user_hashtags) + list(liked_hashtags)
    unique_hashtags = []
    seen_names = set()
    
    for hashtag in all_hashtags:
        if hashtag.name not in seen_names:
            unique_hashtags.append(hashtag.name)
            seen_names.add(hashtag.name)
    
    return unique_hashtags[:limit]


def get_feed_algorithm_score(post, user, algorithm_weights):
    """Calculate algorithm score for a post for specific user"""
    score = 0.0
    
    # Connection score
    if user.is_authenticated:
        is_connected = user.received_connections.filter(
            sender=post.author, status='accepted'
        ).exists() or user.sent_connections.filter(
            receiver=post.author, status='accepted'
        ).exists()
        
        if is_connected:
            score += algorithm_weights.get('connection_weight', 0.3)
    
    # Engagement score
    engagement_rate = post.engagement_rate if hasattr(post, 'engagement_rate') else 0
    score += (engagement_rate / 100) * algorithm_weights.get('engagement_weight', 0.2)
    
    # Recency score
    hours_old = (timezone.now() - post.created_at).total_seconds() / 3600
    if hours_old <= 24:
        recency_score = 1.0
    elif hours_old <= 168:  # 1 week
        recency_score = 0.7
    else:
        recency_score = 0.3
    
    score += recency_score * algorithm_weights.get('recency_weight', 0.2)
    
    # Interest similarity score (based on hashtags)
    if user.is_authenticated:
        user_interests = get_user_interests(user)
        post_hashtags = [hashtag.name for hashtag in post.hashtags.all()]
        
        # Calculate similarity
        common_interests = set(user_interests) & set(post_hashtags)
        if user_interests and post_hashtags:
            similarity = len(common_interests) / len(set(user_interests) | set(post_hashtags))
            score += similarity * algorithm_weights.get('similarity_weight', 0.15)
    
    # Trending score
    is_trending = post.hashtags.filter(is_trending=True).exists()
    if is_trending:
        score += algorithm_weights.get('trending_weight', 0.15)
    
    return min(score, 1.0)  # Cap at 1.0


def extract_hashtags(text):
    """Extract hashtags from text"""
    hashtag_pattern = r'#(\w+)'
    hashtags = re.findall(hashtag_pattern, text.lower())
    return list(set(hashtags))  # Remove duplicates


def extract_mentions(text):
    """Extract @mentions from text"""
    mention_pattern = r'@(\w+)'
    mentions = re.findall(mention_pattern, text.lower())
    return list(set(mentions))  # Remove duplicates


def get_user_by_username(username):
    """Get user by username or email"""
    try:
        # Try by username first (if you have username field)
        return User.objects.get(username=username)
    except (User.DoesNotExist, AttributeError):
        try:
            # Try by email
            return User.objects.get(email=username)
        except User.DoesNotExist:
            return None


def process_post_content(content, author):
    """Process post content to extract hashtags and mentions"""
    hashtags = extract_hashtags(content)
    mentions = extract_mentions(content)
    
    # Get mentioned users
    mentioned_users = []
    for mention in mentions:
        user = get_user_by_username(mention)
        if user and user != author:
            mentioned_users.append(user)
    
    return {
        'hashtags': hashtags,
        'mentioned_users': mentioned_users
    }


def get_content_recommendations(user, limit=5):
    """Get content recommendations for user based on their activity"""
    from .models import Post, Hashtag
    
    if not user.is_authenticated:
        return Post.objects.filter(visibility='public', is_approved=True).order_by('-created_at')[:limit]
    
    # Get user interests
    user_interests = get_user_interests(user)
    
    if not user_interests:
        # Fallback to trending content
        return Post.objects.filter(
            visibility='public', 
            is_approved=True,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-likes_count', '-comments_count')[:limit]
    
    # Get posts with similar hashtags
    recommended_posts = Post.objects.filter(
        hashtags__name__in=user_interests,
        visibility='public',
        is_approved=True
    ).exclude(
        author=user  # Don't recommend user's own posts
    ).distinct().order_by('-created_at')[:limit]
    
    return recommended_posts


def calculate_user_influence_score(user):
    """Calculate user's influence score based on their activity"""
    from .models import Post
    
    user_posts = Post.objects.filter(author=user)
    
    if not user_posts.exists():
        return 0
    
    # Calculate based on engagement
    total_likes = sum(post.likes_count for post in user_posts)
    total_comments = sum(post.comments_count for post in user_posts)
    total_shares = sum(post.shares_count for post in user_posts)
    total_views = sum(post.views_count for post in user_posts)
    
    # Weight different types of engagement
    engagement_score = total_likes + (total_comments * 2) + (total_shares * 3)
    
    # Factor in reach (views)
    if total_views > 0:
        influence_score = (engagement_score / total_views) * 100
    else:
        influence_score = 0
    
    # Factor in follower count (connections)
    follower_count = user.received_connections.filter(status='accepted').count()
    influence_score += follower_count * 0.1
    
    # Factor in consistency (posting frequency)
    days_since_first_post = (timezone.now() - user_posts.first().created_at).days
    if days_since_first_post > 0:
        posts_per_day = user_posts.count() / days_since_first_post
        influence_score += posts_per_day * 5
    
    return min(influence_score, 100)  # Cap at 100


def get_post_analytics(post):
    """Get detailed analytics for a post"""
    from .models import PostView, PostLike, Comment, PostShare
    
    # Basic engagement
    analytics = {
        'total_views': post.views_count,
        'total_likes': post.likes_count,
        'total_comments': post.comments_count,
        'total_shares': post.shares_count,
        'engagement_rate': post.engagement_rate,
    }
    
    # View analytics
    views_by_hour = PostView.objects.filter(post=post).extra(
        select={'hour': "date_part('hour', viewed_at)"}
    ).values('hour').annotate(count=Count('id')).order_by('hour')
    
    analytics['views_by_hour'] = {str(int(item['hour'])): item['count'] for item in views_by_hour}
    
    # Reaction breakdown
    reactions = PostLike.objects.filter(post=post).values('reaction_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    analytics['reactions'] = {item['reaction_type']: item['count'] for item in reactions}
    
    # Top comments
    top_comments = Comment.objects.filter(post=post, parent=None).order_by(
        '-likes_count'
    )[:3]
    
    analytics['top_comments'] = [
        {
            'id': comment.id,
            'content': comment.content[:100],
            'author': comment.author.get_full_name(),
            'likes_count': comment.likes_count
        } for comment in top_comments
    ]
    
    return analytics


def cleanup_old_notifications(days=30):
    """Cleanup old notifications"""
    from .models import Notification
    
    cutoff_date = timezone.now() - timedelta(days=days)
    deleted_count, _ = Notification.objects.filter(
        created_at__lt=cutoff_date,
        is_read=True
    ).delete()
    
    return deleted_count


def get_weekly_digest_data(user):
    """Get data for weekly digest email"""
    from .models import Post, Notification
    
    week_ago = timezone.now() - timedelta(days=7)
    
    # User's activity this week
    user_posts = Post.objects.filter(author=user, created_at__gte=week_ago)
    
    # Calculate total engagement on user's posts
    total_likes = sum(post.likes_count for post in user_posts)
    total_comments = sum(post.comments_count for post in user_posts)
    total_shares = sum(post.shares_count for post in user_posts)
    
    # Get trending content in user's network
    # Skip connections for now to avoid 500 errors
    # TODO: Implement proper connections model
    connected_users = User.objects.none()  # Empty queryset

    network_posts = Post.objects.filter(
        author__in=connected_users,
        created_at__gte=week_ago,
        visibility__in=['public', 'connections']
    ).order_by('-likes_count', '-comments_count')[:5]
    
    # Unread notifications
    unread_notifications = Notification.objects.filter(
        recipient=user,
        is_read=False,
        created_at__gte=week_ago
    ).count()
    
    return {
        'posts_created': user_posts.count(),
        'total_engagement': total_likes + total_comments + total_shares,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'total_shares': total_shares,
        'trending_in_network': network_posts,
        'unread_notifications': unread_notifications,
        'week_start': week_ago.date(),
        'week_end': timezone.now().date()
    } 