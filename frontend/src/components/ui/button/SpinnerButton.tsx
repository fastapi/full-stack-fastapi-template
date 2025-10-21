import React, { ReactNode } from "react";
import Button, { ButtonProps } from "./Button";
import Spinner from "@/components/ui/spinner";

interface SpinnerButtonProps {
  children: ReactNode; // Button text or content
  size?: "sm" | "md"; // Button size
  variant?: "primary" | "outline"; // Button variant
  startIcon?: ReactNode; // Icon before the text
  endIcon?: ReactNode; // Icon after the text
  onClick?: () => void; // Click handler
  disabled?: boolean; // Disabled state
  className?: string; // Disabled state
  loading?: boolean; // Loading state
}

const SpinnerButton: React.FC<SpinnerButtonProps> = ({
  children,
  size = "md",
  variant = "primary",
  startIcon,
  endIcon,
  onClick,
  className = "",
  disabled = false,
  loading = false,
    ...props
}) => {
  return (
    <Button
      {...props}
      startIcon={loading ? <Spinner /> : startIcon}
      disabled={disabled || loading}
    >
      {children}
    </Button>
  );
};

export default SpinnerButton;
