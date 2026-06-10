import type { ReactNode } from "react";

// The locale layout owns <html>/<body>; this root simply passes children through
// (required by Next.js App Router).
export default function RootLayout({ children }: { children: ReactNode }) {
  return children;
}
