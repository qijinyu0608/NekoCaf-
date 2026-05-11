import type { Persona, SessionActor } from "./auth/types";

export type Member = {
  memberId: string;
  tenantId: string;
  nickname: string;
  mobileMasked: string;
  loyaltyLevel: string;
  preferences: string[];
};

export type PointAccount = {
  memberId: string;
  currentPoints: number;
  pendingPoints: number;
  levelCode: string;
  benefitSummary: string[];
};

export type Slot = {
  slotId: string;
  startAt: string;
  capacity: number;
  theme: string;
};

export type CustomerReservation = {
  reservationId: string;
  status: "BOOKED" | "CHECKED_IN" | "CANCELLED" | string;
  storeId: string;
  slotStartAt: string;
  partySize: number;
  theme: string;
};

export type Reservation = {
  reservationId: string;
  status: "BOOKED" | "CHECKED_IN" | "CANCELLED" | string;
  tableCode?: string;
  storeId: string;
  slotId?: string;
  partySize: number;
  checkedInAt?: string | null;
};

export type StaffReservation = {
  reservationId: string;
  memberId: string;
  memberNickname: string;
  status: "BOOKED" | "CHECKED_IN" | "CANCELLED" | string;
  slotStartAt: string;
  partySize: number;
  tableCode: string;
};

export type CreateMyReservationInput = {
  storeId: string;
  slotId: string;
  partySize: number;
  preferredTheme?: string;
  catInteractionMode?: string;
};

const memberApiBase = import.meta.env.VITE_MEMBER_API_BASE ?? "http://127.0.0.1:8002";
const reservationApiBase = import.meta.env.VITE_RESERVATION_API_BASE ?? "http://127.0.0.1:8001";
const tenantId = "tenant-nekocafe";

async function requestJson<T>(
  url: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : { "X-Tenant-Id": tenantId }),
      ...options.headers,
    },
  });

  if (response.status === 204) {
    return undefined as T;
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => undefined);
    const message = payload?.detail?.message ?? payload?.message ?? "请求暂时没有成功";
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function loginSession(persona: Persona): Promise<{ sessionToken: string } & SessionActor> {
  return requestJson(`${memberApiBase}/member/v1/session/login`, {
    method: "POST",
    body: JSON.stringify({ persona }),
  });
}

export function getSessionMe(token: string): Promise<SessionActor> {
  return requestJson<SessionActor>(`${memberApiBase}/member/v1/session/me`, {}, token);
}

export function logoutSession(token: string | null): Promise<void> {
  return requestJson<void>(
    `${memberApiBase}/member/v1/session/logout`,
    { method: "POST" },
    token,
  );
}

export function getCurrentMember(token: string): Promise<Member> {
  return requestJson<Member>(`${memberApiBase}/member/v1/me`, {}, token);
}

export function getCurrentPoints(token: string): Promise<PointAccount> {
  return requestJson<PointAccount>(`${memberApiBase}/member/v1/me/points`, {}, token);
}

export function getSlots(
  storeId: string,
  date: string,
  partySize: number,
  token?: string | null,
): Promise<Slot[]> {
  const params = new URLSearchParams({ date, partySize: String(partySize) });
  return requestJson<Slot[]>(
    `${reservationApiBase}/reservation/v1/stores/${storeId}/slots?${params.toString()}`,
    {},
    token,
  );
}

export function getMyReservations(token: string): Promise<CustomerReservation[]> {
  return requestJson<CustomerReservation[]>(
    `${reservationApiBase}/reservation/v1/me/reservations`,
    {},
    token,
  );
}

export function createMyReservation(
  token: string,
  input: CreateMyReservationInput,
): Promise<Reservation> {
  return requestJson<Reservation>(
    `${reservationApiBase}/reservation/v1/me/reservations`,
    {
      method: "POST",
      body: JSON.stringify(input),
    },
    token,
  );
}

export function cancelReservation(token: string, reservationId: string): Promise<Reservation> {
  return requestJson<Reservation>(
    `${reservationApiBase}/reservation/v1/reservations/${reservationId}/cancel`,
    {
      method: "POST",
    },
    token,
  );
}

export function getStoreReservations(
  token: string,
  storeId: string,
  businessDate: string,
  status?: string,
): Promise<StaffReservation[]> {
  const params = new URLSearchParams({ businessDate });
  if (status) {
    params.set("status", status);
  }
  return requestJson<StaffReservation[]>(
    `${reservationApiBase}/staff/v1/stores/${storeId}/reservations?${params.toString()}`,
    {},
    token,
  );
}

export function checkInReservation(token: string, reservationId: string): Promise<Reservation> {
  return requestJson<Reservation>(
    `${reservationApiBase}/reservation/v1/reservations/${reservationId}/check-in`,
    {
      method: "POST",
    },
    token,
  );
}
