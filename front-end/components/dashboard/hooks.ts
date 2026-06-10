"use client";

import { useEffect, useState } from "react";

/** Count-up animation that eases to `end` once mounted. */
export function useCount(end: number, decimals = 0, run = true, dur = 1200): string {
  const [v, setV] = useState(0);
  useEffect(() => {
    if (!run) {
      setV(end);
      return;
    }
    let raf = 0;
    let start: number | null = null;
    const tick = (t: number) => {
      if (start == null) start = t;
      const p = Math.min((t - start) / dur, 1);
      setV(end * (1 - Math.pow(1 - p, 3)));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [end, run, dur]);
  return v.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}
