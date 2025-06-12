import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { companiesAPI, jobsAPI } from '../utils/api';
import { Company, Job } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  BuildingOfficeIcon,
  MapPinIcon,
  UserGroupIcon,
  CalendarIcon,
  GlobeAltIcon,
  HeartIcon,
  PlusIcon,
  BriefcaseIcon,
  CurrencyDollarIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import {
  HeartIcon as HeartSolidIcon,
  CheckBadgeIcon
} from '@heroicons/react/24/solid';

const CompanyDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  
  const [company, setCompany] = useState<Company | null>(null);
  const [companyJobs, setCompanyJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [following, setFollowing] = useState(false);

  useEffect(() => {
    if (id) {
      fetchCompanyDetails();
    }
  }, [id]);

  const fetchCompanyDetails = async () => {
    try {
      setLoading(true);
      const companyData = await companiesAPI.getCompany(parseInt(id!));
      setCompany(companyData);
      setFollowing(companyData.is_following || false);
      
      // Fetch company jobs
      setJobsLoading(true);
      const jobsData = await jobsAPI.getJobs({
        company_name: companyData.name,
        page: 1
      });
      setCompanyJobs(jobsData.results);
    } catch (error) {
      console.error('Error fetching company details:', error);
      toast.error('Failed to load company details');
    } finally {
      setLoading(false);
      setJobsLoading(false);
    }
  };

  const handleFollowToggle = async () => {
    if (!company) return;
    
    try {
      if (following) {
        await companiesAPI.unfollowCompany(company.id);
        setFollowing(false);
        setCompany({ 
          ...company, 
          follower_count: company.follower_count - 1,
          is_following: false 
        });
        toast.success(`Unfollowed ${company.name}`);
      } else {
        await companiesAPI.followCompany(company.id);
        setFollowing(true);
        setCompany({ 
          ...company, 
          follower_count: company.follower_count + 1,
          is_following: true 
        });
        toast.success(`Following ${company.name}`);
      }
    } catch (error) {
      toast.error('Failed to update follow status');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatSalaryRange = (job: Job) => {
    if (job.salary_min && job.salary_max) {
      return `${job.salary_currency} ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}`;
    } else if (job.salary_min) {
      return `${job.salary_currency} ${job.salary_min.toLocaleString()}+`;
    }
    return 'Competitive salary';
  };

  const getJobType = (type: string) => {
    const types = {
      'full_time': 'Full-time',
      'part_time': 'Part-time',
      'contract': 'Contract',
      'internship': 'Internship',
      'temporary': 'Temporary'
    };
    return types[type as keyof typeof types] || type;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!company) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Company Not Found</h2>
          <p className="text-gray-600 mb-6">The company you're looking for doesn't exist or has been removed.</p>
          <Link
            to="/companies"
            className="px-6 py-3 bg-linkedin-500 text-white rounded-md hover:bg-linkedin-600"
          >
            Back to Companies
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Company Header */}
          <div className="bg-white rounded-lg shadow-card overflow-hidden">
            {/* Cover Image */}
            <div className="h-48 bg-gradient-to-r from-linkedin-500 to-linkedin-600">
              {company.cover_image && (
                <img
                  src={company.cover_image}
                  alt={`${company.name} cover`}
                  className="w-full h-full object-cover"
                />
              )}
            </div>
            
            {/* Company Info */}
            <div className="p-6">
              <div className="flex items-start space-x-4 -mt-16 mb-4">
                {company.logo ? (
                  <img
                    src={company.logo}
                    alt={company.name}
                    className="w-24 h-24 rounded-lg border-4 border-white bg-white object-cover"
                  />
                ) : (
                  <div className="w-24 h-24 rounded-lg border-4 border-white bg-white flex items-center justify-center">
                    <BuildingOfficeIcon className="w-12 h-12 text-gray-400" />
                  </div>
                )}
                <div className="flex-1 pt-12">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <h1 className="text-3xl font-bold text-gray-900">{company.name}</h1>
                        {company.is_verified && (
                          <CheckBadgeIcon className="w-6 h-6 text-blue-500" />
                        )}
                      </div>
                      <p className="text-lg text-gray-600">{company.industry?.name}</p>
                    </div>
                    
                    <button
                      onClick={handleFollowToggle}
                      className={`flex items-center space-x-2 px-6 py-2 rounded-md transition-colors ${
                        following
                          ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          : 'bg-linkedin-500 text-white hover:bg-linkedin-600'
                      }`}
                    >
                      {following ? (
                        <>
                          <HeartSolidIcon className="w-5 h-5" />
                          <span>Following</span>
                        </>
                      ) : (
                        <>
                          <PlusIcon className="w-5 h-5" />
                          <span>Follow</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* Company Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">{company.follower_count}</div>
                  <div className="text-sm text-gray-600">Followers</div>
                </div>
                
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">{companyJobs.length}</div>
                  <div className="text-sm text-gray-600">Open Jobs</div>
                </div>
                
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">{company.company_size}</div>
                  <div className="text-sm text-gray-600">Employees</div>
                </div>
                
                {company.founded_year && (
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{new Date().getFullYear() - company.founded_year}</div>
                    <div className="text-sm text-gray-600">Years Old</div>
                  </div>
                )}
              </div>

              {/* Company Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                {company.headquarters && (
                  <div className="flex items-center space-x-2">
                    <MapPinIcon className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-600">Headquarters: {company.headquarters}</span>
                  </div>
                )}
                
                {company.founded_year && (
                  <div className="flex items-center space-x-2">
                    <CalendarIcon className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-600">Founded: {company.founded_year}</span>
                  </div>
                )}
                
                <div className="flex items-center space-x-2">
                  <UserGroupIcon className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-600">Company size: {company.company_size}</span>
                </div>
                
                {company.website && (
                  <div className="flex items-center space-x-2">
                    <GlobeAltIcon className="w-5 h-5 text-gray-400" />
                    <a
                      href={company.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-linkedin-600 hover:text-linkedin-700"
                    >
                      Website
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* About Company */}
          {company.description && (
            <div className="bg-white rounded-lg shadow-card p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">About {company.name}</h2>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-line">{company.description}</p>
              </div>
            </div>
          )}

          {/* Open Jobs */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                Open Jobs ({companyJobs.length})
              </h2>
              {companyJobs.length > 0 && (
                <Link
                  to={`/jobs?company=${company.name}`}
                  className="text-linkedin-600 hover:text-linkedin-700 flex items-center space-x-1"
                >
                  <span>View all</span>
                  <ChevronRightIcon className="w-4 h-4" />
                </Link>
              )}
            </div>

            {jobsLoading ? (
              <div className="flex justify-center py-8">
                <LoadingSpinner size="medium" />
              </div>
            ) : companyJobs.length === 0 ? (
              <div className="text-center py-8">
                <BriefcaseIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-600">No open positions at the moment</p>
              </div>
            ) : (
              <div className="space-y-4">
                {companyJobs.slice(0, 5).map((job) => (
                  <Link
                    key={job.id}
                    to={`/jobs/${job.id}`}
                    className="block p-4 border border-gray-200 rounded-lg hover:border-linkedin-300 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-1">{job.title}</h3>
                        
                        <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                          <div className="flex items-center space-x-1">
                            <MapPinIcon className="w-4 h-4" />
                            <span>{job.location}</span>
                          </div>
                          
                          <div className="flex items-center space-x-1">
                            <ClockIcon className="w-4 h-4" />
                            <span>{getJobType(job.job_type)}</span>
                          </div>
                          
                          {(job.salary_min || job.salary_max) && (
                            <div className="flex items-center space-x-1">
                              <CurrencyDollarIcon className="w-4 h-4" />
                              <span>{formatSalaryRange(job)}</span>
                            </div>
                          )}
                        </div>
                        
                        <p className="text-gray-700 text-sm line-clamp-2">{job.description}</p>
                        
                        {job.skills_required.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {job.skills_required.slice(0, 3).map((skill) => (
                              <span
                                key={skill.id}
                                className="px-2 py-1 bg-linkedin-100 text-linkedin-700 text-xs rounded-full"
                              >
                                {skill.name}
                              </span>
                            ))}
                            {job.skills_required.length > 3 && (
                              <span className="text-xs text-gray-500 px-2 py-1">
                                +{job.skills_required.length - 3} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                      
                      <div className="ml-4 text-right">
                        <div className="text-sm text-gray-500">
                          {Math.floor((Date.now() - new Date(job.created_at).getTime()) / (1000 * 60 * 60 * 24))} days ago
                        </div>
                        <div className="text-sm text-gray-500 mt-1">
                          {job.application_count} applicants
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <Link
                to={`/jobs?company=${company.name}`}
                className="block w-full px-4 py-2 text-center border border-linkedin-500 text-linkedin-500 rounded-md hover:bg-linkedin-50 transition-colors"
              >
                View All Jobs
              </Link>
              
              {company.website && (
                <a
                  href={company.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full px-4 py-2 text-center bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                >
                  Visit Website
                </a>
              )}
            </div>
          </div>

          {/* Company Insights */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Company Insights</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Industry</span>
                <span className="font-medium">{company.industry?.name || 'Not specified'}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600">Company size</span>
                <span className="font-medium">{company.company_size}</span>
              </div>
              
              {company.founded_year && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Founded</span>
                  <span className="font-medium">{company.founded_year}</span>
                </div>
              )}
              
              <div className="flex justify-between">
                <span className="text-gray-600">Followers</span>
                <span className="font-medium">{company.follower_count.toLocaleString()}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600">Open positions</span>
                <span className="font-medium">{companyJobs.length}</span>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <h3 className="font-semibold text-gray-900 mb-4">Recent Activity</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-gray-600">
                  Posted {companyJobs.filter(job => {
                    const daysDiff = (Date.now() - new Date(job.created_at).getTime()) / (1000 * 60 * 60 * 24);
                    return daysDiff <= 7;
                  }).length} new jobs this week
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-gray-600">Updated company profile</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanyDetailPage; 