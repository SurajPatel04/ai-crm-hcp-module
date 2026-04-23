import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useSelector } from 'react-redux';

/**
 * PublicRoute — only accessible when NOT authenticated.
 * Authenticated users are redirected to /log-interaction.
 * Used for /login and /signup so logged-in users can't go back to them.
 */
const PublicRoute = () => {
  const { isAuthenticated } = useSelector((state) => state.auth);

  if (isAuthenticated) {
    return <Navigate to="/log-interaction" replace />;
  }

  return <Outlet />;
};

export default PublicRoute;
