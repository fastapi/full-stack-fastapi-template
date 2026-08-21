import { Section, Text } from "@react-email/components"

type CalloutProps = React.PropsWithChildren

export const Callout = ({ children }: CalloutProps) => (
  <Section style={calloutStyle}>{children}</Section>
)

type DetailProps = { label: string; value: string }

export const Detail = ({ label, value }: DetailProps) => (
  <Text style={detailStyle}>
    <span style={labelStyle}>{label}</span>
    <br />
    <span style={valueStyle}>{value}</span>
  </Text>
)

const calloutStyle = {
  backgroundColor: "#f2f8f7",
  borderLeft: "3px solid #00897b",
  margin: "24px 0 28px",
  padding: "6px 18px",
}

const detailStyle = {
  margin: "12px 0",
}

const labelStyle = {
  color: "#64748b",
  fontSize: "11px",
  fontWeight: "700",
  letterSpacing: "1px",
  lineHeight: "16px",
  textTransform: "uppercase" as const,
}

const valueStyle = {
  color: "#1e293b",
  fontFamily: 'Consolas, "Courier New", monospace',
  fontSize: "14px",
  fontWeight: "700",
  lineHeight: "22px",
  wordBreak: "break-all" as const,
}
