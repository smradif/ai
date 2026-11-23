import { getAccessToken } from "./service";
import { ErrorResponse, AuthError } from "./types";

const API_BASE_URL = "http://localhost:8000";

export const post = async <T>(path: string, payload: unknown): Promise<T> => {
  try {
    const accessToken = getAccessToken();
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}` || "",
      },
      body: JSON.stringify(payload),
    });

    const result = (await response.json()) as ErrorResponse | null;

    if (!response.ok) {
      if (response.status === 401) {
        throw new AuthError("Unauthorized access. Please log in again.", 401);
      }
      throw new Error(
        result?.detail
          ? String(result.detail)
          : `Request failed  with status: ${response.status}`,
      );
    }

    return result as T;
  } catch (error) {
    throw error;
  }
};

export const get = async <T>(path: string): Promise<T> => {
  try {
    const accessToken = getAccessToken();
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}` || "",
      },
    });

    const result = (await response.json()) as ErrorResponse | null;

    if (!response.ok) {
      if (response.status === 401) {
        throw new AuthError("Unauthorized access. Please log in again.", 401);
      }
      throw new Error(
        result?.detail
          ? String(result.detail)
          : `Request failed  with status: ${response.status}`,
      );
    }

    return result as T;
  } catch (error) {
    throw error;
  }
};


export const postJSON = async <T>(path: string, item: T) => {
  try {
    const accessToken = getAccessToken();
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}` || "",
      },
      body: JSON.stringify({
        ...item,
      }),
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new AuthError("Unauthorized access. Please log in again.", 401);
      }
      throw new Error(`Request failed  with status: ${response.status}`);
    }
    return response.body?.getReader();
  } catch (error) {
    throw error;
  }
};
