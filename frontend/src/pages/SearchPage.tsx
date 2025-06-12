import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { usersAPI } from '../utils/api';
import { User } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import UserCard from '../components/UserCard';
import {
  MagnifyingGlassIcon,
  UserGroupIcon,
  AdjustmentsHorizontalIcon,
} from '@heroicons/react/24/outline';

const SearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [searchResults, setSearchResults] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    const query = searchParams.get('q');
    if (query) {
      setSearchQuery(query);
      performSearch(query);
    }
  }, [searchParams]);

  const performSearch = async (query: string) => {
    if (!query.trim()) return;

    try {
      setLoading(true);
      setHasSearched(true);
      const results = await usersAPI.searchUsers(query);
      setSearchResults(results.results);
    } catch (error) {
      console.error('Error searching users:', error);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    // Update URL with search query
    setSearchParams({ q: searchQuery });
    performSearch(searchQuery);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Search People</h1>
          <p className="text-gray-600">Find and connect with professionals on BYN</p>
        </div>

        {/* Search Form */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name, headline, position, or industry..."
                value={searchQuery}
                onChange={handleInputChange}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !searchQuery.trim()}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <MagnifyingGlassIcon className="w-5 h-5" />
              )}
              <span>Search</span>
            </button>
          </form>
        </div>

        {/* Search Results */}
        {loading && (
          <div className="flex justify-center py-12">
            <LoadingSpinner />
          </div>
        )}

        {!loading && hasSearched && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            {searchResults.length > 0 ? (
              <>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-semibold text-gray-900">
                    Search Results ({searchResults.length})
                  </h2>
                  <button className="flex items-center space-x-2 text-gray-600 hover:text-gray-800">
                    <AdjustmentsHorizontalIcon className="w-5 h-5" />
                    <span>Filters</span>
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {searchResults.map((user) => (
                    <UserCard
                      key={user.id}
                      user={user}
                      showConnectButton={true}
                      onConnectionStatusChange={(userId, status) => {
                        if (status === 'pending') {
                          // Optionally update the UI to show the request was sent
                          console.log(`Connection request sent to user ${userId}`);
                        }
                      }}
                    />
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-12">
                <UserGroupIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
                <p className="text-gray-600 mb-4">
                  We couldn't find any people matching "{searchQuery}"
                </p>
                <p className="text-sm text-gray-500">
                  Try adjusting your search terms or browse suggested connections
                </p>
              </div>
            )}
          </div>
        )}

        {/* Search Suggestions */}
        {!hasSearched && (
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Search Tips</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Search by:</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Name (first or last name)</li>
                  <li>• Job title or position</li>
                  <li>• Company name</li>
                  <li>• Industry</li>
                  <li>• Skills or expertise</li>
                </ul>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Popular searches:</h3>
                <div className="flex flex-wrap gap-2">
                  {['Software Engineer', 'Product Manager', 'Designer', 'Marketing', 'Sales'].map((term) => (
                    <button
                      key={term}
                      onClick={() => {
                        setSearchQuery(term);
                        setSearchParams({ q: term });
                        performSearch(term);
                      }}
                      className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition-colors"
                    >
                      {term}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPage; 