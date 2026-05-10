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

export type Reservation = {
  reservationId: string;
  status: "BOOKED" | "CANCELLED" | string;
  tableCode?: string;
  storeId: string;
  slotId?: string;
  slotStartAt?: string;
  partySize: number;
  checkedInAt?: string | null;
};

export type CreateReservationInput = {
  memberId: string;
  storeId: string;
  slotId: string;
  partySize: number;
  preferredTheme?: string;
  catInteractionMode?: string;
};

const tenantId = "tenant-nekocafe";
const memberApiBase = import.meta.env.VITE_MEMBER_API_BASE ?? "http://127.0.0.1:8002";
const reservationApiBase = import.meta.env.VITE_RESERVATION_API_BASE ?? "http://127.0.0.1:8001";

async function requestJson<T>(url: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Tenant-Id": tenantId,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => undefined);
    const message = payload?.detail?.message ?? payload?.message ?? "请求暂时没有成功";
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function getMember(memberId: string): Promise<Member> {
  return requestJson<Member>(`${memberApiBase}/member/v1/members/${memberId}`);
}

export function getPoints(memberId: string): Promise<PointAccount> {
  return requestJson<PointAccount>(`${memberApiBase}/member/v1/members/${memberId}/points`);
}

export function getSlots(storeId: string, date: string, partySize: number): Promise<Slot[]> {
  const params = new URLSearchParams({ date, partySize: String(partySize) });
  return requestJson<Slot[]>(
    `${reservationApiBase}/reservation/v1/stores/${storeId}/slots?${params.toString()}`,
  );
}

export function createReservation(input: CreateReservationInput): Promise<Reservation> {
  return requestJson<Reservation>(`${reservationApiBase}/reservation/v1/reservations`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getMemberReservations(memberId: string): Promise<Reservation[]> {
  return requestJson<Reservation[]>(
    `${reservationApiBase}/reservation/v1/members/${memberId}/reservations`,
  );
}

export function cancelReservation(reservationId: string): Promise<Reservation> {
  return requestJson<Reservation>(
    `${reservationApiBase}/reservation/v1/reservations/${reservationId}/cancel`,
    {
      method: "POST",
    },
  );
}
