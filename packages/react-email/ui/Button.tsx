import { Button } from "@react-email/components"

type ButtonProps = React.PropsWithChildren & { href: string }

export const LinkButton = ({ children, href }: ButtonProps) => (
  <Button href={href} style={buttonStyle}>
    {children}
  </Button>
)

const buttonStyle = {
  backgroundColor: "#00796b",
  borderRadius: "6px",
  color: "#ffffff",
  display: "inline-block",
  fontSize: "14px",
  fontWeight: "700",
  lineHeight: "20px",
  margin: "8px 0 28px",
  padding: "13px 28px",
  textAlign: "center" as const,
  textDecoration: "none",
}
