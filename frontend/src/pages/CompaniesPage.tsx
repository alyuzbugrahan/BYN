import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { companiesAPI } from '../utils/api';
import { Company, PaginatedResponse } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  UsersIcon,
  GlobeAltIcon,
  PlusIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

const CompaniesPage: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [industryFilter, setIndustryFilter] = useState('');
  const [sizeFilter, setSizeFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [followedCompanies, setFollowedCompanies] = useState<Set<number>>(new Set());
  const [industries, setIndustries] = useState<string[]>([]);
  const [companySizes, setCompanySizes] = useState<string[]>([]);

  useEffect(() => {
    fetchFilterOptions();
  }, []);

  useEffect(() => {
    fetchCompanies();
  }, [currentPage, searchTerm, industryFilter, sizeFilter]);

  const fetchFilterOptions = async () => {
    try {
      const options = await companiesAPI.getFilterOptions();
      setIndustries(options.industries);
      setCompanySizes(options.company_sizes);
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
  };

  const fetchCompanies = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (industryFilter) params.append('industry', industryFilter);
      if (sizeFilter) params.append('company_size', sizeFilter);
      params.append('page', currentPage.toString());

      const response: PaginatedResponse<Company> = await companiesAPI.getCompanies(params.toString());
      setCompanies(response.results);
      setTotalPages(Math.ceil(response.count / 10));
    } catch (error) {
      console.error('Error fetching companies:', error);
      setCompanies([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFollowCompany = async (companyId: number) => {
    try {
      if (followedCompanies.has(companyId)) {
        await companiesAPI.unfollowCompany(companyId);
        setFollowedCompanies(prev => {
          const newSet = new Set(prev);
          newSet.delete(companyId);
          return newSet;
        });
      } else {
        await companiesAPI.followCompany(companyId);
        setFollowedCompanies(prev => new Set(prev).add(companyId));
      }
    } catch (error) {
      console.error('Error toggling company follow:', error);
    }
  };

  const getCompanySize = (size: string) => {
    const sizes: { [key: string]: string } = {
      '1-10': '1-10 employees',
      '11-50': '11-50 employees',
      '51-200': '51-200 employees',
      '100-500': '100-500 employees',
      '201-500': '201-500 employees',
      '501-1000': '501-1000 employees',
      '1001-5000': '1001-5000 employees',
      '5001-10000': '5001-10000 employees',
      '10000+': '10000+ employees'
    };
    return sizes[size] || `${size} employees`;
  };



  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Companies</h1>
        <p className="text-gray-600">Discover companies and connect with professionals</p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-card p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="lg:col-span-2">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search companies..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-linkedin-500 focus:border-linkedin-500"
              />
            </div>
          </div>
          
          <div>
            <select
              value={industryFilter}
              onChange={(e) => setIndustryFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-linkedin-500 focus:border-linkedin-500"
            >
              <option value="">All Industries</option>
              {industries.map(industry => (
                <option key={industry} value={industry}>{industry}</option>
              ))}
            </select>
          </div>

          <div>
            <select
              value={sizeFilter}
              onChange={(e) => setSizeFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-linkedin-500 focus:border-linkedin-500"
            >
              <option value="">All Sizes</option>
              {companySizes.map(size => (
                <option key={size} value={size}>{getCompanySize(size)}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Company Listings */}
      {loading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="large" />
        </div>
      ) : companies.length === 0 ? (
        <div className="bg-white rounded-lg shadow-card p-12 text-center">
          <UsersIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No companies found</h3>
          <p className="text-gray-600">Try adjusting your search criteria or check back later.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {companies.map((company) => (
            <div key={company.id} className="bg-white rounded-lg shadow-card overflow-hidden hover:shadow-lg transition-shadow">
              {/* Company Header */}
              <div className="relative h-32 bg-gradient-to-r from-linkedin-500 to-linkedin-600">
                {company.cover_image && (
                  <img
                    src={company.cover_image}
                    alt={`${company.name} cover`}
                    className="w-full h-full object-cover"
                  />
                )}
                <div className="absolute inset-0 bg-black bg-opacity-20"></div>
              </div>

              {/* Company Info */}
              <div className="p-6">
                <div className="flex items-start space-x-4 mb-4">
                  <div className="flex-shrink-0">
                    {company.logo ? (
                      <img
                        src={company.logo}
                        alt={company.name}
                        className="w-16 h-16 rounded-lg object-cover border-2 border-white shadow-md"
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-lg bg-gray-200 flex items-center justify-center border-2 border-white shadow-md">
                        <UsersIcon className="w-8 h-8 text-gray-400" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <Link
                        to={`/companies/${company.id}`}
                        className="text-lg font-semibold text-gray-900 hover:text-linkedin-600 truncate"
                      >
                        {company.name}
                      </Link>
                      {company.is_verified && (
                        <CheckCircleIcon className="w-5 h-5 text-blue-500" />
                      )}
                    </div>
                    {company.industry && (
                      <p className="text-sm text-gray-600">{company.industry.name}</p>
                    )}
                  </div>
                </div>

                <p className="text-gray-700 text-sm mb-4 line-clamp-3">
                  {company.description || 'No description available'}
                </p>

                <div className="space-y-2 mb-4 text-sm text-gray-600">
                  {company.headquarters && (
                    <div className="flex items-center">
                      <MapPinIcon className="w-4 h-4 mr-2" />
                      {company.headquarters}
                    </div>
                  )}
                  {company.company_size && (
                    <div className="flex items-center">
                      <UsersIcon className="w-4 h-4 mr-2" />
                      {getCompanySize(company.company_size)}
                    </div>
                  )}
                  {company.website && (
                    <div className="flex items-center">
                      <GlobeAltIcon className="w-4 h-4 mr-2" />
                      <a
                        href={company.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-linkedin-600 hover:text-linkedin-700 truncate"
                      >
                        {company.website.replace(/^https?:\/\//, '')}
                      </a>
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    {company.follower_count || 0} followers
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleFollowCompany(company.id)}
                      className={`px-3 py-1.5 text-sm font-medium rounded border transition-colors ${
                        followedCompanies.has(company.id)
                          ? 'bg-linkedin-50 text-linkedin-600 border-linkedin-200 hover:bg-linkedin-100'
                          : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      {followedCompanies.has(company.id) ? (
                        <div className="flex items-center">
                          <CheckCircleIcon className="w-4 h-4 mr-1" />
                          Following
                        </div>
                      ) : (
                        <div className="flex items-center">
                          <PlusIcon className="w-4 h-4 mr-1" />
                          Follow
                        </div>
                      )}
                    </button>
                    <Link
                      to={`/companies/${company.id}`}
                      className="px-3 py-1.5 text-sm font-medium text-white bg-linkedin-500 rounded hover:bg-linkedin-600 transition-colors"
                    >
                      View
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

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
  );
};

export default CompaniesPage; 