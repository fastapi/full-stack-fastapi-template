import { Button } from "@react-email/components"

type ButtonProps = React.PropsWithChildren & { href: string }

export const LinkButton = ({ children, href }: ButtonProps) => (
  <Button
    href={href}
    className="bg-brand text-white rounded-md font-semibold text-sm mt-2 mb-7 inline-block text-center no-underline px-7 py-3.5"
  >
    {children}
  </Button>
)
