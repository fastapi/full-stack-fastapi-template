import React, { ReactNode } from "react";
import Button from "./Button";
import Spinner from "@/components/ui/spinner";

interface SpinnerButtonProps {
  variant?: "primary" | "secondary" | "tertiary"; // Button variant
  size?: "sm" | "md" | undefined;
  children: ReactNode; // Button text or content
  startIcon?: ReactNode; // Icon before the text
  onClick?: () => void; // Click handler
  disabled?: boolean; // Disabled state
  className?: string; // Disabled state
  loading?: boolean; // Loading state
}

const SpinnerButton: React.FC<SpinnerButtonProps> = ({
  children,
  startIcon,
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
        onClick={onClick}
        className={className}
        variant="primary"


    >
      {children}
    </Button>
  );
};

export default SpinnerButton;
