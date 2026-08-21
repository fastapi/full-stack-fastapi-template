import { Text } from "@react-email/components"
import { Callout, Detail } from "../ui/Callout"
import { Heading } from "../ui/Heading"
import { Layout } from "../ui/Layout"

type TestEmailProps = {
  project_name: string
  email: string
}

export default function TestEmail({
  project_name = "{{ project_name }}",
  email = "{{ email }}",
}: TestEmailProps) {
  return (
    <Layout
      title={`${project_name} - Test email`}
      preview={`${project_name} email delivery is working`}
      project_name={project_name}
    >
      <Heading>Test email</Heading>
      <Text style={bodyTextStyle}>Hi,</Text>
      <Text style={bodyTextStyle}>
        This is a test email from {project_name}. If you're reading it, email
        delivery is configured correctly.
      </Text>
      <Callout>
        <Detail label="Sent to" value={email} />
      </Callout>
      <Text style={supportingTextStyle}>
        If you weren't expecting this email, you can safely ignore it.
      </Text>
    </Layout>
  )
}

const bodyTextStyle = {
  color: "#334155",
  fontSize: "15px",
  lineHeight: "26px",
  margin: "0 0 18px",
}

const supportingTextStyle = {
  color: "#64748b",
  fontSize: "14px",
  lineHeight: "23px",
  margin: "0 0 16px",
}
