import { Text } from "@react-email/components"
import { LinkButton } from "../ui/Button"
import { Heading } from "../ui/Heading"
import { Layout } from "../ui/Layout"
import { Link } from "../ui/Link"

type ResetPasswordProps = {
  project_name: string
  username: string
  link: string
  valid_hours: string
}

export default function ResetPassword({
  project_name = "{{ project_name }}",
  username = "{{ username }}",
  link = "{{ link }}",
  valid_hours = "{{ valid_hours }}",
}: ResetPasswordProps) {
  return (
    <Layout
      title={`${project_name} - Password recovery`}
      preview={`Reset your ${project_name} password`}
      project_name={project_name}
    >
      <Heading>Reset your password</Heading>
      <Text className="text-[15px] leading-7 text-body">Hi {username},</Text>
      <Text className="text-[15px] leading-7 text-body">
        We've received a request to reset the password for your {project_name}{" "}
        account. Choose a new one by clicking the button below:
      </Text>
      <LinkButton href={link}>Reset password</LinkButton>
      <Text className="text-sm leading-6 text-muted">
        Or copy and paste this link into your browser:
        <br />
        <Link href={link}>{link}</Link>
      </Text>
      <Text className="text-sm leading-6 text-muted">
        This link will expire in {valid_hours} hours.
      </Text>
      <Text className="text-sm leading-6 text-muted">
        If you didn't request a password recovery, you can safely ignore this
        email.
      </Text>
    </Layout>
  )
}
