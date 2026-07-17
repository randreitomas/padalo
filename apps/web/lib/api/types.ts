export type Decimal = string;

export type Paginated<T> = {
  items: T[];
  limit: number;
  offset: number;
};

export type Household = {
  id: string;
  name: string;
  base_currency: string;
  home_country: string;
  created_by_user_id: string | null;
  created_at: string;
  updated_at: string;
};

export type Envelope = {
  id: string;
  household_id: string;
  name: string;
  target_amount_php: Decimal;
  current_balance_php: Decimal;
  sort_order: number;
  created_at: string;
  updated_at: string;
};

export type TransactionType = "expense" | "refund" | "adjustment";
export type TransactionSource = "manual" | "chat" | "receipt";

export type Transaction = {
  id: string;
  household_id: string;
  envelope_id: string | null;
  logged_by_member_id: string | null;
  amount_php: Decimal;
  transaction_type: TransactionType;
  source: TransactionSource;
  merchant: string | null;
  note: string | null;
  receipt_url: string | null;
  occurred_on: string;
  created_at: string;
  updated_at: string;
};

export type Remittance = {
  id: string;
  household_id: string;
  recorded_by_member_id: string | null;
  amount_php: Decimal;
  source_amount: Decimal;
  source_currency: string;
  provider: string;
  fee_php: Decimal;
  rate_used: Decimal;
  sent_at: string;
  created_at: string;
  updated_at: string;
};

export type BillStatus = "scheduled" | "paid" | "skipped";

export type Bill = {
  id: string;
  household_id: string;
  name: string;
  amount_php: Decimal;
  due_date: string;
  category: string | null;
  recurring: boolean;
  recurrence_rule: string | null;
  status: BillStatus;
  created_at: string;
  updated_at: string;
};

export type DashboardSummary = {
  household: Household;
  as_of: string;
  total_envelope_target_php: Decimal;
  total_envelope_balance_php: Decimal;
  total_remitted_php: Decimal;
  total_spent_this_month_php: Decimal;
  total_upcoming_bills_php: Decimal;
  upcoming_bill_count: number;
  envelopes: Envelope[];
  upcoming_bills: Bill[];
  recent_transactions: Transaction[];
};

export type HouseholdPayload = Pick<Household, "name" | "base_currency" | "home_country">;
export type EnvelopePayload = Pick<
  Envelope,
  "name" | "target_amount_php" | "current_balance_php" | "sort_order"
>;
export type TransactionPayload = Omit<
  Transaction,
  "id" | "household_id" | "created_at" | "updated_at"
>;
export type RemittancePayload = Omit<
  Remittance,
  "id" | "household_id" | "created_at" | "updated_at"
>;
export type BillPayload = Omit<Bill, "id" | "household_id" | "created_at" | "updated_at">;

export type AgentChatPayload = {
  message: string;
  conversation_id?: string;
};
