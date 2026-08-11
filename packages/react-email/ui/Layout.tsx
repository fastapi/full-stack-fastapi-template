import {
  Body,
  Head,
  Hr,
  Html,
  Preview,
  Section,
  Tailwind,
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
    <Tailwind
      config={{
        theme: {
          extend: {
            colors: {
              surface: "#ffffff",
              body: "#1e293b",
              muted: "#64748b",
              rule: "#e2e8f0",
              brand: {
                DEFAULT: "#009688",
                dark: "#00695c",
              },
            },
            fontFamily: {
              sans: [
                "-apple-system",
                "BlinkMacSystemFont",
                '"Segoe UI"',
                "Roboto",
                "Oxygen",
                "Ubuntu",
                "Cantarell",
                '"Fira Sans"',
                '"Droid Sans"',
                '"Helvetica Neue"',
                "sans-serif",
              ],
            },
          },
        },
      }}
    >
      <Html lang="en" dir="ltr">
        <Head>
          <title>{title}</title>
          <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
          />
        </Head>
        {preview ? <Preview>{preview}</Preview> : null}
        <Body className="bg-surface font-sans text-body max-w-[560px] w-full mx-auto my-0 py-12 px-6">
          <Section>
            <Hr className="border-0 border-t-2 border-solid border-brand w-8 m-0" />
            <Text className="text-body text-[13px] font-semibold uppercase tracking-[0.1em] mt-4 mb-9">
              {project_name}
            </Text>
          </Section>
          <Section>{children}</Section>
          <Hr className="border-0 border-t border-solid border-rule mt-10 mb-5" />
          <Section>
            <Text className="text-xs leading-5 text-muted m-0">
              © {new Date().getFullYear()} {project_name}. All rights reserved.
            </Text>
          </Section>
        </Body>
      </Html>
    </Tailwind>
  )
}
