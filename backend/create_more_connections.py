#!/usr/bin/env python
"""
Script to create more realistic connections between users
"""
import os
import django
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linkedin_clone.settings')
django.setup()

from accounts.models import User
from connections.models import ConnectionRequest, Connection
from feed.utils import create_notification

def create_more_connections():
    print("🌐 Creating More Realistic Connection Network")
    print("=" * 50)
    
    users = list(User.objects.all())
    if len(users) < 3:
        print("❌ Need at least 3 users to create connections")
        return
    
    print(f"👥 Found {len(users)} users")
    
    # Create connection messages
    connection_messages = [
        "Hi! I'd love to connect and expand my professional network.",
        "Hello! I see we share similar interests. Let's connect!",
        "Hi there! I'd like to add you to my professional network.",
        "Hello! I noticed we work in similar fields. Would love to connect!",
        "Hi! I came across your profile and would love to connect.",
        "Hello! Let's connect and share professional insights.",
    ]
    
    connections_created = 0
    
    # Create connections between users (each user connects with 2-3 others)
    for user in users:
        # Get potential connections (exclude self and existing connections)
        existing_connections = set()
        for conn in Connection.objects.filter(user1=user):
            existing_connections.add(conn.user2.id)
        for conn in Connection.objects.filter(user2=user):
            existing_connections.add(conn.user1.id)
        
        potential_connections = [u for u in users if u.id != user.id and u.id not in existing_connections]
        
        # Connect with 1-2 random users
        num_connections = min(random.randint(1, 2), len(potential_connections))
        chosen_connections = random.sample(potential_connections, num_connections)
        
        for target_user in chosen_connections:
            # Check if request already exists
            existing_request = ConnectionRequest.objects.filter(
                sender=user, receiver=target_user
            ).first() or ConnectionRequest.objects.filter(
                sender=target_user, receiver=user
            ).first()
            
            if not existing_request:
                # Create connection request
                message = random.choice(connection_messages)
                conn_req = ConnectionRequest.objects.create(
                    sender=user,
                    receiver=target_user,
                    message=message,
                    status='accepted'  # Auto-accept for sample data
                )
                
                # Create the connection
                connection = Connection.objects.create(
                    user1=user,
                    user2=target_user,
                    connection_request=conn_req
                )
                
                print(f"🤝 Connected {user.full_name} ↔ {target_user.full_name}")
                connections_created += 1
                
                # Create notifications
                create_notification(
                    recipient=target_user,
                    sender=user,
                    notification_type='connection_request',
                    title=f"{user.full_name} connected with you",
                    message=f"You are now connected with {user.full_name}",
                    action_url=f"/profile/{user.id}/"
                )
    
    print(f"\n✅ Created {connections_created} new connections!")
    
    # Show final statistics
    total_connections = Connection.objects.count()
    total_users = User.objects.count()
    
    print(f"\n📊 Final Network Statistics:")
    print(f"👥 Total users: {total_users}")
    print(f"🤝 Total connections: {total_connections}")
    print(f"📊 Average connections per user: {total_connections * 2 / total_users:.1f}")
    
    # Show connection details for each user
    print(f"\n🔗 User Connection Details:")
    for user in users:
        user_connections = get_user_connections(user)
        print(f"• {user.full_name}: {len(user_connections)} connections")
        if user_connections:
            connections_list = ", ".join([c.full_name for c in user_connections[:3]])
            more_text = f" and {len(user_connections)-3} more" if len(user_connections) > 3 else ""
            print(f"  Connected with: {connections_list}{more_text}")

def get_user_connections(user):
    """Get all connections for a user"""
    from django.db.models import Q
    
    connections = Connection.objects.filter(
        Q(user1=user) | Q(user2=user)
    )
    
    connected_users = []
    for conn in connections:
        if conn.user1 == user:
            connected_users.append(conn.user2)
        else:
            connected_users.append(conn.user1)
    
    return connected_users

if __name__ == '__main__':
    create_more_connections() 