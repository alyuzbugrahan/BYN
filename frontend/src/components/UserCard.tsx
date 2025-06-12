import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { User } from '../types';
import { connectionsAPI } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import {
  UserIcon,
  UserPlusIcon,
  CheckIcon,
  ClockIcon,
  MapPinIcon,
  BriefcaseIcon,
} from '@heroicons/react/24/outline';

interface UserCardProps {
  user: User;
  showConnectButton?: boolean;
  onConnectionStatusChange?: (userId: number, status: 'none' | 'pending' | 'connected') => void;
  className?: string;
}

const UserCard: React.FC<UserCardProps> = ({ 
  user, 
  showConnectButton = true, 
  onConnectionStatusChange,
  className = ''
}) => {
  const { user: currentUser } = useAuth();
  const [connectionStatus, setConnectionStatus] = useState<'none' | 'pending' | 'connected'>('none');
  const [loading, setLoading] = useState(false);

  const isOwnProfile = currentUser?.id === user.id;

  const handleConnect = async () => {
    if (!currentUser || isOwnProfile || connectionStatus !== 'none') return;

    try {
      setLoading(true);
      await connectionsAPI.sendConnectionRequest(user.id, `Hi ${user.first_name}! I'd like to connect with you on BYN.`);
      setConnectionStatus('pending');
      onConnectionStatusChange?.(user.id, 'pending');
      toast.success('Connection request sent!');
    } catch (error) {
      console.error('Error sending connection request:', error);
      toast.error('Failed to send connection request');
    } finally {
      setLoading(false);
    }
  };

  const getConnectButtonContent = () => {
    if (loading) {
      return (
        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
      );
    }

    switch (connectionStatus) {
      case 'connected':
        return (
          <>
            <CheckIcon className="w-4 h-4" />
            <span>Connected</span>
          </>
        );
      case 'pending':
        return (
          <>
            <ClockIcon className="w-4 h-4" />
            <span>Pending</span>
          </>
        );
      default:
        return (
          <>
            <UserPlusIcon className="w-4 h-4" />
            <span>Connect</span>
          </>
        );
    }
  };

  const getConnectButtonStyles = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'bg-green-500 text-white cursor-default';
      case 'pending':
        return 'bg-gray-400 text-white cursor-default';
      default:
        return 'bg-green-600 text-white hover:bg-green-700';
    }
  };

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow duration-200 ${className}`}>
      <div className="flex flex-col items-center text-center">
        {/* Profile Picture */}
        <Link to={`/profile/${user.id}`} className="mb-4">
                      <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center">
            {user.profile_picture ? (
              <img
                src={user.profile_picture}
                alt={`${user.first_name} ${user.last_name}`}
                className="w-16 h-16 rounded-full object-cover"
              />
            ) : (
              <span className="text-white font-semibold text-lg">
                {user.first_name?.[0]}{user.last_name?.[0]}
              </span>
            )}
          </div>
        </Link>
        
        {/* User Info */}
        <Link to={`/profile/${user.id}`} className="mb-2">
          <h3 className="font-semibold text-gray-900 hover:text-green-600 transition-colors">
            {user.first_name} {user.last_name}
          </h3>
        </Link>
        
        {user.headline && (
          <p className="text-sm text-gray-600 mb-2 line-clamp-2">
            {user.headline}
          </p>
        )}
        
        {user.current_position && (
          <div className="flex items-center text-xs text-gray-500 mb-2">
            <BriefcaseIcon className="w-3 h-3 mr-1" />
            <span className="line-clamp-1">{user.current_position}</span>
          </div>
        )}
        
        {user.location && (
          <div className="flex items-center text-xs text-gray-500 mb-4">
            <MapPinIcon className="w-3 h-3 mr-1" />
            <span>{user.location}</span>
          </div>
        )}
        
        {/* Connect Button */}
        {showConnectButton && !isOwnProfile && (
          <button
            onClick={handleConnect}
            disabled={loading || connectionStatus !== 'none'}
            className={`w-full px-4 py-2 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed ${getConnectButtonStyles()}`}
          >
            {getConnectButtonContent()}
          </button>
        )}

        {/* View Profile Button for own profile */}
        {isOwnProfile && (
          <Link
            to={`/profile/${user.id}`}
            className="w-full px-4 py-2 rounded-lg border border-green-600 text-green-600 hover:bg-green-50 transition-colors duration-200 flex items-center justify-center space-x-2"
          >
            <UserIcon className="w-4 h-4" />
            <span>View Profile</span>
          </Link>
        )}
      </div>
    </div>
  );
};

export default UserCard; 