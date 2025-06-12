import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { jobsAPI, companiesAPI } from '../utils/api';
import { Job, Company } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  MapPinIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  ClockIcon,
  BookmarkIcon,
  ShareIcon,
  BuildingOfficeIcon,
  UserGroupIcon,
  AcademicCapIcon,
  CheckBadgeIcon,
  HeartIcon,
  PaperAirplaneIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import {
  BookmarkIcon as BookmarkSolidIcon,
  HeartIcon as HeartSolidIcon
} from '@heroicons/react/24/solid';

const JobDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [job, setJob] = useState<Job | null>(null);
  const [relatedJobs, setRelatedJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showApplicationModal, setShowApplicationModal] = useState(false);
  const [applicationData, setApplicationData] = useState({
    cover_letter: '',
    portfolio_url: ''
  });

  useEffect(() => {
    if (id) {
      fetchJobDetails();
    }
  }, [id]);

  const fetchJobDetails = async () => {
    try {
      setLoading(true);
      const jobData = await jobsAPI.getJob(parseInt(id!));
      setJob(jobData);
      
      // Fetch related jobs (same company or similar skills)
      const relatedJobsData = await jobsAPI.getJobs({
        company_name: jobData.company.name,
        page: 1
      });
      
      // Filter out current job
      const filtered = relatedJobsData.results.filter(j => j.id !== jobData.id).slice(0, 3);
      setRelatedJobs(filtered);
    } catch (error) {
      console.error('Error fetching job details:', error);
      toast.error('Failed to load job details');
      navigate('/jobs');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveJob = async () => {
    if (!job) return;
    
    try {
      setSaving(true);
      if (job.is_saved) {
        await jobsAPI.unsaveJob(job.id);
        setJob({ ...job, is_saved: false });
        toast.success('Job removed from saved jobs');
      } else {
        await jobsAPI.saveJob(job.id);
        setJob({ ...job, is_saved: true });
        toast.success('Job saved successfully');
      }
    } catch (error) {
      toast.error('Failed to update saved status');
    } finally {
      setSaving(false);
    }
  };

  const handleApply = async () => {
    if (!job) return;
    
    try {
      setApplying(true);
      await jobsAPI.applyForJob(job.id, applicationData);
      setJob({ ...job, has_applied: true });
      setShowApplicationModal(false);
      setApplicationData({ cover_letter: '', portfolio_url: '' });
      toast.success('Application submitted successfully!');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to submit application';
      toast.error(errorMessage);
    } finally {
      setApplying(false);
    }
  };

  const getWorkplaceTypeIcon = (type: string) => {
    switch (type) {
      case 'remote':
        return '🏠';
      case 'hybrid':
        return '🏢🏠';
      default:
        return '🏢';
    }
  };

  const formatSalary = (job: Job) => {
    if (job.salary_min && job.salary_max) {
      return `${job.salary_currency} ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()} ${job.salary_type}`;
    } else if (job.salary_min) {
      return `${job.salary_currency} ${job.salary_min.toLocaleString()}+ ${job.salary_type}`;
    }
    return 'Salary not disclosed';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getDaysAgo = (dateString: string) => {
    const diff = Date.now() - new Date(dateString).getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    if (days === 0) return 'Today';
    if (days === 1) return '1 day ago';
    return `${days} days ago`;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Job Not Found</h2>
          <p className="text-gray-600 mb-6">The job you're looking for doesn't exist or has been removed.</p>
          <button
            onClick={() => navigate('/jobs')}
            className="px-6 py-3 bg-linkedin-500 text-white rounded-md hover:bg-linkedin-600"
          >
            Back to Jobs
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Job Header */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{job.title}</h1>
                <Link 
                  to={`/companies/${job.company.id}`}
                  className="text-lg text-linkedin-500 hover:text-linkedin-600 font-medium flex items-center space-x-2"
                >
                  <BuildingOfficeIcon className="w-5 h-5" />
                  <span>{job.company.name}</span>
                  {job.company.is_verified && <CheckBadgeIcon className="w-5 h-5 text-blue-500" />}
                </Link>
              </div>
              
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleSaveJob}
                  disabled={saving}
                  className={`p-2 rounded-full transition-colors ${
                    job.is_saved 
                      ? 'bg-linkedin-500 text-white' 
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {job.is_saved ? (
                    <BookmarkSolidIcon className="w-5 h-5" />
                  ) : (
                    <BookmarkIcon className="w-5 h-5" />
                  )}
                </button>
                
                <button className="p-2 bg-gray-100 text-gray-600 rounded-full hover:bg-gray-200">
                  <ShareIcon className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Job Meta */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="flex items-center space-x-2 text-gray-600">
                <MapPinIcon className="w-5 h-5" />
                <span>{job.location}</span>
                <span>{getWorkplaceTypeIcon(job.workplace_type)}</span>
              </div>
              
              <div className="flex items-center space-x-2 text-gray-600">
                <ClockIcon className="w-5 h-5" />
                <span className="capitalize">{job.job_type.replace('_', '-')}</span>
              </div>
              
              <div className="flex items-center space-x-2 text-gray-600">
                <AcademicCapIcon className="w-5 h-5" />
                <span className="capitalize">{job.experience_level} level</span>
              </div>
              
              <div className="flex items-center space-x-2 text-gray-600">
                <CalendarIcon className="w-5 h-5" />
                <span>Posted {getDaysAgo(job.created_at)}</span>
              </div>
            </div>

            {/* Salary */}
            {(job.salary_min || job.salary_max) && (
              <div className="flex items-center space-x-2 text-green-600 font-semibold mb-6">
                <CurrencyDollarIcon className="w-5 h-5" />
                <span>{formatSalary(job)}</span>
              </div>
            )}

            {/* Apply Button */}
            <div className="flex space-x-4">
              {job.has_applied ? (
                <div className="flex items-center space-x-2 px-6 py-3 bg-green-100 text-green-700 rounded-md">
                  <CheckBadgeIcon className="w-5 h-5" />
                  <span>Application Submitted</span>
                </div>
              ) : (
                <button
                  onClick={() => setShowApplicationModal(true)}
                  className="flex items-center space-x-2 px-6 py-3 bg-linkedin-500 text-white rounded-md hover:bg-linkedin-600 transition-colors"
                >
                  <PaperAirplaneIcon className="w-5 h-5" />
                  <span>Apply Now</span>
                </button>
              )}
              
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span>{job.application_count} applicants</span>
                <span>{job.view_count} views</span>
              </div>
            </div>
          </div>

          {/* Job Description */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">About this role</h2>
            <div className="prose max-w-none">
              <p className="text-gray-700 whitespace-pre-line">{job.description}</p>
            </div>
          </div>

          {/* Requirements */}
          {job.requirements && (
            <div className="bg-white rounded-lg shadow-card p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Requirements</h2>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-line">{job.requirements}</p>
              </div>
            </div>
          )}

          {/* Responsibilities */}
          {job.responsibilities && (
            <div className="bg-white rounded-lg shadow-card p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Responsibilities</h2>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-line">{job.responsibilities}</p>
              </div>
            </div>
          )}

          {/* Skills */}
          {(job.skills_required.length > 0 || job.skills_preferred.length > 0) && (
            <div className="bg-white rounded-lg shadow-card p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Skills</h2>
              
              {job.skills_required.length > 0 && (
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Required Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {job.skills_required.map((skill) => (
                      <span
                        key={skill.id}
                        className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium"
                      >
                        {skill.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {job.skills_preferred.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Preferred Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {job.skills_preferred.map((skill) => (
                      <span
                        key={skill.id}
                        className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium"
                      >
                        {skill.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Company Info */}
          <div className="bg-white rounded-lg shadow-card p-6">
            <div className="flex items-center space-x-3 mb-4">
              {job.company.logo ? (
                <img 
                  src={job.company.logo} 
                  alt={job.company.name}
                  className="w-12 h-12 rounded-lg object-cover"
                />
              ) : (
                <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                  <BuildingOfficeIcon className="w-6 h-6 text-gray-400" />
                </div>
              )}
              <div>
                <h3 className="font-semibold text-gray-900">{job.company.name}</h3>
                <p className="text-sm text-gray-500">{job.company.industry?.name}</p>
              </div>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex items-center space-x-2">
                <UserGroupIcon className="w-4 h-4 text-gray-400" />
                <span className="text-gray-600">{job.company.company_size} employees</span>
              </div>
              
              {job.company.headquarters && (
                <div className="flex items-center space-x-2">
                  <MapPinIcon className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-600">{job.company.headquarters}</span>
                </div>
              )}
              
              <div className="flex items-center space-x-2">
                <HeartIcon className="w-4 h-4 text-gray-400" />
                <span className="text-gray-600">{job.company.follower_count} followers</span>
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t">
              <Link
                to={`/companies/${job.company.id}`}
                className="block w-full text-center px-4 py-2 border border-linkedin-500 text-linkedin-500 rounded-md hover:bg-linkedin-50 transition-colors"
              >
                View Company
              </Link>
            </div>
          </div>

          {/* Application Deadline */}
          {job.application_deadline && (
            <div className="bg-white rounded-lg shadow-card p-6">
              <h3 className="font-semibold text-gray-900 mb-2">Application Deadline</h3>
              <div className="flex items-center space-x-2 text-red-600">
                <CalendarIcon className="w-5 h-5" />
                <span>{formatDate(job.application_deadline)}</span>
              </div>
            </div>
          )}

          {/* Related Jobs */}
          {relatedJobs.length > 0 && (
            <div className="bg-white rounded-lg shadow-card p-6">
              <h3 className="font-semibold text-gray-900 mb-4">More jobs at {job.company.name}</h3>
              <div className="space-y-3">
                {relatedJobs.map((relatedJob) => (
                  <Link
                    key={relatedJob.id}
                    to={`/jobs/${relatedJob.id}`}
                    className="block p-3 border rounded-md hover:bg-gray-50 transition-colors"
                  >
                    <h4 className="font-medium text-gray-900 text-sm">{relatedJob.title}</h4>
                    <p className="text-xs text-gray-500 mt-1">{relatedJob.location}</p>
                    <p className="text-xs text-gray-400 mt-1">{getDaysAgo(relatedJob.created_at)}</p>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Application Modal */}
      {showApplicationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Apply for {job.title}</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Cover Letter (Optional)
                  </label>
                  <textarea
                    value={applicationData.cover_letter}
                    onChange={(e) => setApplicationData({ ...applicationData, cover_letter: e.target.value })}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    placeholder="Tell the employer why you're a great fit..."
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Portfolio URL (Optional)
                  </label>
                  <input
                    type="url"
                    value={applicationData.portfolio_url}
                    onChange={(e) => setApplicationData({ ...applicationData, portfolio_url: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
                    placeholder="https://..."
                  />
                </div>
              </div>
              
              <div className="flex space-x-3 mt-6">
                <button
                  onClick={() => setShowApplicationModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleApply}
                  disabled={applying}
                  className="flex-1 px-4 py-2 bg-linkedin-500 text-white rounded-md hover:bg-linkedin-600 disabled:opacity-50"
                >
                  {applying ? 'Applying...' : 'Submit Application'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobDetailPage; 