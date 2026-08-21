import { Heading as BaseHeading } from "@react-email/components"

type HeadingProps = React.PropsWithChildren

export const Heading = ({ children }: HeadingProps) => (
  <BaseHeading as="h1" style={headingStyle}>
    {children}
  </BaseHeading>
)

const headingStyle = {
  color: "#17212b",
  fontSize: "26px",
  fontWeight: "700",
  letterSpacing: "-0.3px",
  lineHeight: "34px",
  margin: "0 0 20px",
}
