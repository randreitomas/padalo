import type {
  Bill,
  BillPayload,
  AgentChatPayload,
  DashboardSummary,
  Envelope,
  EnvelopePayload,
  Household,
  HouseholdPayload,
  Paginated,
  Remittance,
  RemittancePayload,
  Transaction,
  TransactionPayload,
} from "@/lib/api/types";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000").replace(
  /\/$/,
  "",
);

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...init.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, body?.detail ?? "The request could not be completed.");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

function json(method: "POST" | "PATCH", body: unknown): RequestInit {
  return { method, body: JSON.stringify(body) };
}

function listPath(path: string, params?: Record<string, string | number | undefined>) {
  const query = new URLSearchParams();
  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (value !== undefined) query.set(key, String(value));
  });
  const suffix = query.toString();
  return suffix ? `${path}?${suffix}` : path;
}

export const api = {
  listHouseholds: () => request<Paginated<Household>>("/api/v1/households"),
  async resetDemo(): Promise<void> {
    const response = await fetch("/api/demo/reset", { method: "POST", cache: "no-store" });
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new ApiError(response.status, body?.detail ?? "The demo household could not be reset.");
    }
  },
  getHousehold: (householdId: string) => request<Household>(`/api/v1/households/${householdId}`),
  createHousehold: (payload: HouseholdPayload) =>
    request<Household>("/api/v1/households", json("POST", payload)),
  updateHousehold: (householdId: string, payload: Partial<HouseholdPayload>) =>
    request<Household>(`/api/v1/households/${householdId}`, json("PATCH", payload)),
  deleteHousehold: (householdId: string) =>
    request<void>(`/api/v1/households/${householdId}`, { method: "DELETE" }),

  getDashboard: (householdId: string) =>
    request<DashboardSummary>(`/api/v1/households/${householdId}/dashboard/summary`),

  listEnvelopes: (householdId: string) =>
    request<Paginated<Envelope>>(`/api/v1/households/${householdId}/envelopes`),
  createEnvelope: (householdId: string, payload: EnvelopePayload) =>
    request<Envelope>(`/api/v1/households/${householdId}/envelopes`, json("POST", payload)),
  updateEnvelope: (householdId: string, envelopeId: string, payload: Partial<EnvelopePayload>) =>
    request<Envelope>(
      `/api/v1/households/${householdId}/envelopes/${envelopeId}`,
      json("PATCH", payload),
    ),
  deleteEnvelope: (householdId: string, envelopeId: string) =>
    request<void>(`/api/v1/households/${householdId}/envelopes/${envelopeId}`, {
      method: "DELETE",
    }),

  listTransactions: (householdId: string) =>
    request<Paginated<Transaction>>(`/api/v1/households/${householdId}/transactions`),
  createTransaction: (householdId: string, payload: TransactionPayload) =>
    request<Transaction>(`/api/v1/households/${householdId}/transactions`, json("POST", payload)),
  updateTransaction: (
    householdId: string,
    transactionId: string,
    payload: Partial<TransactionPayload>,
  ) =>
    request<Transaction>(
      `/api/v1/households/${householdId}/transactions/${transactionId}`,
      json("PATCH", payload),
    ),
  deleteTransaction: (householdId: string, transactionId: string) =>
    request<void>(`/api/v1/households/${householdId}/transactions/${transactionId}`, {
      method: "DELETE",
    }),

  listRemittances: (householdId: string) =>
    request<Paginated<Remittance>>(`/api/v1/households/${householdId}/remittances`),
  createRemittance: (householdId: string, payload: RemittancePayload) =>
    request<Remittance>(`/api/v1/households/${householdId}/remittances`, json("POST", payload)),
  updateRemittance: (
    householdId: string,
    remittanceId: string,
    payload: Partial<RemittancePayload>,
  ) =>
    request<Remittance>(
      `/api/v1/households/${householdId}/remittances/${remittanceId}`,
      json("PATCH", payload),
    ),
  deleteRemittance: (householdId: string, remittanceId: string) =>
    request<void>(`/api/v1/households/${householdId}/remittances/${remittanceId}`, {
      method: "DELETE",
    }),

  listBills: (householdId: string, status?: string) =>
    request<Paginated<Bill>>(listPath(`/api/v1/households/${householdId}/bills`, { status })),
  createBill: (householdId: string, payload: BillPayload) =>
    request<Bill>(`/api/v1/households/${householdId}/bills`, json("POST", payload)),
  updateBill: (householdId: string, billId: string, payload: Partial<BillPayload>) =>
    request<Bill>(`/api/v1/households/${householdId}/bills/${billId}`, json("PATCH", payload)),
  deleteBill: (householdId: string, billId: string) =>
    request<void>(`/api/v1/households/${householdId}/bills/${billId}`, { method: "DELETE" }),

  async openAgentStream(householdId: string, payload: AgentChatPayload): Promise<Response> {
    const response = await fetch(`${API_BASE_URL}/api/v1/households/${householdId}/agent/stream`, {
      method: "POST",
      cache: "no-store",
      headers: {
        Accept: "text/event-stream",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new ApiError(response.status, body?.detail ?? "The assistant could not be reached.");
    }

    return response;
  },
};
