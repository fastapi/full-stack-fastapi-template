"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { TOKEN_COOKIE } from "@/lib/api";
import { ApiError, LoginService, UsersService } from "@/lib/client";

const TOKEN_MAX_AGE = 60 * 60 * 24 * 7;

async function setTokenCookie(token: string): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.set(TOKEN_COOKIE, token, {
    path: "/",
    maxAge: TOKEN_MAX_AGE,
    sameSite: "lax",
    // Not httpOnly: the generated API client also sends this token from the browser.
    httpOnly: false,
  });
}

/** Signs in against the API and stores the access token in a cookie. */
export async function login(locale: string, formData: FormData): Promise<void> {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");

  let token: string;
  try {
    const res = await LoginService.loginAccessToken({
      formData: { username: email, password },
    });
    token = res.access_token;
  } catch (err) {
    if (err instanceof ApiError) redirect(`/${locale}/login?error=invalid`);
    redirect(`/${locale}/login?error=unreachable`);
  }

  await setTokenCookie(token);
  redirect(`/${locale}/dashboard`);
}

/** Registers a new account via the API, then signs it in. */
export async function signup(locale: string, formData: FormData): Promise<void> {
  const fullName = String(formData.get("name") ?? "").trim();
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");

  let token: string;
  try {
    await UsersService.registerUser({
      requestBody: { email, password, full_name: fullName || null },
    });
    const res = await LoginService.loginAccessToken({
      formData: { username: email, password },
    });
    token = res.access_token;
  } catch (err) {
    if (err instanceof ApiError && err.status === 400) redirect(`/${locale}/signup?error=exists`);
    if (err instanceof ApiError) redirect(`/${locale}/signup?error=invalid`);
    redirect(`/${locale}/signup?error=unreachable`);
  }

  await setTokenCookie(token);
  redirect(`/${locale}/dashboard`);
}

/** Clears the session cookie and returns to the login page. */
export async function logout(locale: string): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete(TOKEN_COOKIE);
  redirect(`/${locale}/login`);
}
