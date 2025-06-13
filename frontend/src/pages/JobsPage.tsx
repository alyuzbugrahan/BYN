import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { jobsAPI } from '../utils/api';
import { Job, PaginatedResponse } from '../types';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  BriefcaseIcon,
  ClockIcon,
  CurrencyDollarIcon,
  BookmarkIcon,
  FunnelIcon,
  PlusIcon,
} from '@heroicons/react/24/outline';
import { BookmarkIcon as BookmarkIconSolid } from '@heroicons/react/24/solid';

const JobsPage: React.FC = () => {
  const { user } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [experienceFilter, setExperienceFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [savedJobs, setSavedJobs] = useState<Set<number>>(new Set());

  useEffect(() => {
    fetchJobs();
  }, [currentPage, searchTerm, locationFilter, typeFilter, experienceFilter]);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const filters: any = {
        page: currentPage
      };
      
      if (searchTerm) filters.search = searchTerm;
      if (locationFilter) filters.location = locationFilter;
      if (typeFilter) filters.job_type = typeFilter;
      if (experienceFilter) filters.experience_level = experienceFilter;

      const response: PaginatedResponse<Job> = await jobsAPI.getJobs(filters);
      setJobs(response.results);
      setTotalPages(Math.ceil(response.count / 10));
    } catch (error) {
      console.error('Error fetching jobs:', error);
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveJob = async (jobId: number) => {
    try {
      if (savedJobs.has(jobId)) {
        await jobsAPI.unsaveJob(jobId);
        setSavedJobs(prev => {
          const newSet = new Set(prev);
          newSet.delete(jobId);
          return newSet;
        });
      } else {
        await jobsAPI.saveJob(jobId);
        setSavedJobs(prev => new Set(prev).add(jobId));
      }
    } catch (error) {
      console.error('Error toggling job save:', error);
    }
  };

  const formatSalaryRange = (job: Job) => {
    if (job.salary_min && job.salary_max) {
      return `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}`;
    }
    if (job.salary_min) {
      return `$${job.salary_min.toLocaleString()}+`;
    }
    return 'Salary not specified';
  };

  const getExperienceLevel = (level: string) => {
    const levels: { [key: string]: string } = {
      'entry': 'Entry Level',
      'associate': 'Associate',
      'mid': 'Mid-Senior Level',
      'director': 'Director',
      'executive': 'Executive'
    };
    return levels[level] || level;
  };


  const getJobType = (type: string) => {
    const types: { [key: string]: string } = {
      'full_time': 'Full-time',
      'part_time': 'Part-time',
      'contract': 'Contract',
      'internship': 'Internship',
      'temporary': 'Temporary',
      'volunteer': 'Volunteer'
    };
    return types[type] || type;
  };

  const getWorkplaceType = (type: string) => {
    const types: { [key: string]: string } = {
      'on_site': 'On-site',
      'remote': 'Remote',
      'hybrid': 'Hybrid'
    };
    return types[type] || type;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Jobs</h1>
            <p className="text-gray-600">Find your next career opportunity</p>
          </div>
          {user?.is_company_user && (
            <Link
              to="/jobs/create"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-linkedin-500 hover:bg-linkedin-600"
            >
              <PlusIcon className="w-5 h-5 mr-2" />
              Post a Job
            </Link>
          )}
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-card p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="lg:col-span-2">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search jobs, companies, or skills..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-linkedin-500 focus:border-linkedin-500"
              />
            </div>
          </div>
          
          <div>
            <select
              value={locationFilter}
              onChange={(e) => setLocationFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-linkedin-500 focus:border-linkedin-500"
            >
              <option value="">All Locations</option>
              <option value="San Francisco, CA">San Francisco, CA</option>
              <option value="New York, NY">New York, NY</option>
              <option value="Seattle, WA">Seattle, WA</option>
            </select>
          </div>

          <div>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-linkedin-500 focus:border-linkedin-500"
            >
              <option value="">All Types</option>
              <option value="full_time">Full-time</option>
              <option value="part_time">Part-time</option>
              <option value="contract">Contract</option>
              <option value="internship">Internship</option>
            </select>
          </div>

          <div>
            <select
              value={experienceFilter}
              onChange={(e) => setExperienceFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-linkedin-500 focus:border-linkedin-500"
            >
              <option value="">All Levels</option>
              <option value="entry">Entry Level</option>
              <option value="mid">Mid-Senior Level</option>
              <option value="director">Director</option>
              <option value="executive">Executive</option>
            </select>
          </div>
        </div>
      </div>

      {/* Job Listings */}
      {loading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="large" />
        </div>
      ) : jobs.length === 0 ? (
        <div className="bg-white rounded-lg shadow-card p-12 text-center">
          <BriefcaseIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
          <p className="text-gray-600">Try adjusting your search criteria or check back later for new opportunities.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {jobs.map((job) => (
            <div key={job.id} className="bg-white rounded-lg shadow-card p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    {job.company.logo && (
                      <img
                        src={job.company.logo}
                        alt={job.company.name}
                        className="w-12 h-12 rounded object-cover"
                      />
                    )}
                    <div>
                      <Link
                        to={`/jobs/${job.id}`}
                        className="text-xl font-semibold text-gray-900 hover:text-linkedin-600"
                      >
                        {job.title}
                      </Link>
                      <Link
                        to={`/companies/${job.company.id}`}
                        className="block text-linkedin-600 hover:text-linkedin-700 font-medium"
                      >
                        {job.company.name}
                      </Link>
                    </div>
                  </div>

                  <div className="flex items-center space-x-6 text-sm text-gray-600 mb-3">
                    <div className="flex items-center">
                      <MapPinIcon className="w-4 h-4 mr-1" />
                      {job.location}
                    </div>
                    <div className="flex items-center">
                      <BriefcaseIcon className="w-4 h-4 mr-1" />
                      {getWorkplaceType(job.workplace_type)}
                    </div>
                    <div className="flex items-center">
                      <ClockIcon className="w-4 h-4 mr-1" />
                      {getJobType(job.job_type)}
                    </div>
                    <div className="flex items-center">
                      <CurrencyDollarIcon className="w-4 h-4 mr-1" />
                      {formatSalaryRange(job)}
                    </div>
                  </div>

                  <p className="text-gray-700 mb-3 line-clamp-2">
                    {job.description}
                  </p>

                  <div className="flex items-center justify-between">
                    <div className="flex flex-wrap gap-2">
                      {job.skills_required.slice(0, 3).map((skill) => (
                        <span
                          key={skill.id}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-linkedin-100 text-linkedin-800"
                        >
                          {skill.name}
                        </span>
                      ))}
                      {job.skills_required.length > 3 && (
                        <span className="text-xs text-gray-500">
                          +{job.skills_required.length - 3} more
                        </span>
                      )}
                    </div>

                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => handleSaveJob(job.id)}
                        className="p-2 text-gray-400 hover:text-linkedin-600"
                      >
                        {savedJobs.has(job.id) ? (
                          <BookmarkIconSolid className="w-5 h-5 text-linkedin-600" />
                        ) : (
                          <BookmarkIcon className="w-5 h-5" />
                        )}
                      </button>
                      <Link
                        to={`/jobs/${job.id}`}
                        className="px-4 py-2 bg-linkedin-500 text-white rounded-md hover:bg-linkedin-600 transition-colors"
                      >
                        View Job
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center mt-8">
              <nav className="flex space-x-2">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const page = i + 1;
                  return (
                    <button
                      key={page}
                      onClick={() => setCurrentPage(page)}
                      className={`px-3 py-2 text-sm font-medium rounded-md ${
                        currentPage === page
                          ? 'bg-linkedin-500 text-white'
                          : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      {page}
                    </button>
                  );
                })}

                <button
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </nav>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default JobsPage; 