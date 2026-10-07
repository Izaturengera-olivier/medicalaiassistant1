import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api";

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refresh_token");
        const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem("access_token", access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email: string, password: string) =>
    api.post("/auth/login/", { email, password }),
  register: (data: {
    email: string;
    first_name: string;
    last_name: string;
    role: string;
    password: string;
    password_confirm: string;
  }) => api.post("/auth/register/", data),
  refreshToken: (refresh: string) =>
    api.post("/auth/token/refresh/", { refresh }),
  forgotPassword: (email: string) =>
    api.post("/auth/forgot-password/", { email }),
  resetPassword: (data: {
    email: string;
    code: string;
    password: string;
    password_confirm: string;
  }) => api.post("/auth/reset-password/", data),
  getUser: () => api.get("/auth/me/"),
  updateProfile: (data: any) => api.patch("/auth/profile/", data),
};

// Master Consultations API
export const consultationsAPI = {
  list: (params?: { status?: string; search?: string }) => api.get("/consultations/consultations/", { params }),
  create: (data: { chief_complaint: string }) =>
    api.post("/consultations/consultations/", data),
  get: (id: number) => api.get(`/consultations/consultations/${id}/`),
  update: (id: number, data: any) =>
    api.patch(`/consultations/consultations/${id}/`, data),
  complete: (id: number) =>
    api.post(`/consultations/consultations/${id}/complete/`),
  assignDoctor: (id: number, doctorId: number) =>
    api.post(`/consultations/consultations/${id}/assign_doctor/`, { doctor_id: doctorId }),
  overrideStatus: (id: number, status: string) =>
    api.post(`/consultations/consultations/${id}/override_status/`, { status }),
};

// Symptoms API
export const symptomsAPI = {
  list: () => api.get("/consultations/symptoms/"),
  create: (data: any) => api.post("/consultations/symptoms/", data),
};

// Patient Symptoms API
export const patientSymptomsAPI = {
  list: (consultationId?: number) =>
    api.get("/consultations/patient-symptoms/", {
      params: consultationId ? { consultation: consultationId } : {},
    }),
  create: (data: any) => api.post("/consultations/patient-symptoms/", data),
};

// Medical History API
export const medicalHistoryAPI = {
  list: () => api.get("/patients/medical-history/"),
  create: (data: any) => api.post("/patients/medical-history/", data),
  get: (id: number) => api.get(`/patients/medical-history/${id}/`),
  update: (id: number, data: any) =>
    api.patch(`/patients/medical-history/${id}/`, data),
};

// AI API
export const aiAPI = {
  analyzeSymptoms: (data: {
    patient_input: string;
    history?: { role: "user" | "assistant"; content: string }[];
    patient_history?: string;
    current_medications?: string[];
    consultation_id?: number;
    conversation_id?: number;
  }) => api.post("/ai/analyze-symptoms/", data),
  professionalChat: (data: {
    message: string;
    history?: { role: "user" | "assistant"; content: string }[];
    context?: Record<string, unknown>;
    conversation_id?: number;
  }) => api.post("/ai/professional-chat/", data),
  conversations: (kind?: "patient" | "professional") =>
    api.get("/ai/conversations/", { params: kind ? { kind } : {} }),
  conversation: (id: number) => api.get(`/ai/conversations/${id}/`),
  deleteConversation: (id: number) => api.delete(`/ai/conversations/${id}/`),
  followUp: (data: { consultation_id: number; current_symptoms?: string[] }) =>
    api.post("/ai/follow-up/", data),
  assessUrgency: (data: { symptoms?: string[]; patient_input: string }) =>
    api.post("/ai/assess-urgency/", data),
};

// Doctors API
export const doctorsAPI = {
  dashboard: () => api.get("/doctors/dashboard/"),
  patients: () => api.get("/doctors/patients/"),
  consultations: (status?: string) =>
    api.get("/doctors/consultations/", { params: status ? { status } : {} }),
  consultationDetail: (id: number) => api.get(`/doctors/consultations/${id}/`),
  review: (id: number, data: any) =>
    api.post(`/doctors/consultations/${id}/review/`, data),
  assign: (id: number) => api.post(`/doctors/consultations/${id}/assign/`, {}),
};

// Pharmacists API
export const pharmacistsAPI = {
  dashboard: () => api.get("/pharmacists/dashboard/"),
  prescriptions: (status?: string) =>
    api.get("/pharmacists/prescriptions/", { params: status ? { status } : {} }),
  prescriptionDetail: (id: number) => api.get(`/pharmacists/prescriptions/${id}/`),
  review: (id: number, data: any) =>
    api.post(`/pharmacists/prescriptions/${id}/review/`, data),
  interactions: (medicationId: number) =>
    api.get(`/pharmacists/medications/${medicationId}/interactions/`),
};

// Medications catalog API
export const medicationsAPI = {
  list: (params?: { search?: string; drug_class?: string }) =>
    api.get("/medications/medications/", { params }),
  get: (id: number) => api.get(`/medications/medications/${id}/`),
  create: (data: any) => api.post("/medications/medications/", data),
  update: (id: number, data: any) => api.patch(`/medications/medications/${id}/`, data),
  delete: (id: number) => api.delete(`/medications/medications/${id}/`),
  interactions: (id: number) =>
    api.get(`/medications/medications/${id}/interactions/`),
  createInteraction: (data: any) => api.post("/medications/interactions/", data),
  deleteInteraction: (id: number) => api.delete(`/medications/interactions/${id}/`),
};

// Medical conditions catalog API
export const medicalAPI = {
  conditions: (params?: { search?: string; category?: string }) =>
    api.get("/medical/conditions/", { params }),
  condition: (id: number) => api.get(`/medical/conditions/${id}/`),
  createCondition: (data: any) => api.post("/medical/conditions/", data),
  updateCondition: (id: number, data: any) => api.patch(`/medical/conditions/${id}/`, data),
  deleteCondition: (id: number) => api.delete(`/medical/conditions/${id}/`),
};

// Knowledge / approved sources API
export const knowledgeAPI = {
  sources: () => api.get("/knowledge/sources/"),
  addSource: (data: any) => api.post("/knowledge/sources/add/", data),
  updateSource: (id: number, data: any) => api.patch(`/knowledge/sources/${id}/`, data),
  deleteSource: (id: number) => api.delete(`/knowledge/sources/${id}/delete/`),
  syncIndex: () => api.post("/knowledge/sources/sync/"),
  search: (data: { query: string; limit?: number; filter_approved?: boolean }) =>
    api.post("/knowledge/search/", data),
};

// System Settings API (Admin)
export const adminSettingsAPI = {
  get: () => api.get("/admin/settings/"),
  update: (data: any) => api.post("/admin/settings/update/", data),
};

// Audit logs API (admin)
export const auditAPI = {
  logs: (params?: { action?: string; entity_type?: string }) =>
    api.get("/audit/logs/", { params }),
};

// Admin users API
export const usersAPI = {
  list: (params?: { role?: string; search?: string }) =>
    api.get("/auth/users/", { params }),
  create: (data: any) => api.post("/auth/users/", data),
  update: (id: number, data: any) => api.patch(`/auth/users/${id}/`, data),
  delete: (id: number) => api.delete(`/auth/users/${id}/`),
};

// Patient profile API
export const patientProfileAPI = {
  get: () => api.get("/auth/profile/patient/"),
  update: (data: any) => api.patch("/auth/profile/patient/", data),
};

