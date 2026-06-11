import type { ReactNode } from "react";

export interface AuthCardProps {
  title: string;
  subtitle: string;
  children: ReactNode;
  footer: ReactNode;
}

export default function AuthCard({ title, subtitle, children, footer }: AuthCardProps) {
  return (
    <div className="card auth-card">
      <div className="auth-head">
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      {children}
      <div className="auth-footer">{footer}</div>
    </div>
  );
}
