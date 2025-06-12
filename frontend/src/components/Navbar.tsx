import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  HomeIcon,
  BriefcaseIcon,
  BuildingOfficeIcon,
  UserIcon,
  Bars3Icon,
  XMarkIcon,
  MagnifyingGlassIcon,
  BellIcon,
  ChevronDownIcon,
  UsersIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeSolid,
  BriefcaseIcon as BriefcaseSolid,
  BuildingOfficeIcon as BuildingOfficeSolid,
  UserIcon as UserSolid,
  UsersIcon as UsersSolid,
  ChartBarIcon as ChartBarSolid,
} from '@heroicons/react/24/solid';

const Navbar: React.FC = () => {
  const { user, logout, refreshUser } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  // Auto-refresh user data if is_company_user is undefined (but only after a delay)
  useEffect(() => {
    if (user && user.is_company_user === undefined) {
      console.log('Scheduling user data refresh due to missing is_company_user field...');
      const timeoutId = setTimeout(() => {
        refreshUser();
      }, 1000); // Wait 1 second before refreshing to avoid conflicts
      
      return () => clearTimeout(timeoutId);
    }
  }, [user, refreshUser]);
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const profileMenuRef = useRef<HTMLDivElement>(null);

  const navigation = [
    {
      name: 'Home',
      href: '/',
      icon: HomeIcon,
      iconSolid: HomeSolid,
    },
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: ChartBarIcon,
      iconSolid: ChartBarSolid,
    },
    {
      name: 'Jobs',
      href: '/jobs',
      icon: BriefcaseIcon,
      iconSolid: BriefcaseSolid,
    },
    {
      name: 'Companies',
      href: '/companies',
      icon: BuildingOfficeIcon,
      iconSolid: BuildingOfficeSolid,
    },
    {
      name: 'Network',
      href: '/connections',
      icon: UsersIcon,
      iconSolid: UsersSolid,
    },
    {
      name: 'Profile',
      href: `/profile/${user?.id}`,
      icon: UserIcon,
      iconSolid: UserSolid,
    },
  ];

  // Close profile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node)) {
        setIsProfileMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
    }
  };

  const handleLogout = () => {
    logout();
    setIsProfileMenuOpen(false);
  };

  const isActiveRoute = (href: string) => {
    if (href === '/') {
      return location.pathname === '/';
    }
    if (href === '/dashboard') {
      return location.pathname === '/dashboard';
    }
    return location.pathname.startsWith(href) && location.pathname !== '/' && location.pathname !== '/dashboard';
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 fixed top-0 w-full z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Search */}
          <div className="flex items-center space-x-4">
            <Link to="/" className="flex-shrink-0">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-8 h-8">
                <rect width="32" height="32" rx="8" fill="#22c55e" />
                <text x="50%" y="55%" textAnchor="middle" fill="white" fontSize="16" fontWeight="bold" fontFamily="Inter, sans-serif" dy=".3em">BYN</text>
              </svg>
            </Link>

            {/* Search Bar */}
            <form onSubmit={handleSearch} className="hidden md:block">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search people..."
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-gray-50 placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-green-500 focus:border-green-500"
                />
              </div>
            </form>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => {
              const isActive = isActiveRoute(item.href);
              const Icon = isActive ? item.iconSolid : item.icon;
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex flex-col items-center px-3 py-2 text-xs font-medium rounded-md transition-colors ${
                    isActive
                      ? 'text-green-600 bg-green-50'
                      : 'text-gray-600 hover:text-green-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-6 h-6 mb-1" />
                  {item.name}
                </Link>
              );
            })}

            {/* Notifications */}
            <Link
              to="/notifications"
              className={`flex flex-col items-center px-3 py-2 text-xs font-medium rounded-md transition-colors relative ${
                isActiveRoute('/notifications')
                  ? 'text-green-600 bg-green-50'
                  : 'text-gray-600 hover:text-green-600 hover:bg-gray-50'
              }`}
            >
              <div className="relative">
              <BellIcon className="w-6 h-6 mb-1" />
              </div>
              Notifications
            </Link>
          </div>

          {/* Profile Menu */}
          <div className="flex items-center space-x-4">
            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded-md text-gray-600 hover:text-green-600 hover:bg-gray-50"
            >
              {isMobileMenuOpen ? (
                <XMarkIcon className="w-6 h-6" />
              ) : (
                <Bars3Icon className="w-6 h-6" />
              )}
            </button>

            {/* Profile dropdown */}
            <div className="relative" ref={profileMenuRef}>
              <button
                onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
                className="flex items-center space-x-2 p-2 rounded-md text-gray-600 hover:text-green-600 hover:bg-gray-50 transition-colors"
              >
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  {user?.profile_picture ? (
                    <img
                      src={user.profile_picture}
                      alt={user.first_name}
                      className="w-8 h-8 rounded-full object-cover"
                    />
                  ) : (
                    <span className="text-sm font-medium text-gray-700">
                      {user?.first_name?.[0]}{user?.last_name?.[0]}
                    </span>
                  )}
                </div>
                <ChevronDownIcon className="w-4 h-4 hidden sm:block" />
              </button>

              {/* Profile dropdown menu */}
              {isProfileMenuOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50">
                  <div className="p-4 border-b border-gray-200">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center">
                        {user?.profile_picture ? (
                          <img
                            src={user.profile_picture}
                            alt={user.first_name}
                            className="w-12 h-12 rounded-full object-cover"
                          />
                        ) : (
                          <span className="text-lg font-medium text-gray-700">
                            {user?.first_name?.[0]}{user?.last_name?.[0]}
                          </span>
                        )}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {user?.first_name} {user?.last_name}
                        </p>
                        <p className="text-sm text-gray-500 truncate">
                          {user?.headline || user?.current_position || 'Professional'}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="py-1">
                    <Link
                      to={`/profile/${user?.id}`}
                      onClick={() => setIsProfileMenuOpen(false)}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      View Profile
                    </Link>
                    {user?.is_company_user && (
                      <>
                        <Link
                          to="/company-dashboard"
                          onClick={() => setIsProfileMenuOpen(false)}
                          className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          Company Dashboard
                        </Link>
                        <Link
                          to="/jobs/create"
                          onClick={() => setIsProfileMenuOpen(false)}
                          className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          Post a Job
                        </Link>
                      </>
                    )}
                    <div className="border-t border-gray-200 mt-1 pt-1">
                      <button
                        onClick={handleLogout}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Sign out
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 pt-4 pb-3">
            {/* Mobile Search */}
            <form onSubmit={handleSearch} className="px-2 pb-3">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search jobs..."
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-gray-50 placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-byn-500 focus:border-byn-500"
                />
              </div>
            </form>

            {/* Mobile Navigation Links */}
            <div className="space-y-1">
              {navigation.map((item) => {
                const isActive = isActiveRoute(item.href);
                const Icon = isActive ? item.iconSolid : item.icon;
                
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={`flex items-center px-3 py-2 text-base font-medium rounded-md ${
                      isActive
                        ? 'text-byn-600 bg-byn-50'
                        : 'text-gray-600 hover:text-byn-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-6 h-6 mr-3" />
                    {item.name}
                  </Link>
                );
              })}
              <Link
                to="/notifications"
                className={`flex items-center px-3 py-2 text-base font-medium rounded-md ${
                  isActiveRoute('/notifications')
                    ? 'text-byn-600 bg-byn-50'
                    : 'text-gray-600 hover:text-byn-600 hover:bg-gray-50'
                }`}
              >
                <div className="relative">
                <BellIcon className="w-6 h-6 mr-3" />
                </div>
                Notifications
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar; 