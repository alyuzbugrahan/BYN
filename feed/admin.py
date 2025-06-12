from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from .models import (
    Post, Comment, PostLike, CommentLike, PostShare, PostView, 
    Hashtag, Notification, PostReport, SavedPost, FeedAlgorithm
)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'author', 'post_type', 'content_preview', 'visibility',
        'likes_count', 'comments_count', 'shares_count', 'views_count',
        'is_featured', 'is_reported', 'created_at'
    ]
    list_filter = [
        'post_type', 'visibility', 'is_featured', 'is_reported', 
        'is_approved', 'created_at', 'author__industry'
    ]
    search_fields = ['content', 'author__first_name', 'author__last_name', 'author__email']
    readonly_fields = [
        'likes_count', 'comments_count', 'shares_count', 'views_count',
        'engagement_rate_display', 'created_at', 'updated_at'
    ]
    filter_horizontal = ['hashtags', 'mentioned_users']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('author', 'content', 'post_type', 'visibility')
        }),
        ('Media', {
            'fields': ('image', 'video', 'document'),
            'classes': ('collapse',)
        }),
        ('Article/Link Sharing', {
            'fields': ('article_title', 'article_url', 'article_description', 'article_image'),
            'classes': ('collapse',)
        }),
        ('Job Sharing', {
            'fields': ('shared_job',),
            'classes': ('collapse',)
        }),
        ('Social Features', {
            'fields': ('hashtags', 'mentioned_users')
        }),
        ('Moderation', {
            'fields': ('is_pinned', 'is_featured', 'is_reported', 'is_approved')
        }),
        ('Statistics', {
            'fields': ('likes_count', 'comments_count', 'shares_count', 'views_count', 'engagement_rate_display'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = "Content"
    
    def engagement_rate_display(self, obj):
        return f"{obj.engagement_rate:.2f}%"
    engagement_rate_display.short_description = "Engagement Rate"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'shared_job')
    
    actions = ['mark_as_featured', 'mark_as_reported', 'approve_posts']
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} posts marked as featured.')
    mark_as_featured.short_description = "Mark selected posts as featured"
    
    def mark_as_reported(self, request, queryset):
        updated = queryset.update(is_reported=True)
        self.message_user(request, f'{updated} posts marked as reported.')
    mark_as_reported.short_description = "Mark selected posts as reported"
    
    def approve_posts(self, request, queryset):
        updated = queryset.update(is_approved=True, is_reported=False)
        self.message_user(request, f'{updated} posts approved.')
    approve_posts.short_description = "Approve selected posts"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'author', 'post_preview', 'content_preview', 'is_reply',
        'likes_count', 'replies_count', 'is_reported', 'created_at'
    ]
    list_filter = ['is_reported', 'is_approved', 'created_at', 'post__post_type']
    search_fields = ['content', 'author__first_name', 'author__last_name', 'post__content']
    readonly_fields = ['likes_count', 'replies_count', 'created_at', 'updated_at']
    filter_horizontal = ['mentioned_users']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('post', 'author', 'content', 'parent')
        }),
        ('Media', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Social Features', {
            'fields': ('mentioned_users',)
        }),
        ('Moderation', {
            'fields': ('is_reported', 'is_approved')
        }),
        ('Statistics', {
            'fields': ('likes_count', 'replies_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:80] + "..." if len(obj.content) > 80 else obj.content
    content_preview.short_description = "Content"
    
    def post_preview(self, obj):
        return obj.post.content[:50] + "..." if len(obj.post.content) > 50 else obj.post.content
    post_preview.short_description = "Post"
    
    def is_reply(self, obj):
        return obj.parent is not None
    is_reply.boolean = True
    is_reply.short_description = "Is Reply"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'post', 'parent')


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post_preview', 'reaction_type', 'created_at']
    list_filter = ['reaction_type', 'created_at', 'post__post_type']
    search_fields = ['user__first_name', 'user__last_name', 'post__content']
    readonly_fields = ['created_at']
    
    def post_preview(self, obj):
        return obj.post.content[:50] + "..." if len(obj.post.content) > 50 else obj.post.content
    post_preview.short_description = "Post"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'post')


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__first_name', 'user__last_name', 'comment__content']
    readonly_fields = ['created_at']
    
    def comment_preview(self, obj):
        return obj.comment.content[:50] + "..." if len(obj.comment.content) > 50 else obj.comment.content
    comment_preview.short_description = "Comment"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'comment')


@admin.register(PostShare)
class PostShareAdmin(admin.ModelAdmin):
    list_display = ['user', 'post_preview', 'share_content_preview', 'created_at']
    list_filter = ['created_at', 'post__post_type']
    search_fields = ['user__first_name', 'user__last_name', 'post__content', 'share_content']
    readonly_fields = ['created_at']
    
    def post_preview(self, obj):
        return obj.post.content[:50] + "..." if len(obj.post.content) > 50 else obj.post.content
    post_preview.short_description = "Post"
    
    def share_content_preview(self, obj):
        if obj.share_content:
            return obj.share_content[:50] + "..." if len(obj.share_content) > 50 else obj.share_content
        return "-"
    share_content_preview.short_description = "Share Comment"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'post')


