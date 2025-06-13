'use client';

import React, { createContext, useContext, useReducer, useEffect, ReactNode, useMemo } from 'react';
import { User, LoginCredentials, RegisterData, AuthTokens } from '../types';
import { authAPI, tokenManager } from '../utils/api';
import { toast } from 'react-toastify';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  refreshUser: () => Promise<void>;
}

type AuthAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_ERROR' }
  | { type: 'LOGOUT' };

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_USER':
      return { 
        ...state, 
        user: action.payload, 
        isAuthenticated: !!action.payload,
        error: null 
      };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    case 'LOGOUT':
      return { 
        user: null, 
        isAuthenticated: false, 
        isLoading: false, 
        error: null 
      };
    default:
      return state;
  }
};

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check if user is authenticated on app load
  useEffect(() => {
    const initializeAuth = async () => {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      if (tokenManager.isAuthenticated()) {
        try {
          const user = await authAPI.getProfile();
          dispatch({ type: 'SET_USER', payload: user });
        } catch (error) {
          console.error('Error fetching user profile:', error);
          tokenManager.clearTokens();
          dispatch({ type: 'LOGOUT' });
        }
      } else {
        dispatch({ type: 'LOGOUT' });
      }
      
      dispatch({ type: 'SET_LOADING', payload: false });
    };

    initializeAuth();
  }, []);
  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });

      console.log('🚀 AuthContext: Starting login process...');
      console.log('📧 Email:', credentials.email);
      console.log('🔗 API Base URL:', process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api');
      
      const tokens: AuthTokens = await authAPI.login(credentials);
      console.log('🎫 AuthContext: Tokens received, storing...');
      tokenManager.setTokens(tokens);

      console.log('👤 AuthContext: Fetching user profile...');
      const user = await authAPI.getProfile();
      console.log('✅ AuthContext: User profile loaded:', {
        id: user.id,
        email: user.email,
        is_company_user: user.is_company_user,
        first_name: user.first_name,
        last_name: user.last_name
      });
      
      dispatch({ type: 'SET_USER', payload: user });
      dispatch({ type: 'SET_LOADING', payload: false });

      toast.success('Login successful!');
      console.log('🎉 AuthContext: Login completed successfully');
    } catch (error: any) {      console.error('💥 AuthContext: Login failed:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          baseURL: error.config?.baseURL
        }
      });
      
      const errorMessage = error.response?.data?.detail ?? 'Login failed. Please try again.';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      toast.error(errorMessage);
      throw error;
    }
  };

  const register = async (userData: RegisterData): Promise<void> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'CLEAR_ERROR' });      await authAPI.register(userData);
      
      // Auto-login after registration
      await login({
        email: userData.email,
        password: userData.password,
      });

      toast.success('Registration successful! Welcome to BYN!');
    } catch (error: any) {      const errorMessage = error.response?.data?.detail ?? 
                          error.response?.data?.message ??
                          'Registration failed. Please try again.';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      toast.error(errorMessage);
      throw error;
    }
  };

  const logout = (): void => {
    try {
      authAPI.logout().catch(console.error); // Don't wait for this
      tokenManager.clearTokens();
      dispatch({ type: 'LOGOUT' });
      toast.success('Logged out successfully');
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear local state and tokens
      tokenManager.clearTokens();
      dispatch({ type: 'LOGOUT' });
    }
  };

  const clearError = (): void => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const refreshUser = async (): Promise<void> => {
    try {
      if (tokenManager.isAuthenticated()) {
        const user = await authAPI.getProfile();
        dispatch({ type: 'SET_USER', payload: user });
      }
    } catch (error) {
      console.error('Error refreshing user:', error);
    }
  };
  const value: AuthContextType = useMemo(() => ({
    ...state,
    login,
    register,
    logout,
    clearError,
    refreshUser,
  }), [state, login, register, logout, clearError, refreshUser]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
