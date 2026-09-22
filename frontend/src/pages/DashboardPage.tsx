import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function Dashboard() {
  const { user, logout, isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate("/login");
    } else if (!loading && isAuthenticated) {
      // Redirect to chat interface as the main interface
      navigate("/chat");
    }
  }, [isAuthenticated, loading, navigate]);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!isAuthenticated) {
    return null;
  }

  // Show loading state while redirecting
  return <div className="min-h-screen flex items-center justify-center">Redirecting to AI Chat...</div>;
}