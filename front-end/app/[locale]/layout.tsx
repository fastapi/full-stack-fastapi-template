import type { ReactNode } from "react";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { NextIntlClientProvider } from "next-intl";
import { getMessages, setRequestLocale } from "next-intl/server";
import { locales, isLocale } from "@/lib/i18n";
import { fontVariables } from "@/app/fonts";
import Providers from "@/components/ui/Providers";
import "@/app/globals.css";

export const metadata: Metadata = {
  title: "Tabula — Turn Documents into Data",
  description:
    "Tabula reads your PDFs, scans, and images and reconstructs every table into a clean, formula-ready Excel file.",
};

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params: { locale },
}: {
  children: ReactNode;
  params: { locale: string };
}) {
  if (!isLocale(locale)) notFound();

  setRequestLocale(locale);
  const messages = await getMessages();

  return (
    <html lang={locale} suppressHydrationWarning className={fontVariables}>
      <body>
        <Providers>
          <NextIntlClientProvider messages={messages}>
            {children}
          </NextIntlClientProvider>
        </Providers>
      </body>
    </html>
  );
}
