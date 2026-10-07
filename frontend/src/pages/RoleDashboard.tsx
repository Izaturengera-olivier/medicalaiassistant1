import { useAuth } from "../context/AuthContext";
import { PatientDashboard } from "./patient/PatientDashboard";
import { DoctorDashboard } from "./doctor/DoctorDashboard";
import { PharmacistDashboard } from "./pharmacist/PharmacistDashboard";
import { AdminDashboard } from "./admin/AdminDashboard";

export function RoleDashboard() {
  const { user } = useAuth();
  switch (user?.role) {
    case "DOCTOR":
      return <DoctorDashboard />;
    case "PHARMACIST":
      return <PharmacistDashboard />;
    case "ADMIN":
      return <AdminDashboard />;
    case "PATIENT":
    default:
      return <PatientDashboard />;
  }
}
