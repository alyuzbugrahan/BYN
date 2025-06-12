import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import UserCard from '../components/UserCard';
import { User } from '../types';
import { connectionsAPI, usersAPI } from '../utils/api';
import {
  UserPlusIcon,
  UserMinusIcon,
  CheckIcon,
  XMarkIcon,
  UsersIcon,
  BellIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';

interface LocalUser extends User {
  full_name: string;
}

interface ConnectionRequest {
  id: number;
  sender: LocalUser;
  receiver: LocalUser;
  message: string;
  status: string;
  created_at: string;
}

interface Connection {
  id: number;
  user1: LocalUser;
  user2: LocalUser;
  other_user: LocalUser;
  connected_at: string;
  interaction_count: number;
}

const ConnectionsPage: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'discover' | 'requests' | 'connections'>('discover');
  const [connectionRequests, setConnectionRequests] = useState<ConnectionRequest[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [suggestedUsers, setSuggestedUsers] = useState<LocalUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      if (activeTab === 'discover') {
        // Load all data needed for filtering
        const [usersData, connectionsData, requestsData] = await Promise.all([
          usersAPI.getUsers(),
          connectionsAPI.getConnections(),
          connectionsAPI.getConnectionRequests()
        ]);
        
        const allUsers = usersData.results;
        const allConnections = connectionsData.results;
        const allRequests = requestsData.results;
        
        // Filter out current user, existing connections, and users with pending requests
        const filteredUsers = allUsers.filter((u: User) => {
          // Exclude current user
          if (u.id === user?.id) return false;
          
          // Exclude users who are already connected
          const isConnected = allConnections.some((conn: any) => 
            conn.other_user?.id === u.id || 
            conn.user1?.id === u.id || 
            conn.user2?.id === u.id
          );
          if (isConnected) return false;
          
          // Exclude users with pending connection requests (sent or received)
          const hasPendingRequest = allRequests.some((req: any) => 
            req.status === 'pending' && (
              (req.sender.id === user?.id && req.receiver.id === u.id) ||
              (req.receiver.id === user?.id && req.sender.id === u.id)
            )
          );
          if (hasPendingRequest) return false;
          
          return true;
        });
        
        // Convert User objects to LocalUser objects with full_name
        const usersWithFullName: LocalUser[] = filteredUsers.map((u: User) => ({
          ...u,
          full_name: `${u.first_name} ${u.last_name}`
        }));
        
        setSuggestedUsers(usersWithFullName);
        
        // Also set the connections and requests data since we loaded them
        const connectionsWithFullName = allConnections.map((conn: any) => ({
          ...conn,
          other_user: {
            ...conn.other_user,
            full_name: `${conn.other_user.first_name} ${conn.other_user.last_name}`
          }
        }));
        setConnections(connectionsWithFullName);
        
        const requestsWithFullName = allRequests.map((req: any) => ({
          ...req,
          sender: {
            ...req.sender,
            full_name: `${req.sender.first_name} ${req.sender.last_name}`
          },
          receiver: {
            ...req.receiver,
            full_name: `${req.receiver.first_name} ${req.receiver.last_name}`
          }
        }));
        setConnectionRequests(requestsWithFullName);
      } else if (activeTab === 'requests') {
        const requestsData = await connectionsAPI.getConnectionRequests();
        const requestsWithFullName = requestsData.results.map((req: any) => ({
          ...req,
          sender: {
            ...req.sender,
            full_name: `${req.sender.first_name} ${req.sender.last_name}`
          },
          receiver: {
            ...req.receiver,
            full_name: `${req.receiver.first_name} ${req.receiver.last_name}`
          }
        }));
        setConnectionRequests(requestsWithFullName);
      } else {
        const connectionsData = await connectionsAPI.getConnections();
        const connectionsWithFullName = connectionsData.results.map((conn: any) => ({
          ...conn,
          other_user: {
            ...conn.other_user,
            full_name: `${conn.other_user.first_name} ${conn.other_user.last_name}`
          }
        }));
        setConnections(connectionsWithFullName);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };



  const handleConnectionRequest = async (requestId: number, action: 'accept' | 'decline') => {
    try {
      setActionLoading(requestId);
      await connectionsAPI.respondToConnectionRequest(requestId, action);
      // Reload data to reflect changes
      loadData();
    } catch (error) {
      console.error('Error handling connection request:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const removeConnection = async (connectionId: number) => {
    try {
      setActionLoading(connectionId);
      await connectionsAPI.removeConnection(connectionId);
      // Reload data to reflect changes
      loadData();
    } catch (error) {
      console.error('Error removing connection:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const getReceivedRequests = () => {
    return connectionRequests.filter(req => req.receiver.id === user?.id && req.status === 'pending');
  };

  const getSentRequests = () => {
    return connectionRequests.filter(req => req.sender.id === user?.id && req.status === 'pending');
  };

  const getFilteredUsers = () => {
    if (!searchQuery) return suggestedUsers;
    return suggestedUsers.filter(u => 
      u.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.headline?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.current_position?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">My Network</h1>
          <p className="text-gray-600">Discover and manage your professional connections</p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex">
              <button
                onClick={() => setActiveTab('discover')}
                className={`py-4 px-6 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  activeTab === 'discover'
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <MagnifyingGlassIcon className="w-5 h-5" />
                  <span>Discover People</span>
                </div>
              </button>
              <button
                onClick={() => setActiveTab('requests')}
                className={`py-4 px-6 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  activeTab === 'requests'
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <BellIcon className="w-5 h-5" />
                  <span>Requests</span>
                  {getReceivedRequests().length > 0 && (
                    <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1">
                      {getReceivedRequests().length}
                    </span>
                  )}
                </div>
              </button>
              <button
                onClick={() => setActiveTab('connections')}
                className={`py-4 px-6 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  activeTab === 'connections'
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <UsersIcon className="w-5 h-5" />
                  <span>My Connections</span>
                  <span className="bg-gray-200 text-gray-700 text-xs rounded-full px-2 py-1">
                    {connections.length}
                  </span>
                </div>
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Discover People Tab */}
            {activeTab === 'discover' && (
              <div>
                {/* Search Bar */}
                <div className="mb-6">
                  <div className="relative">
                    <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search people by name, headline, or position..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* People Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {getFilteredUsers().map((suggestedUser) => (
                    <UserCard
                      key={suggestedUser.id}
                      user={suggestedUser}
                      showConnectButton={true}
                      onConnectionStatusChange={(userId, status) => {
                        if (status === 'pending') {
                          // Remove user from suggested users list when request is sent
                          setSuggestedUsers(prev => prev.filter(u => u.id !== userId));
                          // Reload data to ensure all tabs are updated with the new request
                          loadData();
                        }
                      }}
                    />
                  ))}
                </div>

                {getFilteredUsers().length === 0 && (
                  <div className="text-center py-12">
                    <MagnifyingGlassIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      {searchQuery ? 'No people found' : 'No suggestions available'}
                    </h3>
                    <p className="text-gray-600">
                      {searchQuery 
                        ? 'Try adjusting your search terms' 
                        : 'Check back later for new connection suggestions'
                      }
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Requests Tab */}
            {activeTab === 'requests' && (
              <div className="space-y-6">
                {/* Received Requests */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Received Requests ({getReceivedRequests().length})
                  </h3>
                  {getReceivedRequests().length === 0 ? (
                    <p className="text-gray-500 text-center py-8">No pending connection requests</p>
                  ) : (
                    <div className="space-y-4">
                      {getReceivedRequests().map((request) => (
                        <div key={request.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow duration-200">
                          <div className="flex items-center space-x-4">
                            <img
                              src={request.sender.profile_picture_url || '/default-avatar.png'}
                              alt={`${request.sender.first_name} ${request.sender.last_name}`}
                              className="w-12 h-12 rounded-full object-cover"
                            />
                            <div>
                              <h4 className="font-semibold text-gray-900">{request.sender.first_name} {request.sender.last_name}</h4>
                              <p className="text-sm text-gray-600">{request.sender.headline}</p>
                              {request.message && (
                                <p className="text-sm text-gray-500 mt-1">"{request.message}"</p>
                              )}
                              <p className="text-xs text-gray-400 mt-1">
                                {new Date(request.created_at).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleConnectionRequest(request.id, 'accept')}
                              disabled={actionLoading === request.id}
                              className="flex items-center space-x-1 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors duration-200 disabled:opacity-50"
                            >
                              <CheckIcon className="w-4 h-4" />
                              <span>Accept</span>
                            </button>
                            <button
                              onClick={() => handleConnectionRequest(request.id, 'decline')}
                              disabled={actionLoading === request.id}
                              className="flex items-center space-x-1 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors duration-200 disabled:opacity-50"
                            >
                              <XMarkIcon className="w-4 h-4" />
                              <span>Decline</span>
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Sent Requests */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Sent Requests ({getSentRequests().length})
                  </h3>
                  {getSentRequests().length === 0 ? (
                    <p className="text-gray-500 text-center py-8">No pending sent requests</p>
                  ) : (
                    <div className="space-y-4">
                      {getSentRequests().map((request) => (
                        <div key={request.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                          <div className="flex items-center space-x-4">
                            <img
                              src={request.receiver.profile_picture_url || '/default-avatar.png'}
                              alt={`${request.receiver.first_name} ${request.receiver.last_name}`}
                              className="w-12 h-12 rounded-full object-cover"
                            />
                            <div>
                              <h4 className="font-semibold text-gray-900">{request.receiver.first_name} {request.receiver.last_name}</h4>
                              <p className="text-sm text-gray-600">{request.receiver.headline}</p>
                              <p className="text-xs text-gray-400 mt-1">
                                Sent on {new Date(request.created_at).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          <div className="text-sm text-yellow-600 font-medium">
                            Pending
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Connections Tab */}
            {activeTab === 'connections' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  My Connections ({connections.length})
                </h3>
                {connections.length === 0 ? (
                  <div className="text-center py-12">
                    <UsersIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500 text-lg mb-2">No connections yet</p>
                    <p className="text-gray-400">Start building your professional network!</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {connections.map((connection) => (
                      <div key={connection.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow duration-200">
                        <div className="flex items-center space-x-4">
                          <img
                                                          src={connection.other_user.profile_picture_url || '/default-avatar.png'}
                            alt={`${connection.other_user.first_name} ${connection.other_user.last_name}`}
                            className="w-12 h-12 rounded-full object-cover"
                          />
                          <div>
                            <h4 className="font-semibold text-gray-900">{connection.other_user.first_name} {connection.other_user.last_name}</h4>
                            <p className="text-sm text-gray-600">{connection.other_user.headline}</p>
                            <p className="text-xs text-gray-400 mt-1">
                              Connected on {new Date(connection.connected_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={() => removeConnection(connection.id)}
                          disabled={actionLoading === connection.id}
                          className="flex items-center space-x-1 px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-200 disabled:opacity-50"
                        >
                          <UserMinusIcon className="w-4 h-4" />
                          <span className="text-sm">Remove</span>
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConnectionsPage; 