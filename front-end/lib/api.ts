import { ApiError, OpenAPI } from "@/lib/client";

/** Cookie that holds the backend JWT. Non-httpOnly so the browser SDK can send it. */
export const TOKEN_COOKIE = "tabula_token";

export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Reads the auth token from `document.cookie` (browser only). */
export function readToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|;\\s*)${TOKEN_COOKIE}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

OpenAPI.BASE = API_BASE;
OpenAPI.TOKEN = async () => readToken() ?? "";

/** Extracts a human-readable message from an SDK error. */
export function apiMessage(err: unknown): string {
  if (err instanceof ApiError) {
    const detail = (err.body as { detail?: unknown } | null)?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      const msg = (detail[0] as { msg?: unknown } | undefined)?.msg;
      if (typeof msg === "string") return msg;
    }
    return err.message;
  }
  if (err instanceof Error) return err.message;
  return String(err);
}
