import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { jobsAPI } from '../utils/api';
import { JobStats, Job } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
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

const DashboardPage: React.FC = () => {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const [stats, setStats] = useState<JobStats | null>(null);
  const [recommendedJobs, setRecommendedJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Wait for auth to be complete and user to be available
    if (authLoading) {
      return;
    }

    // If not authenticated, don't try to fetch data
    if (!isAuthenticated || !user) {
      setLoading(false);
      return;
    }

    // Add a small delay after authentication to ensure all context is settled
    const timeoutId = setTimeout(() => {
      const fetchDashboardData = async () => {
        try {
          setLoading(true);
          setError(null);
          console.log('Fetching dashboard data for user:', user.email);
          
          // Add timeout to prevent infinite loading
          const timeout = new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Request timeout')), 10000)
          );
          
          const statsPromise = jobsAPI.getJobStats().catch((err): JobStats => {
            console.error('Failed to fetch job stats:', err);
            return {
              applications_sent: 0,
              applications_pending: 0,
              applications_under_review: 0,
              saved_jobs: 0,
              jobs_posted: 0,
              active_jobs_posted: 0
            };
          });
          
          const jobsPromise = jobsAPI.getRecommendedJobs().catch((err) => {
            console.error('Failed to fetch recommended jobs:', err);
            return { results: [] as Job[] };
          });
          
          const [statsData, jobsData] = await Promise.race([
            Promise.all([statsPromise, jobsPromise]),
            timeout
          ]) as [JobStats, { results: Job[] }];
          
          console.log('Dashboard data loaded successfully:', { stats: statsData, jobCount: jobsData.results.length });
          setStats(statsData);
          setRecommendedJobs(jobsData.results.slice(0, 3));
        } catch (error) {
          console.error('Error fetching dashboard data:', error);
          setError('Failed to load dashboard data');
          // Set default empty state
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

      fetchDashboardData();
    }, 200); // 200ms delay to ensure auth context is fully settled

    return () => clearTimeout(timeoutId);
  }, [authLoading, isAuthenticated, user]);

  const quickActions = [
    {
      name: 'Browse Jobs',
      href: '/jobs',
      icon: BriefcaseIcon,
      color: 'bg-blue-500',
      description: 'Find your next opportunity',
    },
    {
      name: 'View Profile',
      href: `/profile/${user?.id}`,
      icon: EyeIcon,
      color: 'bg-green-500',
      description: 'Update your profile',
    },
    {
      name: 'Companies',
      href: '/companies',
      icon: ChartBarIcon,
      color: 'bg-purple-500',
      description: 'Explore companies',
    },
  ];

  const formatSalaryRange = (job: Job) => {
    if (job.salary_min && job.salary_max) {
      return `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}`;
    }
    return 'Salary not specified';
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-gray-600">Authenticating...</p>
          <p className="mt-2 text-sm text-gray-500">Setting up your session</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-gray-600">Loading your dashboard...</p>
          <p className="mt-2 text-sm text-gray-500">Fetching your latest activity</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to load dashboard</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-byn-500 text-white rounded-md hover:bg-byn-600"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.first_name}!
        </h1>
        <p className="mt-2 text-gray-600">
          Here's what's happening in your professional world
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-8">
          {/* Job Statistics */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">Your Job Activity</h2>
            {stats && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-2">
                    <BriefcaseIcon className="w-6 h-6 text-blue-600" />
                  </div>
                  <p className="text-2xl font-bold text-gray-900">{stats.applications_sent}</p>
                  <p className="text-sm text-gray-600">Applications Sent</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center w-12 h-12 bg-yellow-100 rounded-lg mx-auto mb-2">
                    <ClockIcon className="w-6 h-6 text-yellow-600" />
                  </div>
                  <p className="text-2xl font-bold text-gray-900">{stats.applications_pending}</p>
                  <p className="text-sm text-gray-600">Pending</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mx-auto mb-2">
                    <ChartBarIcon className="w-6 h-6 text-green-600" />
                  </div>
                  <p className="text-2xl font-bold text-gray-900">{stats.applications_under_review}</p>
                  <p className="text-sm text-gray-600">Under Review</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-2">
                    <BookmarkIcon className="w-6 h-6 text-purple-600" />
                  </div>
                  <p className="text-2xl font-bold text-gray-900">{stats.saved_jobs}</p>
                  <p className="text-sm text-gray-600">Saved Jobs</p>
                </div>
              </div>
            )}
            <div className="mt-6 flex justify-center">
              <Link
                to="/jobs"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-byn-500 hover:bg-byn-600"
              >
                View All Applications
                <ArrowRightIcon className="ml-2 w-4 h-4" />
              </Link>
            </div>
          </div>

          {/* Recommended Jobs */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Recommended for You</h2>
              <Link
                to="/jobs"
                className="text-byn-500 hover:text-byn-600 text-sm font-medium"
              >
                View all jobs
              </Link>
            </div>
            
            {recommendedJobs.length > 0 ? (
              <div className="space-y-4">
                {recommendedJobs.map((job) => (
                  <div
                    key={job.id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <Link
                          to={`/jobs/${job.id}`}
                          className="text-lg font-semibold text-gray-900 hover:text-byn-600"
                        >
                          {job.title}
                        </Link>
                        <p className="text-gray-600 mt-1">{job.company.name}</p>
                        <p className="text-gray-500 text-sm mt-1">
                          {job.location} • {job.workplace_type.replace('_', ' ')}
                        </p>
                        <p className="text-byn-600 font-medium text-sm mt-2">
                          {formatSalaryRange(job)}
                        </p>
                        <div className="flex flex-wrap gap-2 mt-3">
                          {job.skills_required.slice(0, 3).map((skill) => (
                            <span
                              key={skill.id}
                              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-byn-100 text-byn-800"
                            >
                              {skill.name}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="flex flex-col items-end ml-4">
                        <p className="text-xs text-gray-500">
                          {format(new Date(job.created_at), 'MMM d')}
                        </p>
                        <Link
                          to={`/jobs/${job.id}`}
                          className="mt-2 inline-flex items-center px-3 py-1 border border-byn-500 text-xs font-medium rounded text-byn-500 hover:bg-byn-50"
                        >
                          View Job
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <BriefcaseIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No recommended jobs yet</h3>
                <p className="text-gray-600 mb-4">
                  Complete your profile to get personalized job recommendations.
                </p>
                <Link
                  to="/jobs"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-byn-500 hover:bg-byn-600"
                >
                  Browse All Jobs
                  <ArrowRightIcon className="ml-2 w-4 h-4" />
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Profile Card */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="text-center">
              <div className="w-20 h-20 bg-gray-300 rounded-full mx-auto mb-4 flex items-center justify-center">
                {user?.profile_picture ? (
                  <img
                    src={user.profile_picture}
                    alt={user.first_name}
                    className="w-20 h-20 rounded-full object-cover"
                  />
                ) : (
                  <span className="text-2xl font-bold text-gray-700">
                    {user?.first_name?.[0]}{user?.last_name?.[0]}
                  </span>
                )}
              </div>
              <h3 className="text-lg font-semibold text-gray-900">
                {user?.first_name} {user?.last_name}
              </h3>
              <p className="text-gray-600 text-sm mt-1">
                {user?.headline || user?.current_position || 'Professional'}
              </p>
              <p className="text-gray-500 text-sm">
                {user?.location || 'Location not specified'}
              </p>
              <Link
                to={`/profile/${user?.id}`}
                className="mt-4 w-full inline-flex justify-center items-center px-4 py-2 border border-byn-500 text-sm font-medium rounded-md text-byn-500 hover:bg-byn-50"
              >
                View Profile
              </Link>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              {quickActions.map((action) => (
                <Link
                  key={action.name}
                  to={action.href}
                  className="flex items-center p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className={`flex items-center justify-center w-10 h-10 rounded-lg ${action.color} mr-3`}>
                    <action.icon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{action.name}</p>
                    <p className="text-sm text-gray-500">{action.description}</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Tips */}
          <div className="bg-byn-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-byn-900 mb-4">
              💡 Profile Tips
            </h3>
            <div className="space-y-3 text-sm text-byn-800">
              <p>• Add a professional photo to get 14x more profile views</p>
              <p>• Complete your experience section to attract recruiters</p>
              <p>• Add skills to show your expertise</p>
              <p>• Write a compelling headline to stand out</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage; 