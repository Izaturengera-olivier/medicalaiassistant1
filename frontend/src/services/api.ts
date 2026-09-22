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
  getUser: () => api.get("/auth/me/"),
  updateProfile: (data: any) => api.patch("/auth/profile/", data),
};

// Consultations API
export const consultationsAPI = {
  list: () => api.get("/consultations/consultations/"),
  create: (data: { chief_complaint: string }) =>
    api.post("/consultations/consultations/", data),
  get: (id: number) => api.get(`/consultations/consultations/${id}/`),
  update: (id: number, data: any) =>
    api.patch(`/consultations/consultations/${id}/`, data),
  complete: (id: number) =>
    api.post(`/consultations/consultations/${id}/complete/`),
  assignDoctor: (id: number, doctorId: number) =>
    api.post(`/consultations/consultations/${id}/assign_doctor/`, { doctor_id: doctorId }),
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
