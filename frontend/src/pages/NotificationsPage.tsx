import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { Notification, PaginatedResponse } from '../types';
import { feedAPI } from '../utils/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { BellIcon } from '@heroicons/react/24/outline';

const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [markingAll, setMarkingAll] = useState(false);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const response: PaginatedResponse<Notification> = await feedAPI.getNotifications();
      setNotifications(response.results);
    } catch (err) {
      setError('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId: number) => {
    try {
      await feedAPI.markNotificationAsRead(notificationId);
      setNotifications(prev => prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n));
    } catch (err) {
      // Optionally handle error
    }
  };

  const markAllAsRead = async () => {
    setMarkingAll(true);
    try {
      await feedAPI.markAllNotificationsAsRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (err) {
      // Optionally handle error
    } finally {
      setMarkingAll(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center"><LoadingSpinner size="large" /></div>;
  }

  if (error) {
    return <div className="min-h-screen flex items-center justify-center text-red-600">{error}</div>;
  }

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="min-h-screen bg-gray-50 pt-16">
      <div className="max-w-2xl mx-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">Notifications</h1>
          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              disabled={markingAll}
              className="px-4 py-2 bg-linkedin-600 text-white rounded-md hover:bg-linkedin-700 text-sm font-medium disabled:opacity-50"
            >
              {markingAll ? 'Marking...' : 'Mark all as read'}
            </button>
          )}
        </div>
        {notifications.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <BellIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No notifications yet</h3>
            <p className="text-gray-600">You'll see notifications here when people interact with your posts or send you connection requests.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {notifications.map(notification => (
              <div
                key={notification.id}
                className={`bg-white rounded-lg shadow-sm border p-4 flex items-start gap-4 ${!notification.is_read ? 'border-l-4 border-l-linkedin-600' : 'border-gray-200'}`}
                onClick={() => !notification.is_read && markAsRead(notification.id)}
                style={{ cursor: !notification.is_read ? 'pointer' : 'default' }}
              >
                <div className="p-2 rounded-full bg-gray-100 flex items-center justify-center w-14 h-14">
                  {notification.sender && notification.sender.profile_picture_url ? (
                    <img
                      src={notification.sender.profile_picture_url}
                      alt={notification.sender.first_name}
                      className="w-10 h-10 rounded-full object-cover"
                    />
                  ) : (
                    <BellIcon className="w-8 h-8 text-linkedin-600" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {notification.sender && (
                      <Link to={`/profile/${notification.sender.id}`} className="font-medium text-gray-900 hover:text-linkedin-600">
                        {notification.sender.first_name} {notification.sender.last_name}
                      </Link>
                    )}
                    <span className="text-xs text-gray-500 ml-auto">
                      {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                    </span>
                  </div>
                  <div className="font-medium text-gray-900">{notification.title}</div>
                  <div className="text-gray-600 text-sm">{notification.message}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationsPage; 