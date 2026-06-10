"use client";

import { useEffect, useRef, useState } from "react";
import { useInView } from "framer-motion";
import { useTranslations } from "next-intl";

function Counter({
  end,
  decimals = 0,
  suffix = "",
  duration = 1600,
}: {
  end: number;
  decimals?: number;
  suffix?: string;
  duration?: number;
}) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, amount: 0.5 });
  const [val, setVal] = useState(0);

  useEffect(() => {
    if (!inView) return;
    let raf = 0;
    let start: number | null = null;
    const tick = (t: number) => {
      if (start == null) start = t;
      const p = Math.min((t - start) / duration, 1);
      setVal(end * (1 - Math.pow(1 - p, 3)));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [inView, end, duration]);

  const formatted = val.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  return (
    <span ref={ref}>
      {formatted}
      <span className="u">{suffix}</span>
    </span>
  );
}

export default function Stats() {
  const t = useTranslations("landing.stats");
  return (
    <div className="stats-wrap" id="stats">
      <div className="stats">
        <div className="stat">
          <div className="num">
            <Counter end={10000} suffix="+" />
          </div>
          <div className="lbl">{t("documents")}</div>
        </div>
        <div className="stat">
          <div className="num">
            <Counter end={99.2} decimals={1} suffix="%" />
          </div>
          <div className="lbl">{t("accuracy")}</div>
        </div>
        <div className="stat">
          <div className="num am">
            <span className="u">&lt;</span>
            <Counter end={3} suffix="s" />
          </div>
          <div className="lbl">{t("parseTime")}</div>
        </div>
        <div className="stat">
          <div className="num">
            <Counter end={1.4} decimals={1} suffix="M" />
          </div>
          <div className="lbl">{t("cells")}</div>
        </div>
      </div>
    </div>
  );
}
