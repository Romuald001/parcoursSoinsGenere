import { createContext } from "react";

export interface AuthState {
  token: string | null;
  role: "doctor" | "patient" | "admin" | null;
  patientId: string | null;
}

export interface AuthContextValue extends AuthState {
  login: (identifier: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);