@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ['user_display', 'post_preview', 'view_duration_display', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at', 'post__post_type']
    search_fields = ['user__first_name', 'user__last_name', 'post__content', 'ip_address']
    readonly_fields = ['user', 'post', 'ip_address', 'user_agent', 'viewed_at', 'view_duration']
    
    def user_display(self, obj):
        return obj.user.get_full_name() if obj.user else "Anonymous"
    user_display.short_description = "User"
    
    def post_preview(self, obj):
        return obj.post.content[:50] + "..." if len(obj.post.content) > 50 else obj.post.content
    post_preview.short_description = "Post"
    
    def view_duration_display(self, obj):
        return f"{obj.view_duration}s" if obj.view_duration else "0s"
    view_duration_display.short_description = "Duration"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'post')


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ['name', 'posts_count', 'is_trending', 'created_at']
    list_filter = ['is_trending', 'created_at']
    search_fields = ['name']
    readonly_fields = ['posts_count', 'created_at']
    ordering = ['-posts_count', 'name']
    
    actions = ['mark_as_trending', 'remove_from_trending']
    
    def mark_as_trending(self, request, queryset):
        updated = queryset.update(is_trending=True)
        self.message_user(request, f'{updated} hashtags marked as trending.')
    mark_as_trending.short_description = "Mark selected hashtags as trending"
    
    def remove_from_trending(self, request, queryset):
        updated = queryset.update(is_trending=False)
        self.message_user(request, f'{updated} hashtags removed from trending.')
    remove_from_trending.short_description = "Remove from trending"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'recipient', 'sender', 'notification_type', 'title',
        'is_read', 'is_sent_email', 'created_at'
    ]
    list_filter = [
        'notification_type', 'is_read', 'is_sent_email', 'is_sent_push', 'created_at'
    ]
    search_fields = ['recipient__first_name', 'recipient__last_name', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('recipient', 'sender', 'notification_type', 'title', 'message')
        }),
        ('Related Objects', {
            'fields': ('post', 'comment', 'action_url'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'is_sent_email', 'is_sent_push')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'read_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'sender', 'post', 'comment')
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.filter(is_read=False).update(is_read=True)
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.filter(is_read=True).update(is_read=False)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = "Mark selected notifications as unread"


@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = [
        'reporter', 'post_preview', 'reason', 'is_reviewed',
        'action_taken', 'reviewed_by', 'created_at'
    ]
    list_filter = ['reason', 'is_reviewed', 'created_at']
    search_fields = ['reporter__first_name', 'reporter__last_name', 'post__content', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('reporter', 'post', 'reason', 'description')
        }),
        ('Review', {
            'fields': ('is_reviewed', 'action_taken', 'reviewed_by', 'reviewed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def post_preview(self, obj):
        return obj.post.content[:50] + "..." if len(obj.post.content) > 50 else obj.post.content
    post_preview.short_description = "Post"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('reporter', 'post', 'reviewed_by')
    
    actions = ['mark_as_reviewed', 'approve_posts']
    
    def mark_as_reviewed(self, request, queryset):
        updated = queryset.update(is_reviewed=True, reviewed_by=request.user)
        self.message_user(request, f'{updated} reports marked as reviewed.')
    mark_as_reviewed.short_description = "Mark selected reports as reviewed"
    
    def approve_posts(self, request, queryset):
        for report in queryset:
            report.post.is_approved = True
            report.post.is_reported = False
            report.post.save()
            report.is_reviewed = True
            report.action_taken = "Post approved"
            report.reviewed_by = request.user
            report.save()
        self.message_user(request, f'{queryset.count()} reported posts approved.')
    approve_posts.short_description = "Approve reported posts"


@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ['user', 'post_preview', 'saved_at']
    list_filter = ['saved_at', 'post__post_type']
    search_fields = ['user__first_name', 'user__last_name', 'post__content']
    readonly_fields = ['saved_at']
    
    def post_preview(self, obj):
        return obj.post.content[:50] + "..." if len(obj.post.content) > 50 else obj.post.content
    post_preview.short_description = "Post"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'post')


@admin.register(FeedAlgorithm)
class FeedAlgorithmAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'connection_weight', 'engagement_weight', 'recency_weight',
        'show_promoted_content', 'updated_at'
    ]
    list_filter = ['show_promoted_content', 'show_job_posts', 'show_company_updates', 'updated_at']
    search_fields = ['user__first_name', 'user__last_name']
    readonly_fields = ['updated_at']
    filter_horizontal = ['muted_users', 'muted_hashtags']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Algorithm Weights', {
            'fields': (
                'connection_weight', 'engagement_weight', 'recency_weight',
                'similarity_weight', 'trending_weight'
            )
        }),
        ('Content Preferences', {
            'fields': (
                'show_promoted_content', 'show_job_posts',
                'show_company_updates', 'show_achievement_posts'
            )
        }),
        ('Filters', {
            'fields': ('muted_users', 'muted_hashtags'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Custom admin views for analytics
admin.site.site_header = "BYN Administration"
admin.site.site_title = "BYN Admin"
admin.site.index_title = "Welcome to BYN Administration" 