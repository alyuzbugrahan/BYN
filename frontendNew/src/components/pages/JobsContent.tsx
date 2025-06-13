'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { jobsAPI } from '../../utils/api';
import { Job, JobFilters, PaginatedResponse } from '../../types';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../ui/LoadingSpinner';
import { toast } from 'react-toastify';
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  BriefcaseIcon,
  BuildingOfficeIcon,
  ClockIcon,
  BookmarkIcon,
} from '@heroicons/react/24/outline';
import { BookmarkIcon as BookmarkIconSolid } from '@heroicons/react/24/solid';
import { format } from 'date-fns';

const JobsContent: React.FC = () => {
  const { user } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [location, setLocation] = useState('');
  const [jobType, setJobType] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('');
  const [savedJobs, setSavedJobs] = useState<Set<number>>(new Set());

  const fetchJobs = async (filters: JobFilters = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response: PaginatedResponse<Job> = await jobsAPI.getJobs(filters);
      setJobs(response.results);
    } catch (error) {
      console.error('Error fetching jobs:', error);
      setError('Failed to load jobs');
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const filters: JobFilters = {};
    if (searchQuery) filters.search = searchQuery;
    if (location) filters.location = location;
    if (jobType) filters.job_type = jobType;
    if (experienceLevel) filters.experience_level = experienceLevel;
    
    fetchJobs(filters);
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
        toast.success('Job removed from saved');
      } else {
        await jobsAPI.saveJob(jobId);
        setSavedJobs(prev => new Set(prev).add(jobId));
        toast.success('Job saved successfully');
      }
    } catch (error) {
      console.error('Error saving job:', error);
      toast.error('Failed to save job');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Find Jobs</h1>
            <p className="text-gray-600">Discover your next career opportunity</p>
          </div>
          {user?.is_company_user && (
            <Link
              href="/jobs/create"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-500 hover:bg-primary-600"
            >
              <BriefcaseIcon className="w-5 h-5 mr-2" />
              Post a Job
            </Link>
          )}
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
                Job Title or Keywords
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon className="h-4 w-4 text-gray-400" />
                </div>
                <input
                  type="text"
                  id="search"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
                  placeholder="e.g. Software Engineer, Marketing Manager"
                />
              </div>
            </div>

            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
                Location
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MapPinIcon className="h-4 w-4 text-gray-400" />
                </div>
                <input
                  type="text"
                  id="location"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
                  placeholder="e.g. New York, Remote"
                />
              </div>
            </div>

            <div>
              <label htmlFor="jobType" className="block text-sm font-medium text-gray-700 mb-2">
                Job Type
              </label>
              <select
                id="jobType"
                value={jobType}
                onChange={(e) => setJobType(e.target.value)}
                className="block w-full pl-3 pr-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
              >
                <option value="">All Types</option>
                <option value="full_time">Full Time</option>
                <option value="part_time">Part Time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
                <option value="freelance">Freelance</option>
              </select>
            </div>
          </div>

          <div className="mt-4 flex justify-between items-center">
            <select
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              className="block pl-3 pr-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
            >
              <option value="">All Experience Levels</option>
              <option value="intern">Internship</option>
              <option value="entry">Entry Level</option>
              <option value="associate">Associate</option>
              <option value="mid">Mid Level</option>
              <option value="senior">Senior Level</option>
              <option value="executive">Executive</option>
            </select>

            <button
              type="submit"
              className="ml-4 inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors"
            >
              Search Jobs
            </button>
          </div>
        </form>        {/* Results */}
        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="large" />
          </div>
        ) : (
          (() => {
            if (error) {
              return (
                <div className="text-center py-12">
                  <div className="text-red-600 text-lg font-medium mb-2">Failed to load jobs</div>
                  <p className="text-gray-600 mb-4">{error}</p>
                  <button
                    onClick={() => fetchJobs()}
                    className="px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors"
                  >
                    Try Again
                  </button>
                </div>
              );
            } else {
              return (
                <div className="space-y-6">
                  <div className="flex justify-between items-center">
                    <p className="text-gray-600">
                      {jobs.length} job{jobs.length !== 1 ? 's' : ''} found
                    </p>
                  </div>

            {jobs.length > 0 ? (
              <div className="space-y-4">
                {jobs.map((job) => (
                  <div key={job.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 hover:text-emerald-600">
                              <Link href={`/jobs/${job.id}`}>
                                {job.title}
                              </Link>
                            </h3>
                            <div className="flex items-center mt-2 space-x-4 text-sm text-gray-600">
                              <div className="flex items-center">
                                <BuildingOfficeIcon className="h-4 w-4 mr-1" />
                                {job.company.name}
                              </div>
                              <div className="flex items-center">
                                <MapPinIcon className="h-4 w-4 mr-1" />
                                {job.location}
                              </div>
                              <div className="flex items-center">
                                <ClockIcon className="h-4 w-4 mr-1" />
                                {format(new Date(job.posted_date), 'MMM dd, yyyy')}
                              </div>
                            </div>
                          </div>
                            <button
                            onClick={() => handleSaveJob(job.id)}
                            className={`ml-4 p-2 rounded-md transition-colors ${
                              savedJobs.has(job.id)
                                ? 'text-emerald-600 bg-emerald-50'
                                : 'text-gray-400 hover:text-emerald-600 hover:bg-gray-50'
                            }`}
                          >
                            {savedJobs.has(job.id) ? (
                              <BookmarkIconSolid className="h-5 w-5" />
                            ) : (
                              <BookmarkIcon className="h-5 w-5" />
                            )}
                          </button>
                        </div>

                        <p className="mt-3 text-gray-700 line-clamp-2">
                          {job.description}
                        </p>

                        <div className="mt-4 flex items-center justify-between">
                          <div className="flex space-x-2">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                              {job.job_type.replace('_', ' ')}
                            </span>
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {job.employment_type.replace('_', ' ')}
                            </span>
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                              {job.experience_level}
                            </span>
                          </div>

                          <div className="flex space-x-3">
                            <Link
                              href={`/jobs/${job.id}`}
                              className="inline-flex items-center px-4 py-2 border border-emerald-600 text-sm font-medium rounded-md text-emerald-600 bg-white hover:bg-emerald-50 transition-colors"
                            >
                              View Details
                            </Link>
                            {!job.user_has_applied && (
                              <Link
                                href={`/jobs/${job.id}/apply`}
                                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-emerald-600 hover:bg-emerald-700 transition-colors"
                              >
                                <BriefcaseIcon className="h-4 w-4 mr-2" />
                                Apply Now
                              </Link>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <BriefcaseIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>                <p className="text-gray-600">Try adjusting your search criteria</p>
              </div>
            )}
                </div>
              );
            }
          })()
        )}
      </div>
    </div>
  );
};

export default JobsContent;
