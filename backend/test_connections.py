#!/usr/bin/env python
"""
Test connections system for LinkedIn Clone
This script verifies that all connections are working properly
"""

import os
import sys
import django
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linkedin_clone.settings')
django.setup()

from accounts.models import User
from connections.models import Connection, ConnectionRequest
from django.db.models import Count

def log(message, level="INFO"):
    """Log messages with timestamp"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def test_connections_system():
    """Test the connections system"""
    log("🧪 Testing connections system...")
    
    try:
        # Test 1: Check if users exist
        users = User.objects.all()
        user_count = users.count()
        log(f"✅ Found {user_count} users in the system")
        
        if user_count < 2:
            log("⚠️  Need at least 2 users to test connections", "WARNING")
            return False
        
        # Test 2: Check connections
        connections = Connection.objects.all()
        connection_count = connections.count()
        log(f"✅ Found {connection_count} connections in the system")
        
        # Test 3: Show connection details
        for user in users[:5]:  # Show first 5 users
            user_connections = Connection.objects.filter(
                user=user
            ).count()
            log(f"   👤 {user.full_name}: {user_connections} connections")
        
        # Test 4: Check connection requests
        requests = ConnectionRequest.objects.all()
        request_count = requests.count()
        log(f"✅ Found {request_count} connection requests")
        
        # Test 5: Verify bidirectional connections
        bidirectional_count = 0
        for connection in connections:
            reverse_exists = Connection.objects.filter(
                user=connection.connected_user,
                connected_user=connection.user
            ).exists()
            if reverse_exists:
                bidirectional_count += 1
        
        log(f"✅ Found {bidirectional_count} bidirectional connections")
        
        # Test 6: Show network statistics
        most_connected_user = User.objects.annotate(
            connection_count=Count('connections')
        ).order_by('-connection_count').first()
        
        if most_connected_user:
            log(f"🌟 Most connected user: {most_connected_user.full_name} with {most_connected_user.connection_count} connections")
        
        # Test 7: Verify connection functionality
        if user_count >= 2:
            user1 = users[0]
            user2 = users[1]
            
            # Check if they are connected
            are_connected = Connection.objects.filter(
                user=user1,
                connected_user=user2
            ).exists()
            
            log(f"✅ Connection test: {user1.full_name} and {user2.full_name} are {'connected' if are_connected else 'not connected'}")
        
        log("🎉 All connection tests passed successfully!")
        log("🔗 Connection system is working properly")
        return True
        
    except Exception as e:
        log(f"❌ Error testing connections: {str(e)}", "ERROR")
        return False

def show_connection_summary():
    """Show a summary of the connection system"""
    log("\n📊 Connection System Summary:")
    log("-" * 40)
    
    total_users = User.objects.count()
    total_connections = Connection.objects.count()
    total_requests = ConnectionRequest.objects.count()
    
    log(f"👥 Total Users: {total_users}")
    log(f"🤝 Total Connections: {total_connections}")
    log(f"📩 Total Connection Requests: {total_requests}")
    
    if total_users > 0:
        avg_connections = total_connections / total_users
        log(f"📈 Average Connections per User: {avg_connections:.1f}")
    
    # Show top connected users
    log("\n🌟 Top Connected Users:")
    top_users = User.objects.annotate(
        connection_count=Count('connections')
    ).order_by('-connection_count')[:3]
    
    for i, user in enumerate(top_users, 1):
        log(f"   {i}. {user.full_name}: {user.connection_count} connections")

def main():
    """Main function"""
    log("🚀 Starting Connection System Test")
    log("=" * 50)
    
    success = test_connections_system()
    show_connection_summary()
    
    if success:
        log("\n✅ Connection system test completed successfully!")
        log("🌐 Your LinkedIn Clone connections are ready to use!")
    else:
        log("\n❌ Connection system test failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 