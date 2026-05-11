import {
  createContext,
  type PropsWithChildren,
  useContext,
  useEffect,
  useState,
} from "react";
import { getSessionMe, loginSession, logoutSession } from "../api";
import { clearSessionToken, readSessionToken, writeSessionToken } from "./storage";
import type { Persona, SessionActor, SessionStatus } from "./types";

type AuthContextValue = {
  session: SessionActor | null;
  sessionStatus: SessionStatus;
  token: string | null;
  authNotice: string;
  loginAs: (persona: Persona) => Promise<void>;
  logout: () => Promise<void>;
  clearNotice: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [session, setSession] = useState<SessionActor | null>(null);
  const [sessionStatus, setSessionStatus] = useState<SessionStatus>("authenticating");
  const [token, setToken] = useState<string | null>(null);
  const [authNotice, setAuthNotice] = useState("");

  useEffect(() => {
    async function restoreSession() {
      const storedToken = readSessionToken();
      if (!storedToken) {
        setSessionStatus("anonymous");
        setToken(null);
        return;
      }

      setSessionStatus("authenticating");
      try {
        const nextSession = await getSessionMe(storedToken);
        setToken(storedToken);
        setSession(nextSession);
        setSessionStatus("authenticated");
      } catch {
        clearSessionToken();
        setSession(null);
        setToken(null);
        setSessionStatus("expired");
        setAuthNotice("上次会话已失效，请重新进入。");
      }
    }

    void restoreSession();
  }, []);

  async function loginAs(persona: Persona) {
    setSessionStatus("authenticating");
    setAuthNotice("");
    const payload = await loginSession(persona);
    writeSessionToken(payload.sessionToken);
    setToken(payload.sessionToken);
    setSession({
      sessionStatus: "authenticated",
      tenantId: payload.tenantId,
      actorId: payload.actorId,
      displayName: payload.displayName,
      role: payload.role,
      memberId: payload.memberId,
      storeId: payload.storeId,
    });
    setSessionStatus("authenticated");
  }

  async function logout() {
    await logoutSession(token);
    clearSessionToken();
    setSession(null);
    setToken(null);
    setSessionStatus("anonymous");
    setAuthNotice("已退出当前会话。");
  }

  function clearNotice() {
    setAuthNotice("");
  }

  return (
    <AuthContext.Provider
      value={{ session, sessionStatus, token, authNotice, loginAs, logout, clearNotice }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
