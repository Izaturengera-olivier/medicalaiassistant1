import { createBrowserRouter, Navigate } from "react-router-dom";
import { LoginPage } from "../pages/auth/LoginPage";
import { RegisterPage } from "../pages/auth/RegisterPage";
import { HomePage } from "../pages/HomePage";
import { Dashboard } from "../pages/DashboardPage";
import { ChatInterface } from "../components/ChatInterface";
import { AuthProvider } from "../context/AuthContext";

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
    path: "/dashboard",
    element: (
      <AuthProvider>
        <Dashboard />
      </AuthProvider>
    ),
  },
  {
    path: "/chat",
    element: (
      <AuthProvider>
        <ChatInterface />
      </AuthProvider>
    ),
  },
]);