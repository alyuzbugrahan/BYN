import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { jobsAPI, companiesAPI } from '../utils/api';
import { Job, Company, JobApplication } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  BriefcaseIcon,
  PlusIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  UserGroupIcon,
  ChartBarIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';
import ApiDebugger from '../components/ApiDebugger';

const CompanyDashboard: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [stats, setStats] = useState({
    total_jobs: 0,
    active_jobs: 0,
    total_applications: 0,
    new_applications: 0,
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        console.log('=== Company Dashboard Debug ===');
        console.log('Fetching companies for user:', user?.email);
        console.log('User is_company_user:', user?.is_company_user);
        console.log('User ID:', user?.id);
        console.log('Access token exists:', !!localStorage.getItem('accessToken'));
        
        const companiesData = await companiesAPI.getMyCompanies();
        console.log('getMyCompanies response:', companiesData);
        console.log('Companies data type:', typeof companiesData);
        console.log('Is array:', Array.isArray(companiesData));
        
        setCompanies(Array.isArray(companiesData) ? companiesData : []);
        
        if (Array.isArray(companiesData) && companiesData.length > 0) {
          console.log('Setting selected company:', companiesData[0]);
          setSelectedCompany(companiesData[0]);
        } else {
          console.log('No companies found or invalid data format');
        }
      } catch (error: any) {
        console.error('Error fetching companies:', error);
        console.error('Error details:', error.response?.data);
        console.error('Error status:', error.response?.status);
        toast.error('Failed to load companies');
        setCompanies([]);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchData();
    }
  }, [user]);

  useEffect(() => {
    if (selectedCompany) {
      fetchCompanyJobs();
    }
  }, [selectedCompany]);

  const fetchCompanyJobs = async () => {
    if (!selectedCompany) return;
    
    try {
      console.log('=== Jobs Debug ===');
      console.log('Fetching jobs for company:', selectedCompany.name);
      console.log('Selected company ID:', selectedCompany.id);
      
      const jobsData = await jobsAPI.getMyJobs();
      console.log('getMyJobs response:', jobsData);
      console.log('Jobs data type:', typeof jobsData);
      console.log('Jobs has results:', 'results' in jobsData);
      console.log('Jobs is array:', Array.isArray(jobsData));
      
      if (jobsData.results) {
        console.log('Total jobs in response:', jobsData.results.length);
        jobsData.results.forEach((job, index) => {
          console.log(`Job ${index + 1}: ${job.title} at company ID ${job.company.id} (${job.company.name})`);
        });
      }
      
      // The response should now include all jobs the user can manage (including company admin jobs)
      const companyJobs = jobsData.results ? 
        jobsData.results.filter(job => job.company.id === selectedCompany.id) :
        (Array.isArray(jobsData) ? jobsData.filter(job => job.company.id === selectedCompany.id) : []);
      
      console.log('Filtered company jobs:', companyJobs.length);
      console.log('Company jobs:', companyJobs);
      setJobs(companyJobs);
      
      // Calculate stats
      const activeJobs = companyJobs.filter(job => job.is_active).length;
      const totalApplications = companyJobs.reduce((total, job) => total + job.application_count, 0);
      
      const calculatedStats = {
        total_jobs: companyJobs.length,
        active_jobs: activeJobs,
        total_applications: totalApplications,
        new_applications: 0, // This would need a separate API call for new applications
      };
      
      console.log('Calculated stats:', calculatedStats);
      setStats(calculatedStats);
    } catch (error: any) {
      console.error('Error fetching jobs:', error);
      console.error('Error details:', error.response?.data);
      console.error('Error status:', error.response?.status);
      toast.error('Failed to load jobs');
      // Set empty arrays as fallback
      setJobs([]);
      setStats({
        total_jobs: 0,
        active_jobs: 0,
        total_applications: 0,
        new_applications: 0,
      });
    }
  };

  const handleDeleteJob = async (jobId: number) => {
    if (!window.confirm('Are you sure you want to delete this job?')) {
      return;
    }

    try {
      await jobsAPI.deleteJob(jobId);
      toast.success('Job deleted successfully');
      fetchCompanyJobs(); // Refresh the list
    } catch (error: any) {
      console.error('Error deleting job:', error);
      toast.error('Failed to delete job');
    }
  };

  const toggleJobStatus = async (jobId: number, isActive: boolean) => {
    try {
      await jobsAPI.updateJob(jobId, { is_active: !isActive });
      toast.success(`Job ${!isActive ? 'activated' : 'deactivated'} successfully`);
      fetchCompanyJobs(); // Refresh the list
    } catch (error: any) {
      console.error('Error updating job status:', error);
      toast.error('Failed to update job status');
    }
  };

  const formatSalaryRange = (job: Job) => {
    if (job.salary_min && job.salary_max) {
      return `${job.salary_currency} ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()} ${job.salary_type}`;
    } else if (job.salary_min) {
      return `${job.salary_currency} ${job.salary_min.toLocaleString()}+ ${job.salary_type}`;
    }
    return 'Salary not specified';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (companies.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <BuildingOfficeIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Companies Found</h2>
          <p className="text-gray-600 mb-6">
            You need to be an admin of a company to access this dashboard.
          </p>
          <Link
            to="/companies"
            className="px-6 py-3 bg-linkedin-500 text-white rounded-md hover:bg-linkedin-600"
          >
            Browse Companies
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <ApiDebugger />
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Company Dashboard</h1>
              <p className="mt-2 text-gray-600">Manage your job postings and applications</p>
            </div>
            <Link
              to="/jobs/create"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-linkedin-500 hover:bg-linkedin-600"
            >
              <PlusIcon className="w-5 h-5 mr-2" />
              Post New Job
            </Link>
          </div>
        </div>

        {/* Company Selector */}
        {companies.length > 1 && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Company
            </label>
            <select
              value={selectedCompany?.id || ''}
              onChange={(e) => {
                const company = companies.find(c => c.id === parseInt(e.target.value));
                setSelectedCompany(company || null);
              }}
              className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-linkedin-500"
            >
              {companies.map((company) => (
                <option key={company.id} value={company.id}>
                  {company.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {selectedCompany && (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow-card p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <BriefcaseIcon className="h-8 w-8 text-blue-500" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Total Jobs</dt>
                      <dd className="text-2xl font-bold text-gray-900">{stats.total_jobs}</dd>
                    </dl>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-card p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <CheckCircleIcon className="h-8 w-8 text-green-500" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Active Jobs</dt>
                      <dd className="text-2xl font-bold text-gray-900">{stats.active_jobs}</dd>
                    </dl>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-card p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <UserGroupIcon className="h-8 w-8 text-purple-500" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Total Applications</dt>
                      <dd className="text-2xl font-bold text-gray-900">{stats.total_applications}</dd>
                    </dl>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-card p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-8 w-8 text-yellow-500" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">New Applications</dt>
                      <dd className="text-2xl font-bold text-gray-900">{stats.new_applications}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* Jobs List */}
            <div className="bg-white shadow-card rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Job Postings</h2>
              </div>

              {jobs.length === 0 ? (
                <div className="text-center py-12">
                  <BriefcaseIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs posted yet</h3>
                  <p className="text-gray-600">Get started by posting your first job using the "Post New Job" button above</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {jobs.map((job) => (
                    <div key={job.id} className="p-6 hover:bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                job.is_active
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-gray-100 text-gray-800'
                              }`}
                            >
                              {job.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </div>

                          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-3">
                            <div className="flex items-center">
                              <MapPinIcon className="w-4 h-4 mr-1" />
                              {job.location}
                            </div>
                            <div className="flex items-center">
                              <BriefcaseIcon className="w-4 h-4 mr-1" />
                              {job.job_type.replace('_', ' ')}
                            </div>
                            <div className="flex items-center">
                              <CurrencyDollarIcon className="w-4 h-4 mr-1" />
                              {formatSalaryRange(job)}
                            </div>
                            <div className="flex items-center">
                              <CalendarIcon className="w-4 h-4 mr-1" />
                              Posted {format(new Date(job.created_at), 'MMM d, yyyy')}
                            </div>
                          </div>

                          <div className="flex items-center space-x-6 text-sm text-gray-600">
                            <span className="flex items-center">
                              <EyeIcon className="w-4 h-4 mr-1" />
                              {job.view_count} views
                            </span>
                            <span className="flex items-center">
                              <UserGroupIcon className="w-4 h-4 mr-1" />
                              {job.application_count} applications
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center space-x-2 ml-4">
                          <Link
                            to={`/jobs/${job.id}`}
                            className="p-2 text-gray-400 hover:text-gray-600"
                            title="View Job"
                          >
                            <EyeIcon className="w-5 h-5" />
                          </Link>

                          <Link
                            to={`/jobs/${job.id}/edit`}
                            className="p-2 text-gray-400 hover:text-linkedin-600"
                            title="Edit Job"
                          >
                            <PencilIcon className="w-5 h-5" />
                          </Link>

                          <button
                            onClick={() => toggleJobStatus(job.id, job.is_active)}
                            className="p-2 text-gray-400 hover:text-yellow-600"
                            title={job.is_active ? 'Deactivate Job' : 'Activate Job'}
                          >
                            {job.is_active ? (
                              <XCircleIcon className="w-5 h-5" />
                            ) : (
                              <CheckCircleIcon className="w-5 h-5" />
                            )}
                          </button>

                          <button
                            onClick={() => handleDeleteJob(job.id)}
                            className="p-2 text-gray-400 hover:text-red-600"
                            title="Delete Job"
                          >
                            <TrashIcon className="w-5 h-5" />
                          </button>
                        </div>
                      </div>

                      {job.application_deadline && (
                        <div className="mt-3 text-sm text-gray-600">
                          Application deadline: {format(new Date(job.application_deadline), 'MMM d, yyyy, h:mm a')}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default CompanyDashboard; 