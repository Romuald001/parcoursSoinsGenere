import { useCallback, useState, type ReactNode } from "react";
import apiClient from "../api/client";
import { AUTH_STORAGE_KEY } from "../auth/storageKey";
import { AuthContext, type AuthState } from "./authContext";

function loadStoredAuth(): AuthState {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return { token: null, role: null, patientId: null };
    return JSON.parse(raw);
  } catch {
    return { token: null, role: null, patientId: null };
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthState>(loadStoredAuth);

  const login = useCallback(async (identifier: string, password: string) => {
    const { data } = await apiClient.post("/auth/login", { identifier, password });
    const next: AuthState = {
      token: data.access_token,
      role: data.role,
      patientId: data.patient_id ?? null,
    };
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(next));
    setAuth(next);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    setAuth({ token: null, role: null, patientId: null });
  }, []);

  return (
    <AuthContext.Provider value={{ ...auth, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
