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
      <Text className="text-[15px] leading-7 text-body">Hi,</Text>
      <Text className="text-[15px] leading-7 text-body">
        Your account has been successfully created and is ready to use. These
        are your credentials:
      </Text>
      <Callout>
        <Detail label="Username" value={username} />
        <Detail label="Password" value={password} />
      </Callout>
      <Text className="text-[15px] leading-7 text-body">
        Get started by signing in to your dashboard:
      </Text>
      <LinkButton href={link}>Go to Dashboard</LinkButton>
      <Text className="text-sm leading-6 text-muted">
        Or copy and paste this link into your browser:
        <br />
        <Link href={link}>{link}</Link>
      </Text>
      <Text className="text-sm leading-6 text-muted">
        For security reasons, change your password after your first sign in.
      </Text>
    </Layout>
  )
}
