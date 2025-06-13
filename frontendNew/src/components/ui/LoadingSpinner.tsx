import React from 'react';
import clsx from 'clsx';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'white' | 'gray';
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'medium', 
  color = 'primary',
  className 
}) => {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-6 w-6',
    large: 'h-8 w-8',
  };

  const colorClasses = {
    primary: 'text-emerald-600',
    white: 'text-white',
    gray: 'text-gray-600',
  };
  return (
    <div className={clsx('flex items-center justify-center', className)}>
      <div
        className={clsx(
          'animate-spin rounded-full border-2 border-solid border-current border-r-transparent',
          sizeClasses[size],
          colorClasses[color]
        )}
        aria-label="Loading"
      >
        <span className="sr-only">Loading...</span>
      </div>
    </div>
  );
};

export const CommentSkeleton: React.FC = () => {
  return (
    <div className="flex space-x-3 animate-pulse">
      <div className="flex-shrink-0">
        <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
      </div>
      <div className="flex-1 space-y-2">
        <div className="bg-gray-200 rounded-lg p-3 space-y-2">
          <div className="h-3 bg-gray-300 rounded w-1/4"></div>
          <div className="space-y-1">
            <div className="h-3 bg-gray-300 rounded w-full"></div>
            <div className="h-3 bg-gray-300 rounded w-3/4"></div>
          </div>
        </div>
        <div className="flex space-x-4">
          <div className="h-2 bg-gray-300 rounded w-16"></div>
          <div className="h-2 bg-gray-300 rounded w-8"></div>
          <div className="h-2 bg-gray-300 rounded w-12"></div>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
