import django_filters
from django.db.models import Q
from .models import Post, Comment, Hashtag, Notification


class PostFilter(django_filters.FilterSet):
    # Text search
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    # Author filters
    author = django_filters.NumberFilter(field_name='author__id')
    author_name = django_filters.CharFilter(method='filter_author_name', label='Author Name')
    
    # Content type filters
    post_type = django_filters.ChoiceFilter(choices=Post.POST_TYPES)
    visibility = django_filters.ChoiceFilter(choices=Post.VISIBILITY_CHOICES)
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    created_date = django_filters.DateFilter(field_name='created_at__date')
    
    # Engagement filters
    min_likes = django_filters.NumberFilter(field_name='likes_count', lookup_expr='gte')
    min_comments = django_filters.NumberFilter(field_name='comments_count', lookup_expr='gte')
    min_shares = django_filters.NumberFilter(field_name='shares_count', lookup_expr='gte')
    min_views = django_filters.NumberFilter(field_name='views_count', lookup_expr='gte')
    
    # Hashtag filters
    hashtags = django_filters.CharFilter(method='filter_hashtags', label='Hashtags')
    has_hashtags = django_filters.BooleanFilter(method='filter_has_hashtags', label='Has Hashtags')
    
    # Status filters
    is_featured = django_filters.BooleanFilter()
    is_pinned = django_filters.BooleanFilter()
    is_approved = django_filters.BooleanFilter()
    
    # Media filters
    has_image = django_filters.BooleanFilter(method='filter_has_image', label='Has Image')
    has_video = django_filters.BooleanFilter(method='filter_has_video', label='Has Video')
    has_document = django_filters.BooleanFilter(method='filter_has_document', label='Has Document')
    has_media = django_filters.BooleanFilter(method='filter_has_media', label='Has Any Media')
    
    # Job sharing
    shared_job = django_filters.NumberFilter(field_name='shared_job__id')
    has_shared_job = django_filters.BooleanFilter(method='filter_has_shared_job', label='Has Shared Job')
    
    # Article sharing
    has_article = django_filters.BooleanFilter(method='filter_has_article', label='Has Article Link')
    
    # User interaction filters
    liked_by_user = django_filters.BooleanFilter(method='filter_liked_by_user', label='Liked by Current User')
    saved_by_user = django_filters.BooleanFilter(method='filter_saved_by_user', label='Saved by Current User')
    
    # Connection filters
    from_connections = django_filters.BooleanFilter(method='filter_from_connections', label='From Connections')
    
    class Meta:
        model = Post
        fields = []
    
    def filter_search(self, queryset, name, value):
        """Search in content, author name, and hashtags"""
        if value:
            return queryset.filter(
                Q(content__icontains=value) |
                Q(author__first_name__icontains=value) |
                Q(author__last_name__icontains=value) |
                Q(hashtags__name__icontains=value) |
                Q(article_title__icontains=value)
            ).distinct()
        return queryset
    
    def filter_author_name(self, queryset, name, value):
        """Filter by author's full name"""
        if value:
            return queryset.filter(
                Q(author__first_name__icontains=value) |
                Q(author__last_name__icontains=value)
            ).distinct()
        return queryset
    
    def filter_hashtags(self, queryset, name, value):
        """Filter by hashtag names (comma-separated)"""
        if value:
            hashtag_names = [tag.strip().lower().lstrip('#') for tag in value.split(',')]
            return queryset.filter(hashtags__name__in=hashtag_names).distinct()
        return queryset
    
    def filter_has_hashtags(self, queryset, name, value):
        """Filter posts that have hashtags"""
        if value is not None:
            if value:
                return queryset.filter(hashtags__isnull=False).distinct()
            else:
                return queryset.filter(hashtags__isnull=True)
        return queryset
    
    def filter_has_image(self, queryset, name, value):
        """Filter posts with images"""
        if value is not None:
            if value:
                return queryset.exclude(image__isnull=True).exclude(image='')
            else:
                return queryset.filter(Q(image__isnull=True) | Q(image=''))
        return queryset
    
    def filter_has_video(self, queryset, name, value):
        """Filter posts with videos"""
        if value is not None:
            if value:
                return queryset.exclude(video__isnull=True).exclude(video='')
            else:
                return queryset.filter(Q(video__isnull=True) | Q(video=''))
        return queryset
    
    def filter_has_document(self, queryset, name, value):
        """Filter posts with documents"""
        if value is not None:
            if value:
                return queryset.exclude(document__isnull=True).exclude(document='')
            else:
                return queryset.filter(Q(document__isnull=True) | Q(document=''))
        return queryset
    
    def filter_has_media(self, queryset, name, value):
        """Filter posts with any type of media"""
        if value is not None:
            if value:
                return queryset.filter(
                    Q(image__isnull=False, image__ne='') |
                    Q(video__isnull=False, video__ne='') |
                    Q(document__isnull=False, document__ne='')
                )
            else:
                return queryset.filter(
                    Q(image__isnull=True) | Q(image=''),
                    Q(video__isnull=True) | Q(video=''),
                    Q(document__isnull=True) | Q(document='')
                )
        return queryset
    
    def filter_has_shared_job(self, queryset, name, value):
        """Filter posts that share jobs"""
        if value is not None:
            if value:
                return queryset.filter(shared_job__isnull=False)
            else:
                return queryset.filter(shared_job__isnull=True)
        return queryset
    
    def filter_has_article(self, queryset, name, value):
        """Filter posts with article links"""
        if value is not None:
            if value:
                return queryset.exclude(article_url__isnull=True).exclude(article_url='')
            else:
                return queryset.filter(Q(article_url__isnull=True) | Q(article_url=''))
        return queryset
    
    def filter_liked_by_user(self, queryset, name, value):
        """Filter posts liked by current user"""
        if value is not None and self.request and self.request.user.is_authenticated:
            if value:
                return queryset.filter(likes__user=self.request.user)
            else:
                return queryset.exclude(likes__user=self.request.user)
        return queryset
    
    def filter_saved_by_user(self, queryset, name, value):
        """Filter posts saved by current user"""
        if value is not None and self.request and self.request.user.is_authenticated:
            if value:
                return queryset.filter(saved_by__user=self.request.user)
            else:
                return queryset.exclude(saved_by__user=self.request.user)
        return queryset
    
    def filter_from_connections(self, queryset, name, value):
        """Filter posts from user's connections"""
        if value is not None and self.request and self.request.user.is_authenticated:
            user = self.request.user
            if value:
                # Skip connections for now to avoid 500 errors
                # TODO: Implement proper connections model
                from django.contrib.auth import get_user_model
                User = get_user_model()
                connected_users = User.objects.none()  # Empty queryset
                return queryset.filter(author__in=connected_users)
            else:
                # Skip connections for now to avoid 500 errors
                # TODO: Implement proper connections model
                from django.contrib.auth import get_user_model
                User = get_user_model()
                connected_users = User.objects.none()  # Empty queryset
                return queryset.exclude(author__in=connected_users)
        return queryset


