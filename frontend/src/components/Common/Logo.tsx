import { Link } from "@tanstack/react-router"

import { cn } from "@/lib/utils"
import logo from "/assets/images/forge_ai_logo.png"

interface LogoProps {
  variant?: "full" | "icon" | "responsive"
  className?: string
  asLink?: boolean
}

export function Logo({
  variant = "full",
  className,
  asLink = true,
}: LogoProps) {
  const content =
    variant === "responsive" ? (
      <>
        <img
          src={logo}
          alt="Forge AI"
          className={cn(
            "h-6 w-auto group-data-[collapsible=icon]:hidden",
            className,
          )}
        />
        <span
          className={cn(
            "hidden size-5 overflow-hidden rounded-sm group-data-[collapsible=icon]:inline-flex",
          )}
        >
          <img
            src={logo}
            alt="Forge AI"
            className={cn("h-full w-full object-cover object-left", className)}
          />
        </span>
      </>
    ) : variant === "full" ? (
      <img src={logo} alt="Forge AI" className={cn("h-6 w-auto", className)} />
    ) : (
      <span className={cn("inline-flex size-5 overflow-hidden rounded-sm")}>
        <img
          src={logo}
          alt="Forge AI"
          className={cn("h-full w-full object-cover object-left", className)}
        />
      </span>
    )

  if (!asLink) {
    return content
  }

  return <Link to="/">{content}</Link>
}
