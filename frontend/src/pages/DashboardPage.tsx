import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function Dashboard() {
  const { user, logout, isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, loading, navigate]);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!isAuthenticated) {
    return null;
  }

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold text-gray-900">Clinical CDS</h1>
              </div>
            </div>
            <div className="flex items-center">
              <span className="text-sm text-gray-700 mr-4">
                {user?.first_name} {user?.last_name} ({user?.role})
              </span>
              <button
                onClick={handleLogout}
                className="text-sm text-red-600 hover:text-red-500"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center bg-white">
              <div className="text-center">
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                  Welcome to your Dashboard
                </h2>
                <p className="text-gray-600">
                  You are logged in as {user?.role}
                </p>
                <p className="text-sm text-gray-500 mt-4">
                  Dashboard functionality will be implemented in subsequent phases.
                </p>
              </div>
            </div>
            <div className="border-4 border-dashed border-blue-200 rounded-lg h-96 flex items-center justify-center bg-blue-50">
              <div className="text-center">
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                  AI Consultation Assistant
                </h2>
                <p className="text-gray-600 mb-4">
                  Get AI-powered symptom analysis and medical information
                </p>
                <a
                  href="/chat"
                  className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Start AI Chat
                </a>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}