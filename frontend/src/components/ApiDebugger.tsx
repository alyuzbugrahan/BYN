import React, { useState } from 'react';
import { companiesAPI, jobsAPI, authAPI } from '../utils/api';

const ApiDebugger: React.FC = () => {
  const [results, setResults] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const addResult = (message: string) => {
    setResults(prev => prev + message + '\n');
  };

  const testAPIs = async () => {
    setLoading(true);
    setResults('=== API DEBUG TEST ===\n');

    // Test authentication status
    addResult(`Token exists: ${!!localStorage.getItem('accessToken')}`);
    addResult(`Token: ${localStorage.getItem('accessToken')?.substring(0, 50)}...`);

    try {
      // Test 1: Profile API (should work if authenticated)
      addResult('\n1. Testing auth/profile...');
      const profile = await authAPI.getProfile();
      addResult(`✅ Profile: ${profile.email} (is_company_user: ${profile.is_company_user})`);

      // Test 2: My Companies API
      addResult('\n2. Testing companies/my-companies...');
      const companies = await companiesAPI.getMyCompanies();
      addResult(`✅ Companies count: ${companies.length}`);
      companies.forEach((company: any) => {
        addResult(`   - ${company.name} (ID: ${company.id})`);
      });

      // Test 3: My Jobs API
      addResult('\n3. Testing jobs/my-posts...');
      const jobs = await jobsAPI.getMyJobs();
      addResult(`✅ Jobs response type: ${typeof jobs}`);
      addResult(`✅ Jobs has results: ${'results' in jobs}`);
      if ('results' in jobs && jobs.results) {
        addResult(`✅ Jobs count: ${jobs.results.length}`);
        jobs.results.forEach((job: any) => {
          addResult(`   - ${job.title} at ${job.company.name} (Company ID: ${job.company.id})`);
        });
      } else if (Array.isArray(jobs)) {
        addResult(`✅ Jobs count (array): ${jobs.length}`);
        jobs.forEach((job: any) => {
          addResult(`   - ${job.title} at ${job.company.name}`);
        });
      }

    } catch (error: any) {
      addResult(`❌ Error: ${error.message}`);
      addResult(`❌ Status: ${error.response?.status}`);
      addResult(`❌ Data: ${JSON.stringify(error.response?.data)}`);
    }

    addResult('\n=== DEBUG COMPLETE ===');
    setLoading(false);
  };

  return (
    <div className="fixed top-4 right-4 bg-white border rounded-lg shadow-lg p-4 w-96 max-h-96 overflow-y-auto z-50">
      <h3 className="font-bold mb-2">API Debugger</h3>
      <button
        onClick={testAPIs}
        disabled={loading}
        className="bg-blue-500 text-white px-4 py-2 rounded mb-4 disabled:opacity-50"
      >
        {loading ? 'Testing...' : 'Test APIs'}
      </button>
      
      <pre className="text-xs bg-gray-100 p-2 rounded whitespace-pre-wrap">
        {results || 'Click "Test APIs" to run diagnostics'}
      </pre>
    </div>
  );
};

export default ApiDebugger; 