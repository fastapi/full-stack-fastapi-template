type LinkProps = React.PropsWithChildren & { href: string }

export const Link = ({ children, href }: LinkProps) => (
  <a href={href} className="text-brand-dark underline break-all">
    {children}
  </a>
)
