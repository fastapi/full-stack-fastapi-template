import { Heading as BaseHeading } from "@react-email/components"

type HeadingProps = React.PropsWithChildren

export const Heading = ({ children }: HeadingProps) => (
  <BaseHeading
    as="h1"
    className="text-2xl leading-8 font-semibold tracking-[-0.02em] text-body m-0 mb-5"
  >
    {children}
  </BaseHeading>
)
