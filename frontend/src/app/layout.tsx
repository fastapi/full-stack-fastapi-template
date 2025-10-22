'use client';
import './globals.css';

import { Outfit } from 'next/font/google';
import { SidebarProvider } from '@/context/SidebarContext';
import { ThemeProvider } from '@/context/ThemeContext';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { OpenAPI } from "@/client/core/OpenAPI";

OpenAPI.TOKEN = async () => {
  return localStorage.getItem("access_token") || ""
}

OpenAPI.BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const queryClient = new QueryClient();

const outfit = Outfit({
  subsets: ["latin"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${outfit.className} dark:bg-gray-900`}>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider>
            <SidebarProvider>{children}</SidebarProvider>
          </ThemeProvider>
        </QueryClientProvider>
      </body>
    </html>
  );
}
