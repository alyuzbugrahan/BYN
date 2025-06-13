import React from 'react';
import ProtectedRoute from '../../components/auth/ProtectedRoute';
import Layout from '../../components/layout/Layout';
import JobsContent from '../../components/pages/JobsContent';

const JobsPage: React.FC = () => {
  return (
    <ProtectedRoute>
      <Layout>
        <JobsContent />
      </Layout>
    </ProtectedRoute>
  );
};

export default JobsPage;
