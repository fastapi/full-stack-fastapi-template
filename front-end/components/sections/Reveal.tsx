"use client";

import { useRef, type MouseEventHandler, type ReactNode } from "react";
import { motion, useInView } from "framer-motion";

export interface RevealProps {
  children: ReactNode;
  delay?: number;
  className?: string;
  onMouseMove?: MouseEventHandler<HTMLDivElement>;
}

export default function Reveal({ children, delay = 0, className, onMouseMove }: RevealProps) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "0px 0px -8% 0px" });
  return (
    <motion.div
      ref={ref}
      className={className}
      onMouseMove={onMouseMove}
      initial={{ opacity: 0, y: 28 }}
      animate={inView ? { opacity: 1, y: 0 } : undefined}
      transition={{ duration: 0.7, delay: delay / 1000, ease: [0.2, 0.7, 0.2, 1] }}
    >
      {children}
    </motion.div>
  );
}
