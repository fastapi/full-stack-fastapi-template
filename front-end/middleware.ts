import createMiddleware from "next-intl/middleware";
import { locales, defaultLocale } from "@/lib/i18n";

export default createMiddleware({
  locales,
  defaultLocale,
  localePrefix: "always",
});

export const config = {
  // Match all pathnames except for api, _next, _vercel, and files with an extension
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
