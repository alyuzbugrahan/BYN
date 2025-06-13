#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linkedin_clone.settings')
django.setup()

from accounts.models import User
from companies.models import Company
from jobs.models import Job
from feed.models import Post, Comment, Hashtag, Notification
from connections.models import Connection

print("COMPREHENSIVE SAMPLE DATA SUMMARY")
print("=" * 50)

users_count = User.objects.count()
companies_count = Company.objects.count()
jobs_count = Job.objects.count()
posts_count = Post.objects.count()
comments_count = Comment.objects.count()
hashtags_count = Hashtag.objects.count()
connections_count = Connection.objects.count()
notifications_count = Notification.objects.count()

users_with_photos = User.objects.filter(profile_picture__isnull=False).count()
companies_with_logos = Company.objects.filter(logo__isnull=False).count()

print(f"Users: {users_count}")
print(f"Companies: {companies_count}")
print(f"Jobs: {jobs_count}")
print(f"Posts: {posts_count}")
print(f"Comments: {comments_count}")
print(f"Hashtags: {hashtags_count}")
print(f"Connections: {connections_count}")
print(f"Notifications: {notifications_count}")
print(f"Users with photos: {users_with_photos}/{users_count}")
print(f"Companies with logos: {companies_with_logos}/{companies_count}")

avg_posts_per_user = posts_count / users_count if users_count > 0 else 0
avg_comments_per_post = comments_count / posts_count if posts_count > 0 else 0
avg_connections_per_user = (connections_count * 2) / users_count if users_count > 0 else 0

print(f"\nENGAGEMENT STATS:")
print(f"Average posts per user: {avg_posts_per_user:.1f}")
print(f"Average comments per post: {avg_comments_per_post:.1f}")
print(f"Average connections per user: {avg_connections_per_user:.1f}")

print(f"\nYOUR LINKEDIN CLONE IS READY!")
print(f"Frontend: http://localhost:3000")
print(f"Backend API: http://localhost:8000/api/")
print(f"Admin Panel: http://localhost:8000/admin") 