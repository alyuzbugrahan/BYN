from rest_framework import permissions
from django.db.models import Q


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.author == request.user


class CanInteractWithPost(permissions.BasePermission):
    """
    Permission to check if user can interact with a post based on visibility settings.
    """
    
    def has_object_permission(self, request, view, obj):
        # If user is not authenticated, only public posts are accessible
        if not request.user.is_authenticated:
            return obj.visibility == 'public' and obj.is_approved
        
        # Owner can always access their own posts
        if obj.author == request.user:
            return True
        
        # Staff can access all posts
        if request.user.is_staff:
            return True
        
        # Check visibility settings
        if obj.visibility == 'public':
            return obj.is_approved
        elif obj.visibility == 'private':
            return False  # Only owner can access private posts
        elif obj.visibility == 'connections':
            # Check if user is connected to the post author
            is_connected = request.user.received_connections.filter(
                sender=obj.author, status='accepted'
            ).exists() or request.user.sent_connections.filter(
                receiver=obj.author, status='accepted'
            ).exists()
            return is_connected and obj.is_approved
        
        return False


class CanCommentOnPost(permissions.BasePermission):
    """
    Permission to check if user can comment on a post.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Use the same logic as CanInteractWithPost for the post
        if hasattr(obj, 'post'):
            post = obj.post
        else:
            post = obj
        
        return CanInteractWithPost().has_object_permission(request, view, post)


class CanModerateContent(permissions.BasePermission):
    """
    Permission for content moderation (staff or moderators).
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.groups.filter(name='Moderators').exists()
        )


class IsOwnerOrModerator(permissions.BasePermission):
    """
    Permission for owners or moderators to access/modify content.
    """
    
    def has_object_permission(self, request, view, obj):
        # Owner can always access
        if hasattr(obj, 'author') and obj.author == request.user:
            return True
        
        # User can access their own objects (notifications, saved posts, etc.)
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        if hasattr(obj, 'recipient') and obj.recipient == request.user:
            return True
        
        # Moderators can access for moderation purposes
        return request.user.is_staff or request.user.groups.filter(name='Moderators').exists()


class CanReportContent(permissions.BasePermission):
    """
    Permission to report content (authenticated users only).
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Users cannot report their own content
        if hasattr(obj, 'author') and obj.author == request.user:
            return False
        
        # Users cannot report already reported content by themselves
        if hasattr(obj, 'reports'):
            already_reported = obj.reports.filter(reporter=request.user).exists()
            if already_reported:
                return False
        
        return True


class CanViewAnalytics(permissions.BasePermission):
    """
    Permission to view analytics (owners or staff).
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Owner can view their own analytics
        if hasattr(obj, 'author') and obj.author == request.user:
            return True
        
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Staff can view all analytics
        return request.user.is_staff


class CanManageFeedAlgorithm(permissions.BasePermission):
    """
    Permission to manage feed algorithm settings (user's own only).
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Users can only manage their own feed algorithm
        return obj.user == request.user


class IsConnectionOrPublic(permissions.BasePermission):
    """
    Permission based on user connections and content visibility.
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            # Anonymous users can only see public content
            return getattr(obj, 'visibility', 'public') == 'public'
        
        # Owner can always access
        if hasattr(obj, 'author') and obj.author == request.user:
            return True
        
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # Check visibility and connections
        visibility = getattr(obj, 'visibility', 'public')
        
        if visibility == 'public':
            return True
        elif visibility == 'private':
            return False
        elif visibility == 'connections':
            # Check if users are connected
            author = getattr(obj, 'author', None)
            if author:
                is_connected = request.user.received_connections.filter(
                    sender=author, status='accepted'
                ).exists() or request.user.sent_connections.filter(
                    receiver=author, status='accepted'
                ).exists()
                return is_connected
        
        return False


class CanAccessNotifications(permissions.BasePermission):
    """
    Permission to access notifications (recipient only).
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Only recipient can access their notifications
        return obj.recipient == request.user


class CanManageHashtags(permissions.BasePermission):
    """
    Permission to manage hashtags (staff only for moderation).
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_staff


class RateLimitPermission(permissions.BasePermission):
    """
    Simple rate limiting permission (can be enhanced with Redis/cache).
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return True
        
        # Basic rate limiting logic
        from django.core.cache import cache
        from django.utils import timezone
        
        # Different limits for different actions
        limits = {
            'POST': 50,  # 50 posts per hour
            'comment': 200,  # 200 comments per hour
            'like': 500,  # 500 likes per hour
        }
        
        action = 'POST'
        if 'comment' in request.path:
            action = 'comment'
        elif 'like' in request.path:
            action = 'like'
        
        cache_key = f"rate_limit_{request.user.id}_{action}_{timezone.now().hour}"
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limits.get(action, 100):
            return False
        
        # Increment counter
        cache.set(cache_key, current_count + 1, 3600)  # 1 hour timeout
        return True


class ContentModerationPermission(permissions.BasePermission):
    """
    Permission for content that might need moderation.
    """
    
    def has_object_permission(self, request, view, obj):
        # If content is not approved, only owner and moderators can see it
        if hasattr(obj, 'is_approved') and not obj.is_approved:
            if hasattr(obj, 'author') and obj.author == request.user:
                return True
            return request.user.is_staff or request.user.groups.filter(name='Moderators').exists()
        
        # If content is reported, apply additional checks
        if hasattr(obj, 'is_reported') and obj.is_reported:
            # Reported content might have restricted visibility
            if request.user.is_staff or request.user.groups.filter(name='Moderators').exists():
                return True
            # Owner can still see their reported content
            if hasattr(obj, 'author') and obj.author == request.user:
                return True
        
        return True


# Utility function to check if users are connected
def are_users_connected(user1, user2):
    """
    Check if two users are connected (have accepted connection).
    """
    if user1 == user2:
        return True
    
    return user1.received_connections.filter(
        sender=user2, status='accepted'
    ).exists() or user1.sent_connections.filter(
        receiver=user2, status='accepted'
    ).exists()


# Utility function to get user's connection level access
def get_user_access_level(user, target_user):
    """
    Get user's access level to target user's content.
    Returns: 'owner', 'connection', 'public', 'none'
    """
    if user == target_user:
        return 'owner'
    
    if not user.is_authenticated:
        return 'public'
    
    if user.is_staff:
        return 'owner'  # Staff has owner-level access
    
    if are_users_connected(user, target_user):
        return 'connection'
    
    return 'public' 