import { Container, Heading, Stack } from "@chakra-ui/react"
import { useTheme } from "next-themes"
import type { FormEvent } from "react"

import { Radio, RadioGroup } from "@/components/ui/radio"

type Theme = "system" | "light" | "dark"

const Appearance = () => {
  const { theme, setTheme } = useTheme()

  const handleThemeChange = (event: FormEvent<HTMLDivElement>) => {
    const value = (event.target as HTMLInputElement).value
    setTheme(value as Theme)
  }

  return (
    <>
      <Container maxW="full">
        <Heading size="sm" py={4}>
          Appearance
        </Heading>

        <RadioGroup
          defaultValue={(theme as Theme) || "system"}
          name="theme"
          onChange={handleThemeChange}
        >
          <Stack>
            <Radio value="system">System</Radio>
            <Radio value="light">Light Mode</Radio>
            <Radio value="dark">Dark Mode</Radio>
          </Stack>
        </RadioGroup>
      </Container>
    </>
  )
}
export default Appearance
