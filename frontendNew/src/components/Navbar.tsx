'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
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
  const router = useRouter();
  const pathname = usePathname();

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
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
      setSearchQuery('');
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const getDisplayName = (user: User) => {
    return `${user.first_name} ${user.last_name}`.trim() || user.email;
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and Navigation */}
          <div className="flex items-center space-x-8">
            {/* Logo */}
            <Link href="/dashboard" className="flex-shrink-0 flex items-center">
              <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">BYN</span>
              </div>
            </Link>

            {/* Search */}
            <div className="hidden md:block">
              <form onSubmit={handleSearch} className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="block w-80 pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-green-500 focus:border-green-500 sm:text-sm"
                  placeholder="Search"
                />
              </form>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              const Icon = isActive ? item.iconSolid : item.icon;
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex flex-col items-center px-3 py-2 text-xs font-medium rounded-md transition-colors ${
                    isActive
                      ? 'text-green-600 bg-green-50'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="h-6 w-6 mb-1" />
                  {item.name}
                </Link>
              );
            })}

            {/* Notifications */}
            <Link
              href="/notifications"
              className="flex flex-col items-center px-3 py-2 text-xs font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
            >
              <BellIcon className="h-6 w-6 mb-1" />
              <span className="hidden lg:block">Notifications</span>
            </Link>

            {/* Profile Menu */}
            <div className="relative ml-3" ref={profileMenuRef}>
              <button
                onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors"
              >
                <div className="flex items-center space-x-2">
                  {user?.profile_picture_url ? (
                    <img
                      className="h-8 w-8 rounded-full object-cover"
                      src={user.profile_picture_url}
                      alt={getDisplayName(user)}
                    />
                  ) : (
                    <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                      <UserIcon className="h-5 w-5 text-gray-600" />
                    </div>
                  )}
                  <span className="hidden lg:block">{user?.first_name || 'Me'}</span>
                  <ChevronDownIcon className="h-4 w-4" />
                </div>
              </button>

              {/* Profile Dropdown */}
              {isProfileMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900">{getDisplayName(user!)}</p>
                    <p className="text-sm text-gray-500">{user?.email}</p>
                  </div>
                  <Link
                    href={`/profile/${user?.id}`}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setIsProfileMenuOpen(false)}
                  >
                    View Profile
                  </Link>
                  <Link
                    href="/settings"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setIsProfileMenuOpen(false)}
                  >
                    Settings
                  </Link>
                  {user?.is_company_user && (
                    <Link
                      href="/company-dashboard"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setIsProfileMenuOpen(false)}
                    >
                      Company Dashboard
                    </Link>
                  )}
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Sign out
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-green-500"
            >
              {isMobileMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white border-t border-gray-200">
            {/* Mobile Search */}
            <form onSubmit={handleSearch} className="px-3 pb-3">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-green-500 focus:border-green-500 sm:text-sm"
                  placeholder="Search"
                />
              </div>
            </form>

            {/* Mobile Navigation */}
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              const Icon = isActive ? item.iconSolid : item.icon;
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center px-3 py-2 text-base font-medium rounded-md ${
                    isActive
                      ? 'text-green-600 bg-green-50'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <Icon className="h-6 w-6 mr-3" />
                  {item.name}
                </Link>
              );
            })}

            <Link
              href="/notifications"
              className="flex items-center px-3 py-2 text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <BellIcon className="h-6 w-6 mr-3" />
              Notifications
            </Link>

            {/* Mobile Profile Section */}
            <div className="border-t border-gray-200 pt-4 pb-3">
              <div className="flex items-center px-5">
                {user?.profile_picture_url ? (
                  <img
                    className="h-10 w-10 rounded-full object-cover"
                    src={user.profile_picture_url}
                    alt={getDisplayName(user)}
                  />
                ) : (
                  <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                    <UserIcon className="h-6 w-6 text-gray-600" />
                  </div>
                )}
                <div className="ml-3">
                  <div className="text-base font-medium text-gray-800">{getDisplayName(user!)}</div>
                  <div className="text-sm font-medium text-gray-500">{user?.email}</div>
                </div>
              </div>
              <div className="mt-3 px-2 space-y-1">
                <Link
                  href={`/profile/${user?.id}`}
                  className="block px-3 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-50 rounded-md"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Your Profile
                </Link>
                <Link
                  href="/settings"
                  className="block px-3 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-50 rounded-md"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Settings
                </Link>
                {user?.is_company_user && (
                  <Link
                    href="/company-dashboard"
                    className="block px-3 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-50 rounded-md"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Company Dashboard
                  </Link>
                )}
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-3 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-50 rounded-md"
                >
                  Sign out
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
