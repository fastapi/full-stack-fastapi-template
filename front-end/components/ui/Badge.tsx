import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export type BadgeTone = "cyan" | "amber" | "bad" | "neutral";

export interface BadgeProps {
  tone?: BadgeTone;
  children: ReactNode;
  className?: string;
}

const TONE: Record<BadgeTone, string> = {
  cyan: "text-cyan bg-cyan-dim border-cyan-dim",
  amber: "text-amber bg-amber-dim border-amber-dim",
  bad: "text-bad bg-bad-dim border-bad-dim",
  neutral: "text-fg-dim bg-surface-2 border-line",
};

export default function Badge({ tone = "neutral", children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 font-mono text-[10.5px] uppercase tracking-[0.08em]",
        TONE[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
