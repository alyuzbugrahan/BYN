'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '../../contexts/AuthContext';
import { jobsAPI } from '../../utils/api';
import { JobStats, Job } from '../../types';
import LoadingSpinner from '../ui/LoadingSpinner';
import {
  BriefcaseIcon,
  BookmarkIcon,
  ClockIcon,
  EyeIcon,
  ChartBarIcon,
  PlusIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';

const DashboardContent: React.FC = () => {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const [stats, setStats] = useState<JobStats | null>(null);
  const [recommendedJobs, setRecommendedJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    // Wait for auth to be complete and user to be available
    if (authLoading || !isAuthenticated || !user) {
      setLoading(false);
      return;
    }

    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('Fetching dashboard data for user:', user.email);
        
        const defaultStats: JobStats = {
          applications_sent: 0,
          applications_pending: 0,
          applications_under_review: 0,
          saved_jobs: 0,
          jobs_posted: 0,
          active_jobs_posted: 0
        };
        
        const statsPromise = jobsAPI.getJobStats().catch((err) => {
          console.error('Failed to fetch job stats:', err);
          return defaultStats;
        });
        
        const jobsPromise = jobsAPI.getRecommendedJobs().catch((err) => {
          console.error('Failed to fetch recommended jobs:', err);
          return { results: [] as Job[] };
        });
        
        const [statsData, jobsData] = await Promise.all([statsPromise, jobsPromise]);
        
        console.log('Dashboard data loaded successfully:', { stats: statsData, jobCount: jobsData.results.length });
        setStats(statsData);
        setRecommendedJobs(jobsData.results.slice(0, 3));
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError('Failed to load dashboard data');
        setStats({
          applications_sent: 0,
          applications_pending: 0,
          applications_under_review: 0,
          saved_jobs: 0,
          jobs_posted: 0,
          active_jobs_posted: 0
        });
        setRecommendedJobs([]);
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(fetchDashboardData, 200);
    return () => clearTimeout(timeoutId);
  }, [authLoading, isAuthenticated, user]);

  const quickActions = [
    {
      name: 'Browse Jobs',
      description: 'Find your next opportunity',
      href: '/jobs',
      icon: BriefcaseIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'Create Job Post',
      description: 'Post a new job opening',
      href: '/jobs/create',
      icon: PlusIcon,
      color: 'bg-green-500',
      show: user?.is_company_user,
    },
    {
      name: 'View Network',
      description: 'Connect with professionals',
      href: '/connections',
      icon: EyeIcon,
      color: 'bg-purple-500',
    },
    {
      name: 'Update Profile',
      description: 'Keep your profile current',
      href: `/profile/${user?.id}`,
      icon: ChartBarIcon,
      color: 'bg-orange-500',
    },
  ].filter(action => action.show !== false);

  if (loading || authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-lg font-medium mb-2">Failed to load dashboard</div>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.first_name}!
          </h1>
          <p className="text-gray-600 mt-2">
            Here's what's happening in your professional world.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BriefcaseIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Applications Sent</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.applications_sent || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Under Review</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.applications_under_review || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BookmarkIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Saved Jobs</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.saved_jobs || 0}</p>
              </div>
            </div>
          </div>

          {user?.is_company_user && (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-8 w-8 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Active Job Posts</p>
                  <p className="text-2xl font-bold text-gray-900">{stats?.active_jobs_posted || 0}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Quick Actions */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">Quick Actions</h2>
              </div>
              <div className="p-6 space-y-4">
                {quickActions.map((action) => (
                  <Link
                    key={action.name}
                    href={action.href}
                    className="flex items-center p-3 rounded-lg border border-gray-200 hover:border-emerald-300 hover:shadow-sm transition-all"
                  >
                    <div className={`flex-shrink-0 p-2 rounded-lg ${action.color}`}>
                      <action.icon className="h-5 w-5 text-white" />
                    </div>
                    <div className="ml-3 flex-1">
                      <p className="text-sm font-medium text-gray-900">{action.name}</p>
                      <p className="text-xs text-gray-500">{action.description}</p>
                    </div>
                    <ArrowRightIcon className="h-4 w-4 text-gray-400" />
                  </Link>
                ))}
              </div>
            </div>
          </div>

          {/* Recommended Jobs */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <h2 className="text-lg font-medium text-gray-900">Recommended Jobs</h2>
                <Link
                  href="/jobs"
                  className="text-sm text-emerald-600 hover:text-emerald-700 font-medium"
                >
                  View all
                </Link>
              </div>
              <div className="p-6">
                {recommendedJobs.length > 0 ? (
                  <div className="space-y-4">
                    {recommendedJobs.map((job) => (
                      <div
                        key={job.id}
                        className="border border-gray-200 rounded-lg p-4 hover:border-emerald-300 hover:shadow-sm transition-all"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="text-sm font-medium text-gray-900">
                              <Link
                                href={`/jobs/${job.id}`}
                                className="hover:text-emerald-600"
                              >
                                {job.title}
                              </Link>
                            </h3>
                            <p className="text-sm text-gray-600 mt-1">{job.company.name}</p>
                            <p className="text-sm text-gray-500 mt-1">{job.location}</p>
                            <div className="flex items-center mt-2 space-x-4">
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                {job.job_type.replace('_', ' ')}
                              </span>
                              <span className="text-xs text-gray-500">
                                {format(new Date(job.posted_date), 'MMM dd, yyyy')}
                              </span>
                            </div>
                          </div>
                          <div className="ml-4 flex-shrink-0">
                            <Link
                              href={`/jobs/${job.id}`}
                              className="inline-flex items-center px-3 py-2 border border-emerald-600 text-sm leading-4 font-medium rounded-md text-emerald-600 bg-white hover:bg-emerald-50 transition-colors"
                            >
                              View
                            </Link>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <BriefcaseIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">No job recommendations available</p>
                    <Link
                      href="/jobs"
                      className="mt-2 text-emerald-600 hover:text-emerald-700 font-medium"
                    >
                      Browse all jobs
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardContent;
