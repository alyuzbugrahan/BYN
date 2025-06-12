#!/usr/bin/env python
"""
Test script for connection functionality
This script demonstrates how the connection system works and creates sample connections
"""

import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linkedin_clone.settings')
django.setup()

from accounts.models import User
from connections.models import ConnectionRequest, Connection
from feed.models import Post, Notification
from feed.utils import create_notification

def test_connections():
    print("🔗 Testing BYN Connection System")
    print("=" * 50)
    
    # Get some users
    users = User.objects.all()[:4]
    if len(users) < 2:
        print("❌ Need at least 2 users to test connections")
        return
    
    user1, user2 = users[0], users[1]
    print(f"👤 User 1: {user1.full_name} (ID: {user1.id})")
    print(f"👤 User 2: {user2.full_name} (ID: {user2.id})")
    
    # Test 1: Send connection request
    print("\n📤 Test 1: Sending connection request...")
    conn_req, created = ConnectionRequest.objects.get_or_create(
        sender=user1,
        receiver=user2,
        defaults={'message': 'Hi! I would like to connect with you.', 'status': 'pending'}
    )
    
    if created:
        print(f"✅ Connection request sent from {user1.full_name} to {user2.full_name}")
        
        # Create notification
        create_notification(
            recipient=user2,
            sender=user1,
            notification_type='connection_request',
            title=f"{user1.full_name} sent you a connection request",
            message=f"You have a new connection request from {user1.full_name}",
            action_url=f"/connections/requests/"
        )
        print("📧 Notification created for connection request")
    else:
        print(f"ℹ️  Connection request already exists (Status: {conn_req.status})")
    
    # Test 2: Accept connection request
    print("\n✅ Test 2: Accepting connection request...")
    if conn_req.status == 'pending':
        conn_req.status = 'accepted'
        conn_req.save()
        
        # Create the connection
        connection, created = Connection.objects.get_or_create(
            user1=user1,
            user2=user2,
            defaults={'connection_request': conn_req}
        )
        
        if created:
            print(f"🤝 Connection established between {user1.full_name} and {user2.full_name}")
            
            # Create notification for sender
            create_notification(
                recipient=user1,
                sender=user2,
                notification_type='connection_request',
                title=f"{user2.full_name} accepted your connection request",
                message=f"You are now connected with {user2.full_name}",
                action_url=f"/profile/{user2.id}/"
            )
            print("📧 Notification created for connection acceptance")
        else:
            print("ℹ️  Connection already exists")
    else:
        print(f"ℹ️  Connection request status: {conn_req.status}")
    
    # Test 3: Create a post and test connection notifications
    print("\n📝 Test 3: Testing connection post notifications...")
    
    # Create a post by user1
    post = Post.objects.create(
        author=user1,
        content="Just implemented an amazing connection system for BYN! 🚀 #networking #connections #BYN",
        visibility='public',
        is_approved=True
    )
    print(f"📄 Post created by {user1.full_name}: {post.content[:50]}...")
    
    # Get connected users
    from connections.views import get_user_connections
    connected_users = get_user_connections(user1)
    print(f"🔗 {user1.full_name} has {len(connected_users)} connections")
    
    # Create notifications for connected users
    for connected_user in connected_users:
        create_notification(
            recipient=connected_user,
            sender=user1,
            notification_type='connection_post',
            title=f"{user1.full_name} shared a new post",
            message=f"Your connection {user1.full_name} posted: {post.content[:100]}...",
            post=post,
            action_url=f"/feed/post/{post.id}/"
        )
        print(f"📧 Post notification sent to {connected_user.full_name}")
    
    # Test 4: Show statistics
    print("\n📊 Test 4: Connection Statistics")
    print("-" * 30)
    
    total_requests = ConnectionRequest.objects.count()
    pending_requests = ConnectionRequest.objects.filter(status='pending').count()
    accepted_requests = ConnectionRequest.objects.filter(status='accepted').count()
    total_connections = Connection.objects.count()
    total_notifications = Notification.objects.count()
    
    print(f"📤 Total connection requests: {total_requests}")
    print(f"⏳ Pending requests: {pending_requests}")
    print(f"✅ Accepted requests: {accepted_requests}")
    print(f"🤝 Total connections: {total_connections}")
    print(f"📧 Total notifications: {total_notifications}")
    
    # Test 5: Show recent notifications
    print("\n📧 Test 5: Recent Notifications")
    print("-" * 30)
    
    recent_notifications = Notification.objects.order_by('-created_at')[:5]
    for notification in recent_notifications:
        print(f"• {notification.title}")
        print(f"  To: {notification.recipient.full_name}")
        print(f"  From: {notification.sender.full_name if notification.sender else 'System'}")
        print(f"  Type: {notification.notification_type}")
        print(f"  Time: {notification.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    print("🎉 Connection system test completed successfully!")
    print("\n🔗 Available API Endpoints:")
    print("• GET /api/connections/requests/ - List connection requests")
    print("• POST /api/connections/requests/ - Send connection request")
    print("• POST /api/connections/requests/{id}/respond/ - Accept/decline request")
    print("• GET /api/connections/connections/ - List connections")
    print("• DELETE /api/connections/connections/{id}/remove/ - Remove connection")
    print("• GET /api/feed/notifications/ - List notifications")

if __name__ == '__main__':
    test_connections() 