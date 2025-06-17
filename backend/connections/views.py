from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db import IntegrityError, transaction
from drf_spectacular.utils import extend_schema, extend_schema_view

from accounts.models import User
from .models import ConnectionRequest, Connection, Follow, UserRecommendation, NetworkMetrics
from .serializers import (
    ConnectionRequestSerializer, ConnectionSerializer, FollowSerializer,
    UserRecommendationSerializer, NetworkMetricsSerializer
)
from feed.utils import create_notification


class ConnectionPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema_view(
    list=extend_schema(description='List connection requests'),
    create=extend_schema(description='Create a connection request'),
    respond=extend_schema(description='Accept or decline a connection request'),
    withdraw=extend_schema(description='Withdraw a connection request')
)
class ConnectionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ConnectionRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ConnectionPagination
    queryset = ConnectionRequest.objects.none()  # Default empty queryset
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ConnectionRequest.objects.none()
        user = self.request.user
        return ConnectionRequest.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).select_related('sender', 'receiver').order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Send a connection request"""
        receiver_id = request.data.get('receiver_id')
        message = request.data.get('message', '')
        
        if not receiver_id:
            return Response({'detail': 'receiver_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if receiver == request.user:
            return Response({'detail': 'You cannot send a connection request to yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if users are already connected
        existing_connection = Connection.objects.filter(
            Q(user1=request.user, user2=receiver) | Q(user1=receiver, user2=request.user)
        ).exists()
        
        if existing_connection:
            return Response({'detail': 'You are already connected to this user.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                conn_req, created = ConnectionRequest.objects.get_or_create(
                    sender=request.user,
                    receiver=receiver,
                    defaults={'message': message, 'status': 'pending'}
                )
                
                if not created:
                    if conn_req.status == 'pending':
                        return Response({'detail': 'Connection request already sent.'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Update existing request
                        conn_req.message = message
                        conn_req.status = 'pending'
                        conn_req.save()
                
                # Create notification for receiver
                create_notification(
                    recipient=receiver,
                    sender=request.user,
                    notification_type='connection_request',
                    title=f"{request.user.full_name} sent you a connection request",
                    message=f"You have a new connection request from {request.user.full_name}",
                    action_url=f"/connections/requests/"
                )
                
                serializer = self.get_serializer(conn_req)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        except IntegrityError:
            return Response({'detail': 'Connection request already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """Accept or decline a connection request"""
        connection_request = self.get_object()
        action_type = request.data.get('action')  # 'accept' or 'decline'
        
        if connection_request.receiver != request.user:
            return Response({'detail': 'You can only respond to requests sent to you.'}, status=status.HTTP_403_FORBIDDEN)
        
        if connection_request.status != 'pending':
            return Response({'detail': 'This request has already been responded to.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if action_type not in ['accept', 'decline']:
            return Response({'detail': 'Action must be either "accept" or "decline".'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            connection_request.status = 'accepted' if action_type == 'accept' else 'declined'
            connection_request.responded_at = timezone.now()
            connection_request.save()
            
            if action_type == 'accept':
                # Create the connection
                Connection.objects.create(
                    user1=connection_request.sender,
                    user2=connection_request.receiver,
                    connection_request=connection_request
                )
                
                # Create notification for sender
                create_notification(
                    recipient=connection_request.sender,
                    sender=request.user,
                    notification_type='connection_request',
                    title=f"{request.user.full_name} accepted your connection request",
                    message=f"You are now connected with {request.user.full_name}",
                    action_url=f"/profile/{request.user.id}/"
                )
                
                return Response({'status': 'accepted', 'message': 'Connection request accepted'})
            else:
                return Response({'status': 'declined', 'message': 'Connection request declined'})
    
    @action(detail=True, methods=['delete'])
    def withdraw(self, request, pk=None):
        """Withdraw a connection request"""
        connection_request = self.get_object()
        
        if connection_request.sender != request.user:
            return Response({'detail': 'You can only withdraw requests you sent.'}, status=status.HTTP_403_FORBIDDEN)
        
        if connection_request.status != 'pending':
            return Response({'detail': 'You can only withdraw pending requests.'}, status=status.HTTP_400_BAD_REQUEST)
        
        connection_request.status = 'withdrawn'
        connection_request.save()
        
        return Response({'status': 'withdrawn', 'message': 'Connection request withdrawn'})


@extend_schema_view(
    list=extend_schema(description='List connections'),
    retrieve=extend_schema(description='Get a specific connection'),
    remove=extend_schema(description='Remove a connection')
)
class ConnectionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConnectionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ConnectionPagination
    queryset = Connection.objects.none()  # Default empty queryset
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Connection.objects.none()
        user = self.request.user
        return Connection.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).select_related('user1', 'user2', 'connection_request').order_by('-connected_at')
    
    @action(detail=True, methods=['delete'])
    def remove(self, request, pk=None):
        """Remove a connection"""
        connection = self.get_object()
        
        if connection.user1 != request.user and connection.user2 != request.user:
            return Response({'detail': 'You can only remove your own connections.'}, status=status.HTTP_403_FORBIDDEN)
        
        connection.delete()
        return Response({'status': 'removed', 'message': 'Connection removed'})


@extend_schema_view(
    list=extend_schema(description='List follows'),
    create=extend_schema(description='Follow a user'),
    unfollow=extend_schema(description='Unfollow a user'),
    followers=extend_schema(description='List followers'),
    following=extend_schema(description='List following')
)
class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ConnectionPagination
    queryset = Follow.objects.none()  # Default empty queryset
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Follow.objects.none()
        user = self.request.user
        return Follow.objects.filter(follower=user).select_related('following').order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Follow a user"""
        following_id = request.data.get('following_id')
        
        if not following_id:
            return Response({'detail': 'following_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            following_user = User.objects.get(id=following_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if following_user == request.user:
            return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=following_user
        )
        
        if created:
            # Create notification
            create_notification(
                recipient=following_user,
                sender=request.user,
                notification_type='follow',
                title=f"{request.user.full_name} started following you",
                message=f"You have a new follower: {request.user.full_name}",
                action_url=f"/profile/{request.user.id}/"
            )
            
            serializer = self.get_serializer(follow)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'You are already following this user.'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    def unfollow(self, request):
        """Unfollow a user"""
        following_id = request.data.get('following_id')
        
        if not following_id:
            return Response({'detail': 'following_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            follow = Follow.objects.get(follower=request.user, following_id=following_id)
            follow.delete()
            return Response({'status': 'unfollowed', 'message': 'User unfollowed'})
        except Follow.DoesNotExist:
            return Response({'detail': 'You are not following this user.'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def followers(self, request):
        """Get user's followers"""
        user_id = request.query_params.get('user_id', request.user.id)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        followers = Follow.objects.filter(following=user).select_related('follower')
        page = self.paginate_queryset(followers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def following(self, request):
        """Get users that the user is following"""
        user_id = request.query_params.get('user_id', request.user.id)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        following = Follow.objects.filter(follower=user).select_related('following')
        page = self.paginate_queryset(following)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(description='List user recommendations'),
    retrieve=extend_schema(description='Get a specific recommendation'),
    dismiss=extend_schema(description='Dismiss a recommendation')
)
class UserRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserRecommendationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ConnectionPagination
    queryset = UserRecommendation.objects.none()  # Default empty queryset
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return UserRecommendation.objects.none()
        return UserRecommendation.objects.filter(
            user=self.request.user,
            is_dismissed=False
        ).select_related('recommended_user').order_by('-score')
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss a user recommendation"""
        recommendation = self.get_object()
        recommendation.is_dismissed = True
        recommendation.dismissed_at = timezone.now()
        recommendation.save()
        
        return Response({'status': 'dismissed', 'message': 'Recommendation dismissed'})


@extend_schema_view(
    list=extend_schema(description='List network metrics'),
    my_metrics=extend_schema(description='Get current user network metrics')
)
class NetworkMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NetworkMetricsSerializer
    permission_classes = [IsAuthenticated]
    queryset = NetworkMetrics.objects.none()  # Default empty queryset
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return NetworkMetrics.objects.none()
        return NetworkMetrics.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_metrics(self, request):
        """Get current user's network metrics"""
        metrics, created = NetworkMetrics.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(metrics)
        return Response(serializer.data)


# Helper function to get user connections
def get_user_connections(user):
    """Get all users connected to the given user"""
    connections = Connection.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).select_related('user1', 'user2')
    
    connected_users = []
    for connection in connections:
        if connection.user1 == user:
            connected_users.append(connection.user2)
        else:
            connected_users.append(connection.user1)
    
    return connected_users 