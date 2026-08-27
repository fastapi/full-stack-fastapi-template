import {
  Body,
  Column,
  Container,
  Head,
  Hr,
  Html,
  Preview,
  Row,
  Section,
  Text,
} from "@react-email/components"

type LayoutProps = React.PropsWithChildren & {
  title: string
  project_name: string
  preview?: string
}

export const Layout = ({
  project_name,
  title,
  preview,
  children,
}: LayoutProps) => {
  return (
    <Html lang="en" dir="ltr">
      <Head>
        <title>{title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </Head>
      {preview ? <Preview>{preview}</Preview> : null}
      <Body style={bodyStyle}>
        <Container style={containerStyle}>
          <Row>
            <Column style={contentStyle}>
              <Section>
                <Hr style={brandRuleStyle} />
                <Text style={brandStyle}>{project_name}</Text>
              </Section>
              <Section>{children}</Section>
              <Hr style={footerRuleStyle} />
              <Section>
                <Text style={footerStyle}>
                  © {new Date().getFullYear()} {project_name}. All rights
                  reserved.
                </Text>
              </Section>
            </Column>
          </Row>
        </Container>
      </Body>
    </Html>
  )
}

const fontFamily =
  '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'

const bodyStyle = {
  backgroundColor: "#f4f7f6",
  color: "#1e293b",
  fontFamily,
  margin: "0",
  padding: "32px 12px",
}

const containerStyle = {
  backgroundColor: "#ffffff",
  border: "1px solid #dce7e5",
  borderRadius: "8px",
  boxSizing: "border-box" as const,
  margin: "0 auto",
  maxWidth: "560px",
  width: "100%",
}

const contentStyle = {
  padding: "40px 36px 32px",
}

const brandRuleStyle = {
  border: "0",
  borderTop: "3px solid #00897b",
  margin: "0 0 16px",
  width: "32px",
}

const brandStyle = {
  color: "#334155",
  fontSize: "13px",
  fontWeight: "700",
  letterSpacing: "1px",
  lineHeight: "20px",
  margin: "0 0 32px",
  textTransform: "uppercase" as const,
}

const footerRuleStyle = {
  border: "0",
  borderTop: "1px solid #dce7e5",
  margin: "36px 0 18px",
  width: "100%",
}

const footerStyle = {
  color: "#64748b",
  fontSize: "12px",
  lineHeight: "20px",
  margin: "0",
}
