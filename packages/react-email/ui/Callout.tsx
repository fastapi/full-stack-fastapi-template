import { Section, Text } from "@react-email/components"

type CalloutProps = React.PropsWithChildren

export const Callout = ({ children }: CalloutProps) => (
  <Section className="border-0 border-l-2 border-solid border-brand pl-5 my-7">
    {children}
  </Section>
)

type DetailProps = { label: string; value: string }

export const Detail = ({ label, value }: DetailProps) => (
  <Text className="m-0 my-3">
    <span className="block text-[11px] uppercase tracking-[0.08em] text-muted">
      {label}
    </span>
    <span className="block text-sm font-semibold break-all font-mono mt-1">
      {value}
    </span>
  </Text>
)