class CommentFilter(django_filters.FilterSet):
    # Post filter
    post = django_filters.NumberFilter(field_name='post__id')
    
    # Author filters
    author = django_filters.NumberFilter(field_name='author__id')
    author_name = django_filters.CharFilter(method='filter_author_name', label='Author Name')
    
    # Content search
    search = django_filters.CharFilter(field_name='content', lookup_expr='icontains')
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Engagement filters
    min_likes = django_filters.NumberFilter(field_name='likes_count', lookup_expr='gte')
    min_replies = django_filters.NumberFilter(field_name='replies_count', lookup_expr='gte')
    
    # Structure filters
    is_reply = django_filters.BooleanFilter(method='filter_is_reply', label='Is Reply')
    parent_comment = django_filters.NumberFilter(field_name='parent__id')
    
    # Status filters
    is_approved = django_filters.BooleanFilter()
    is_reported = django_filters.BooleanFilter()
    
    # Media filters
    has_image = django_filters.BooleanFilter(method='filter_has_image', label='Has Image')
    
    class Meta:
        model = Comment
        fields = []
    
    def filter_author_name(self, queryset, name, value):
        """Filter by author's full name"""
        if value:
            return queryset.filter(
                Q(author__first_name__icontains=value) |
                Q(author__last_name__icontains=value)
            ).distinct()
        return queryset
    
    def filter_is_reply(self, queryset, name, value):
        """Filter replies vs top-level comments"""
        if value is not None:
            if value:
                return queryset.filter(parent__isnull=False)
            else:
                return queryset.filter(parent__isnull=True)
        return queryset
    
    def filter_has_image(self, queryset, name, value):
        """Filter comments with images"""
        if value is not None:
            if value:
                return queryset.exclude(image__isnull=True).exclude(image='')
            else:
                return queryset.filter(Q(image__isnull=True) | Q(image=''))
        return queryset


class HashtagFilter(django_filters.FilterSet):
    # Name search
    search = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    name = django_filters.CharFilter(field_name='name', lookup_expr='iexact')
    
    # Popularity filters
    min_posts = django_filters.NumberFilter(field_name='posts_count', lookup_expr='gte')
    max_posts = django_filters.NumberFilter(field_name='posts_count', lookup_expr='lte')
    
    # Trending filter
    is_trending = django_filters.BooleanFilter()
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Hashtag
        fields = []


class NotificationFilter(django_filters.FilterSet):
    # Type filter
    notification_type = django_filters.ChoiceFilter(choices=Notification.NOTIFICATION_TYPES)
    
    # Status filters
    is_read = django_filters.BooleanFilter()
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Sender filter
    sender = django_filters.NumberFilter(field_name='sender__id')
    sender_name = django_filters.CharFilter(method='filter_sender_name', label='Sender Name')
    
    # Related object filters
    post = django_filters.NumberFilter(field_name='post__id')
    comment = django_filters.NumberFilter(field_name='comment__id')
    
    class Meta:
        model = Notification
        fields = []
    
    def filter_sender_name(self, queryset, name, value):
        """Filter by sender's full name"""
        if value:
            return queryset.filter(
                Q(sender__first_name__icontains=value) |
                Q(sender__last_name__icontains=value)
            ).distinct()
        return queryset 