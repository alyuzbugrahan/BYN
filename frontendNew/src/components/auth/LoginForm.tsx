'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../contexts/AuthContext';
import { LoginCredentials } from '../../types';
import LoadingSpinner from '../ui/LoadingSpinner';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import { testAPIConnection } from '../../utils/api';

const LoginForm: React.FC = () => {
  const router = useRouter();
  const { login, isLoading, error } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionTest, setConnectionTest] = useState<{result?: boolean; error?: string} | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginCredentials>();
  const handleTestConnection = async () => {
    setTestingConnection(true);
    setConnectionTest(null);
    
    try {
      const result = await testAPIConnection();
      setConnectionTest({ result: result.connected, error: result.error });
    } catch (error) {
      console.error('Connection test error:', error);
      setConnectionTest({ result: false, error: 'Connection test failed' });
    } finally {
      setTestingConnection(false);
    }
  };const onSubmit = async (data: LoginCredentials) => {
    try {
      console.log('📋 LoginForm: Form submitted', {
        email: data.email,
        timestamp: new Date().toISOString()
      });
      
      await login(data);
      console.log('🎯 LoginForm: Login successful, redirecting to dashboard');
      router.push('/dashboard');
    } catch (error) {
      // Error is handled in the auth context and displayed via state
      console.error('📋 LoginForm: Login error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-emerald-500 rounded-2xl flex items-center justify-center">
            <span className="text-white font-bold text-xl">BYN</span>
          </div>
        </div>
        <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
          Sign in to your account
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Stay updated on your professional world
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <div className="mt-1">
                <input
                  {...register('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Invalid email address',
                    },
                  })}
                  type="email"
                  autoComplete="email"
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
                  placeholder="Enter your email"
                />
                {errors.email && (
                  <p className="mt-2 text-sm text-red-600">{errors.email.message}</p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="mt-1 relative">
                <input
                  {...register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 6,
                      message: 'Password must be at least 6 characters',
                    },
                  })}
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  className="appearance-none block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
                  placeholder="Enter your password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
                {errors.password && (
                  <p className="mt-2 text-sm text-red-600">{errors.password.message}</p>
                )}
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? <LoadingSpinner size="small" color="white" /> : 'Sign in'}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">New to BYN?</span>
              </div>
            </div>

            <div className="mt-6">
              <Link
                href="/register"
                className="w-full flex justify-center py-2 px-4 border border-emerald-600 rounded-md shadow-sm text-sm font-medium text-emerald-600 bg-white hover:bg-emerald-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors"
              >
                Join now
              </Link>
            </div>
          </div>
        </div>        {/* Demo Credentials */}
        <div className="mt-4 bg-blue-50 border border-blue-200 rounded-md p-4">
          <h3 className="text-sm font-medium text-blue-800 mb-2">Demo Credentials:</h3>
          <div className="text-sm text-blue-700 space-y-1">
            <p><strong>Email:</strong> john.doe@example.com</p>
            <p><strong>Password:</strong> testpass123</p>
            <p className="text-xs mt-2 text-blue-600">
              You can also use jane.smith@example.com or mike.wilson@example.com with the same password.
            </p>
          </div>
        </div>        {/* API Debug Info */}
        {process.env.NEXT_PUBLIC_DEBUG_API === 'true' && (
          <div className="mt-4 bg-green-50 border border-green-200 rounded-md p-4">
            <h3 className="text-sm font-medium text-green-800 mb-2">API Configuration:</h3>
            <div className="text-sm text-green-700 space-y-1">
              <p><strong>API URL:</strong> {process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api'}</p>
              <p><strong>Debug Mode:</strong> Enabled</p>
              <p className="text-xs mt-2 text-green-600">
                Check the browser console for detailed API request logs.
              </p>
              
              <div className="mt-3">
                <button
                  type="button"
                  onClick={handleTestConnection}
                  disabled={testingConnection}
                  className="inline-flex items-center px-3 py-1.5 border border-green-300 text-xs font-medium rounded-md text-green-700 bg-white hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                >
                  {testingConnection ? (
                    <>
                      <LoadingSpinner size="small" />
                      <span className="ml-1">Testing...</span>
                    </>
                  ) : (
                    'Test API Connection'
                  )}
                </button>
                
                {connectionTest && (
                  <div className={`mt-2 text-xs ${connectionTest.result ? 'text-green-600' : 'text-red-600'}`}>
                    {connectionTest.result ? '✅ Connection successful' : `❌ Connection failed: ${connectionTest.error}`}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoginForm;
