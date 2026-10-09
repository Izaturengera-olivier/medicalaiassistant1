import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Platform } from "react-native";

// Android emulators reach the host machine at 10.0.2.2; a physical device needs
// the developer's LAN IP, so EXPO_PUBLIC_API_URL always wins when set.
const DEFAULT_API_URL =
  Platform.OS === "android"
    ? "http://10.0.2.2:8000/api"
    : "http://127.0.0.1:8000/api";

export const BASE_API_URL = process.env.EXPO_PUBLIC_API_URL || DEFAULT_API_URL;

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";

export const mobileAPI = axios.create({
  baseURL: BASE_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 60000,
});

// Bare client so refreshing a token never re-enters the interceptors below.
const authClient = axios.create({ baseURL: BASE_API_URL });

mobileAPI.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem(ACCESS_TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

type UnauthorizedHandler = () => void;
let onUnauthorized: UnauthorizedHandler | null = null;

export const setUnauthorizedHandler = (handler: UnauthorizedHandler | null) => {
  onUnauthorized = handler;
};

export const clearTokens = async () => {
  await AsyncStorage.multiRemove([ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY]);
};

const signOut = async () => {
  await clearTokens();
  onUnauthorized?.();
};

// Access tokens live 15 minutes (JWT_ACCESS_MINUTES), so a long-lived app
// session must be able to renew silently or every request starts failing.
let refreshInFlight: Promise<string | null> | null = null;

const refreshAccessToken = async (): Promise<string | null> => {
  const refreshToken = await AsyncStorage.getItem(REFRESH_TOKEN_KEY);
  if (!refreshToken) return null;

  try {
    const res = await authClient.post("/auth/token/refresh/", {
      refresh: refreshToken,
    });
    const access = res.data?.access as string | undefined;
    const nextRefresh = res.data?.refresh as string | undefined;
    if (!access) return null;
    await AsyncStorage.setItem(ACCESS_TOKEN_KEY, access);
    if (nextRefresh) {
      await AsyncStorage.setItem(REFRESH_TOKEN_KEY, nextRefresh);
    }
    return access;
  } catch {
    return null;
  }
};

mobileAPI.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as
      | (InternalAxiosRequestConfig & { _retried?: boolean })
      | undefined;

    if (error.response?.status !== 401 || !original || original._retried) {
      return Promise.reject(error);
    }

    original._retried = true;
    // Collapse concurrent 401s onto a single refresh call.
    refreshInFlight ??= refreshAccessToken().finally(() => {
      refreshInFlight = null;
    });
    const access = await refreshInFlight;

    if (!access) {
      await signOut();
      return Promise.reject(error);
    }

    original.headers.Authorization = `Bearer ${access}`;
    return mobileAPI(original);
  }
);

export interface KnowledgeSource {
  id?: number;
  name: string;
  title?: string;
  url?: string;
  source_type?: string;
  approval_status?: string;
}

export interface PossibleCondition {
  name?: string;
  condition?: string;
  probability?: number;
  reason?: string;
}

export interface AssessmentResult {
  id?: number;
  consultation_id?: number;
  conversation_id?: number;
  reply: string;
  symptoms_identified: string[];
  follow_up_questions: string[];
  possible_conditions: PossibleCondition[];
  warning_signs: string[];
  urgency_level: string;
  general_information: string;
  medication_information: Record<string, unknown>[];
  recommended_next_step: string;
  sources: KnowledgeSource[];
  model_used: string;
  confidence: number;
}

export interface ChatHistoryTurn {
  role: "user" | "assistant";
  content: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const authAPI = {
  login: (email: string, password: string) =>
    mobileAPI.post("/auth/login/", { email, password }),
  register: (data: {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
    password_confirm: string;
    role: string;
  }) => mobileAPI.post("/auth/register/", data),
  forgotPassword: (email: string) =>
    mobileAPI.post("/auth/forgot-password/", { email }),
  resetPassword: (data: {
    email: string;
    code: string;
    password: string;
    password_confirm: string;
  }) => mobileAPI.post("/auth/reset-password/", data),
  getMe: () => mobileAPI.get("/auth/me/"),
};

export const aiAPI = {
  analyzeSymptoms: (data: {
    patient_input: string;
    history?: ChatHistoryTurn[];
    consultation_id?: number;
    conversation_id?: number;
  }) => mobileAPI.post<AssessmentResult>("/ai/analyze-symptoms/", data),
  professionalChat: (data: {
    message: string;
    history?: ChatHistoryTurn[];
    conversation_id?: number;
  }) => mobileAPI.post<AssessmentResult>("/ai/professional-chat/", data),
};

export const consultationsAPI = {
  list: () => mobileAPI.get<Paginated<Consultation>>("/consultations/consultations/"),
  create: (chief_complaint: string) =>
    mobileAPI.post<{ id: number }>("/consultations/consultations/", { chief_complaint }),
};

export interface Consultation {
  id: number;
  chief_complaint: string;
  status: string;
  created_at: string;
}

export interface SystemSettings {
  ai_provider: string;
  ai_triage_mode: string;
  web_search_enabled: boolean;
  maintenance_mode: boolean;
  system_notice: string;
  allow_registration: boolean;
  last_updated: string;
}

export const adminAPI = {
  users: () => mobileAPI.get<Paginated<{ id: number; email: string; role: string }>>("/auth/users/"),
  settings: () => mobileAPI.get<SystemSettings>("/admin/settings/"),
  sources: () => mobileAPI.get<{ sources: KnowledgeSource[]; total: number }>("/knowledge/sources/"),
};
