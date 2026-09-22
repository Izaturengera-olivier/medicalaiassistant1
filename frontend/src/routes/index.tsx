import { createBrowserRouter, Navigate } from "react-router-dom";
import { LoginPage } from "../pages/auth/LoginPage";
import { RegisterPage } from "../pages/auth/RegisterPage";
import { HomePage } from "../pages/HomePage";
import { Dashboard } from "../pages/DashboardPage";
import { ChatInterface } from "../components/ChatInterface";
import { AuthProvider, useAuth } from "../context/AuthContext";

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

export const router = createBrowserRouter([
  {
    path: "/",
    element: <HomePage />,
  },
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/register",
    element: <RegisterPage />,
  },
  {
    path: "/chat",
    element: (
      <AuthProvider>
        <ProtectedRoute>
          <ChatInterface />
        </ProtectedRoute>
      </AuthProvider>
    ),
  },
  {
    path: "/dashboard",
    element: (
      <AuthProvider>
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      </AuthProvider>
    ),
  },
]);