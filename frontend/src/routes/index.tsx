import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import { LoginPage } from "../pages/auth/LoginPage";
import { RegisterPage } from "../pages/auth/RegisterPage";
import { ForgotPasswordPage } from "../pages/auth/ForgotPasswordPage";
import { HomePage } from "../pages/HomePage";
import { RoleDashboard } from "../pages/RoleDashboard";
import { AppShell } from "../layouts/AppShell";
import { AuthProvider, useAuth } from "../context/AuthContext";

import { AssessmentPage } from "../pages/patient/AssessmentPage";
import { ConsultationHistoryPage } from "../pages/patient/ConsultationHistoryPage";
import { ProfilePage } from "../pages/patient/ProfilePage";
import { AIAssistantPage } from "../pages/AIAssistantPage";

import { DoctorPatientsPage } from "../pages/doctor/DoctorPatientsPage";
import { DoctorConsultationsPage } from "../pages/doctor/DoctorConsultationsPage";
import { ConsultationDetailPage } from "../pages/doctor/ConsultationDetailPage";

import { PrescriptionsPage } from "../pages/pharmacist/PrescriptionsPage";
import { PrescriptionDetailPage } from "../pages/pharmacist/PrescriptionDetailPage";
import { InteractionCheckerPage } from "../pages/pharmacist/InteractionCheckerPage";

import { UsersPage } from "../pages/admin/UsersPage";
import { MedicationsPage } from "../pages/admin/MedicationsPage";
import { ConditionsPage } from "../pages/admin/ConditionsPage";
import { SourcesPage } from "../pages/admin/SourcesPage";
import { AuditLogsPage } from "../pages/admin/AuditLogsPage";
import { SystemConsultationsPage } from "../pages/admin/SystemConsultationsPage";
import { SystemSettingsPage } from "../pages/admin/SystemSettingsPage";

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="loading-wrap"><div className="spinner" /></div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

const RoleGate = ({ roles, children }: { roles: string[]; children: React.ReactNode }) => {
  const { user } = useAuth();
  if (!user || !roles.includes(user.role)) {
    return <Navigate to="/app" replace />;
  }
  return <>{children}</>;
};

const RootLayout = () => {
  return (
    <AuthProvider>
      <Outlet />
    </AuthProvider>
  );
};

const RootErrorBoundary = () => {
  return (
    <div className="auth-page">
      <div className="auth-card panel" style={{ textAlign: "center", padding: "32px 24px" }}>
        <h2 style={{ color: "#e11d48", marginBottom: 12 }}>Something went wrong</h2>
        <p style={{ color: "#64748b", marginBottom: 24 }}>An unexpected error occurred. Please try again or return to the home page.</p>
        <a href="/" className="btn btn-primary" style={{ display: "inline-block" }}>
          Return to Home
        </a>
      </div>
    </div>
  );
};

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    errorElement: <RootErrorBoundary />,
    children: [
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
        path: "/forgot-password",
        element: <ForgotPasswordPage />,
      },
      {
        path: "/app",
        element: (
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        ),
        children: [
          { index: true, element: <RoleDashboard /> },

          // Patient
          {
            path: "assessment",
            element: (
              <RoleGate roles={["PATIENT"]}>
                <AssessmentPage />
              </RoleGate>
            ),
          },
          {
            path: "history",
            element: (
              <RoleGate roles={["PATIENT"]}>
                <ConsultationHistoryPage />
              </RoleGate>
            ),
          },
          {
            path: "profile",
            element: (
              <RoleGate roles={["PATIENT"]}>
                <ProfilePage />
              </RoleGate>
            ),
          },

          // Doctor
          {
            path: "patients",
            element: (
              <RoleGate roles={["DOCTOR"]}>
                <DoctorPatientsPage />
              </RoleGate>
            ),
          },
          {
            path: "consultations",
            element: (
              <RoleGate roles={["DOCTOR"]}>
                <DoctorConsultationsPage />
              </RoleGate>
            ),
          },
          {
            path: "consultations/:id",
            element: (
              <RoleGate roles={["DOCTOR"]}>
                <ConsultationDetailPage />
              </RoleGate>
            ),
          },

          // Shared clinical AI assistant with report upload (all signed-in roles;
          // the page picks the patient or clinician endpoint per role)
          {
            path: "ai-assistant",
            element: (
              <RoleGate roles={["DOCTOR", "PHARMACIST", "ADMIN", "PATIENT"]}>
                <AIAssistantPage />
              </RoleGate>
            ),
          },

          // Pharmacist
          {
            path: "prescriptions",
            element: (
              <RoleGate roles={["PHARMACIST"]}>
                <PrescriptionsPage />
              </RoleGate>
            ),
          },
          {
            path: "prescriptions/:id",
            element: (
              <RoleGate roles={["PHARMACIST"]}>
                <PrescriptionDetailPage />
              </RoleGate>
            ),
          },
          {
            path: "interactions",
            element: (
              <RoleGate roles={["PHARMACIST"]}>
                <InteractionCheckerPage />
              </RoleGate>
            ),
          },

          // Admin
          {
            path: "users",
            element: (
              <RoleGate roles={["ADMIN"]}>
                <UsersPage />
              </RoleGate>
            ),
          },
          {
            path: "system-consultations",
            element: (
              <RoleGate roles={["ADMIN"]}>
                <SystemConsultationsPage />
              </RoleGate>
            ),
          },
          {
            path: "medications",
            element: (
              <RoleGate roles={["ADMIN"]}>
                <MedicationsPage />
              </RoleGate>
            ),
          },
          {
            path: "conditions",
            element: (
              <RoleGate roles={["ADMIN"]}>
                <ConditionsPage />
              </RoleGate>
            ),
          },
          {
            path: "sources",
            element: (
              <RoleGate roles={["ADMIN"]}>
                <SourcesPage />
              </RoleGate>
            ),
          },
          {
            path: "admin-settings",
            element: (
              <RoleGate roles={["ADMIN"]}>
                <SystemSettingsPage />
              </RoleGate>
            ),
          },
          {
            path: "audit",
            element: (
              <RoleGate roles={["ADMIN"]}>
                <AuditLogsPage />
              </RoleGate>
            ),
          },

          { path: "*", element: <Navigate to="/app" replace /> },
        ],
      },
      {
        path: "/dashboard",
        element: <Navigate to="/app" replace />,
      },
      {
        path: "/chat",
        element: <Navigate to="/app/assessment" replace />,
      },
      {
        path: "*",
        element: <Navigate to="/" replace />,
      },
    ],
  },
]);
