export type Persona = "customer" | "staff";

export type SessionStatus = "anonymous" | "authenticating" | "authenticated" | "expired";

export type SessionActor = {
  sessionStatus: "authenticated";
  tenantId: string;
  actorId: string;
  displayName: string;
  role: Persona;
  memberId: string | null;
  storeId: string | null;
};
