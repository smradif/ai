export interface RegistrationRequest {
  fname: string;
  lname: string;
  email: string;
  password: string;
}

export interface RegisteredUser {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
}

export interface ErrorResponse {
  detail: string;
}

export interface RequestItemBase {
  name: string;
  query: string;
  session_id?: string;
}

export interface MoneyItemRequest extends RequestItemBase {
  id: string;
}

export interface ChatRequest extends RequestItemBase {
  vendor_id?: number;
  previous_state_id?: number;
}

export interface VendorResponse {
  id: number;
  name: string;
}

export interface ChatHistoryResponse {
  id: number;
  title: string;
  conversation: string;
  created_at: string;
}

export class AuthError extends Error {
  statusCode: number = 401;
  constructor(
    message: string = "Unauthorized access. Please log in again.",
    statusCode: number = 401,
  ) {
    super(message);
    this.name = "AuthError";
    this.statusCode = statusCode;
  }
}

export interface Page {
  id: number;
  title: string;
  path: string;
  isMenuItem?: boolean
  component: () => React.JSX.Element;
}
