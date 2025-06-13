import React from 'react';
import ProtectedRoute from '../../components/auth/ProtectedRoute';
import Layout from '../../components/layout/Layout';
import DashboardContent from '../../components/pages/DashboardContent';

const DashboardPage: React.FC = () => {
  return (
    <ProtectedRoute>
      <Layout>
        <DashboardContent />
      </Layout>
    </ProtectedRoute>
  );
};

export default DashboardPage;
