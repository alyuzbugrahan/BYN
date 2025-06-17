import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { useAuth } from "../contexts/AuthContext";
import { LoginCredentials } from "../types";
import LoadingSpinner from "../components/LoadingSpinner";
import { EyeIcon, EyeSlashIcon } from "@heroicons/react/24/outline";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginCredentials>();

  const onSubmit = async (data: LoginCredentials) => {
    console.log("🚀 Login form submitted:", data);
    try {
      console.log("📞 Calling login function...");
      await login(data);
      console.log("✅ Login successful, navigating to dashboard...");
      // Small delay to ensure auth context is fully updated
      setTimeout(() => {
        navigate("/dashboard");
      }, 100);
    } catch (error) {
      console.error("❌ Login error in component:", error);
      const errorMessage =
        (error as any)?.response?.data?.detail ||
        (error as any)?.message ||
        "Login failed. Please try again.";
      toast.error(errorMessage, {
        position: "top-right",
        autoClose: 5000,
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <ToastContainer />
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <svg
            width="64"
            height="64"
            viewBox="0 0 32 32"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="w-16 h-16"
          >
            <rect width="32" height="32" rx="8" fill="#22c55e" />
            <text
              x="50%"
              y="55%"
              textAnchor="middle"
              fill="white"
              fontSize="16"
              fontWeight="bold"
              fontFamily="Inter, sans-serif"
              dy=".3em"
            >
              BYN
            </text>
          </svg>
        </div>
        <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
          Sign in to your account
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Stay updated on your professional world
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-card sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700"
              >
                Email address
              </label>
              <div className="mt-1">
                <input
                  {...register("email", {
                    required: "Email is required",
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: "Invalid email address",
                    },
                  })}
                  type="email"
                  autoComplete="email"
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-byn-500 focus:border-byn-500 sm:text-sm"
                  placeholder="Enter your email"
                />
                {errors.email && (
                  <p className="mt-2 text-sm text-red-600">
                    {errors.email.message}
                  </p>
                )}
              </div>
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700"
              >
                Password
              </label>
              <div className="mt-1 relative">
                <input
                  {...register("password", {
                    required: "Password is required",
                    minLength: {
                      value: 6,
                      message: "Password must be at least 6 characters",
                    },
                  })}
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  className="appearance-none block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-byn-500 focus:border-byn-500 sm:text-sm"
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
                  <p className="mt-2 text-sm text-red-600">
                    {errors.password.message}
                  </p>
                )}
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-byn-500 hover:bg-byn-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-byn-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? <LoadingSpinner size="small" /> : "Sign in"}
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
                to="/register"
                className="w-full flex justify-center py-2 px-4 border border-byn-500 rounded-md shadow-sm text-sm font-medium text-byn-500 bg-white hover:bg-byn-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-byn-500"
              >
                Join now
              </Link>
            </div>
          </div>
        </div>

        {/* Demo Credentials */}
        <div className="mt-4 bg-blue-50 border border-blue-200 rounded-md p-4">
          <h3 className="text-sm font-medium text-blue-800 mb-2">Demo Credentials:</h3>
          <div className="text-sm text-blue-700 space-y-1">
            <p><strong>Working User:</strong> test@example.com / Test1234!</p>
            <p className="text-xs mt-2 text-blue-600">
              <strong>Note:</strong> Sample data (companies, jobs) not loaded on remote server yet.<br/>
              Backend script 'create_sample_data.py' needs to be run to populate demo content.
            </p>
          </div>
        </div>

        {/* Debug Section */}
        <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <h3 className="text-sm font-medium text-yellow-800 mb-2">🔧 Debug Tools:</h3>
          <div className="space-y-2">
            <button
              onClick={async () => {
                console.log('🔍 Testing API connection...');
                try {
                  const apiUrl = process.env.REACT_APP_API_BASE_URL || 'byn-build-your-network-platform.railway.internal';
                  const response = await fetch(`${apiUrl}/api/auth/login/`, {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                      email: 'test@example.com',
                      password: 'Test1234!'
                    })
                  });
                  
                  console.log('📊 Response status:', response.status);
                  console.log('📊 Response headers:', Object.fromEntries(response.headers.entries()));
                  
                  if (response.ok) {
                    const data = await response.json();
                    console.log('✅ API Response:', data);
                    alert('API Test SUCCESS! Check console for details.');
                  } else {
                    const errorData = await response.text();
                    console.log('❌ API Error:', errorData);
                    alert(`API Test FAILED! Status: ${response.status}. Check console.`);
                  }
                } catch (error) {
                  console.error('🔥 Network Error:', error);
                  alert('Network Error! Check console.');
                }
              }}
              className="w-full text-xs px-3 py-2 bg-yellow-200 text-yellow-800 rounded hover:bg-yellow-300"
            >
              Test API Direct (Raw Fetch)
            </button>
            
            <button
              onClick={() => {
                const apiUrl = process.env.REACT_APP_API_BASE_URL || 'byn-build-your-network-platform.railway.internal';
                console.log('📍 Current API Base URL:', `${apiUrl}/api`);
                console.log('🔑 Stored Access Token:', localStorage.getItem('accessToken'));
                console.log('🔄 Stored Refresh Token:', localStorage.getItem('refreshToken'));
                console.log('🌐 Current Location:', window.location.href);
                alert('Check console for debug info!');
              }}
              className="w-full text-xs px-3 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
            >
              Show Debug Info
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
