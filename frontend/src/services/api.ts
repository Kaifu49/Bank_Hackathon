import { ApiEnvelope } from "../types/api";

export class ApiError extends Error {
  code: string;
  status: number;
  details?: Record<string, any>;

  constructor(message: string, code: string, status: number, details?: Record<string, any>) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export function getApiBaseUrl(): string {
  if (typeof window !== "undefined") {
    let localOverride = localStorage.getItem("finintel_api_base_url");
    if (localOverride) {
      localOverride = localOverride.trim().replace(/\/$/, "");
      if (localOverride.toLowerCase().includes("localhot")) {
        localOverride = localOverride.replace(/localhot/i, "localhost");
        localStorage.setItem("finintel_api_base_url", localOverride);
      }
      return localOverride;
    }
  }

  // @ts-ignore
  const envUrl = import.meta.env?.VITE_FININTEL_API_BASE_URL;
  if (envUrl) {
    return envUrl.trim().replace(/\/$/, "");
  }

  return "http://localhost:8080";
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}${path.startsWith("/") ? path : `/${path}`}`;

  const headers = new Headers(options.headers || {});
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  // Do not set Content-Type for FormData, browser will automatically set boundary
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const mergedOptions: RequestInit = {
    ...options,
    headers,
  };

  let response: Response;
  try {
    response = await fetch(url, mergedOptions);
  } catch (error: any) {
    // Network / Offline error
    throw new ApiError(
      error?.message || "Network request failed. Backend service might be offline.",
      "NETWORK_ERROR",
      502
    );
  }

  if (response.status === 415) {
    const errorJson = await response.json().catch(() => ({}));
    throw new ApiError(
      errorJson?.error?.message || "Unsupported media type uploaded.",
      "UNSUPPORTED_MEDIA_TYPE",
      415,
      errorJson?.error?.details
    );
  }

  // Parse JSON envelope
  let envelope: ApiEnvelope<T>;
  try {
    envelope = await response.json();
  } catch (err) {
    if (!response.ok) {
      throw new ApiError(
        `HTTP Error ${response.status}: ${response.statusText}`,
        "HTTP_ERROR",
        response.status
      );
    }
    throw new ApiError("Failed to parse JSON response from server.", "PARSE_ERROR", 500);
  }

  if (!envelope.success || envelope.error) {
    const errObj = envelope.error || { code: "UNKNOWN_ERROR", message: "An unknown error occurred." };
    throw new ApiError(
      errObj.message,
      errObj.code,
      response.status,
      errObj.details
    );
  }

  if (envelope.data === null) {
    throw new ApiError("Server returned a success response but the payload data was empty.", "EMPTY_DATA", 200);
  }

  return envelope.data;
}
