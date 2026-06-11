"use client";

import { useTransition } from "react";
import { useLocale, useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { signup } from "@/lib/actions";

export default function SignupForm() {
  const t = useTranslations("auth.signup");
  const locale = useLocale();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const error = searchParams.get("error");

  const errorMessage =
    error === "exists" ? t("errorExists") : error === "unreachable" ? t("errorUnreachable") : t("error");

  return (
    <form
      className="auth-form"
      action={(formData) => startTransition(() => void signup(locale, formData))}
    >
      {error && <div className="field-error">{errorMessage}</div>}

      <div className="field">
        <label htmlFor="signup-name">{t("name")}</label>
        <input
          id="signup-name"
          name="name"
          type="text"
          required
          autoComplete="name"
          placeholder={t("namePlaceholder")}
        />
      </div>

      <div className="field">
        <label htmlFor="signup-email">{t("email")}</label>
        <input
          id="signup-email"
          name="email"
          type="email"
          required
          autoComplete="email"
          placeholder={t("emailPlaceholder")}
        />
      </div>

      <div className="field">
        <label htmlFor="signup-password">{t("password")}</label>
        <input
          id="signup-password"
          name="password"
          type="password"
          required
          minLength={8}
          autoComplete="new-password"
          placeholder={t("passwordPlaceholder")}
        />
      </div>

      <button type="submit" className="btn btn-primary" disabled={isPending}>
        {t("submit")}
      </button>
    </form>
  );
}
