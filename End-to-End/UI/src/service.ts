import { get, post, postJSON } from "./baseService";
import {
  RegistrationRequest,
  RegisteredUser,
  LoginRequest,
  LoginResponse,
  MoneyItemRequest,
  ChatRequest,
  AuthError,
} from "./types";

export const registerUser = (payload: RegistrationRequest) =>
  post<RegisteredUser>("/users/register", payload);

export const loginUser = (payload: LoginRequest) =>
  post<LoginResponse>("/users/login", payload);

export const getMoneyTransferResponse = async (item: MoneyItemRequest) =>
  postJSON("/money-agent", item);

export const getChatResponse = async (item: ChatRequest) =>
  postJSON("/chat-agent", item);

export const getSuervisorResponse = async (item: MoneyItemRequest) =>
  postJSON("/supervisor-agent", item);

export const getOrchestratorResponse = async (item: MoneyItemRequest) =>
  postJSON("/orchestrator-agent", item);

export const getVendorsResponse = async <T>() => get("/vendors") as T;

export const getChatsHistoryResponse = async <T>(vendor_id: number) => {
  try {
    return (await get(`/chats/${vendor_id}`)) as T;
  } catch (error) {
    console.log(error);
    if (error instanceof AuthError) {
      redirectToLogin("chat");
    } else {
      throw error;
    }
  }
};
export const getChatHistoryResponse = async <T>(id: number) => {
  try {
    return (await get(`/chat/${id}`)) as T;
  } catch (error) {
    console.log(error);
    if (error instanceof AuthError) {
      redirectToLogin("chat");
    } else {
      throw error;
    }
  }
};

export const isAuthenticated = (): boolean => {
  const accessToken = window.localStorage.getItem("access_token");
  return !!accessToken;
};

export const getAccessToken = (): string | null => {
  return window.localStorage.getItem("access_token");
};

export const redirectToLogin = (returnUrl: string) => {
  window.location.href = `/login?returnUrl=${returnUrl}`;
};
