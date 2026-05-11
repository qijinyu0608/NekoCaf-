const SESSION_TOKEN_KEY = "nekocafe.session-token";

export function readSessionToken(): string | null {
  return window.localStorage.getItem(SESSION_TOKEN_KEY);
}

export function writeSessionToken(token: string): void {
  window.localStorage.setItem(SESSION_TOKEN_KEY, token);
}

export function clearSessionToken(): void {
  window.localStorage.removeItem(SESSION_TOKEN_KEY);
}
