import { Text } from "@react-email/components"
import { LinkButton } from "../ui/Button"
import { Callout, Detail } from "../ui/Callout"
import { Heading } from "../ui/Heading"
import { Layout } from "../ui/Layout"
import { Link } from "../ui/Link"

type NewAccountProps = {
  project_name: string
  username: string
  password: string
  link: string
}

export default function NewAccount({
  project_name = "{{ project_name }}",
  username = "{{ username }}",
  password = "{{ password }}",
  link = "{{ link }}",
}: NewAccountProps) {
  return (
    <Layout
      title={`${project_name} - New account`}
      preview={`Your ${project_name} account is ready`}
      project_name={project_name}
    >
      <Heading>Welcome to {project_name}!</Heading>
      <Text style={bodyTextStyle}>Hi,</Text>
      <Text style={bodyTextStyle}>
        Your account has been successfully created and is ready to use. These
        are your credentials:
      </Text>
      <Callout>
        <Detail label="Username" value={username} />
        <Detail label="Password" value={password} />
      </Callout>
      <Text style={bodyTextStyle}>
        Get started by signing in to your dashboard:
      </Text>
      <LinkButton href={link}>Go to Dashboard</LinkButton>
      <Text style={supportingTextStyle}>
        Or copy and paste this link into your browser:
        <br />
        <Link href={link}>{link}</Link>
      </Text>
      <Text style={supportingTextStyle}>
        For security reasons, change your password after your first sign in.
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
