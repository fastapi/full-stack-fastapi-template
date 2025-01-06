import { Badge, Container, Heading, Stack } from "@chakra-ui/react"

import { Radio, RadioGroup } from "@/components/ui/radio"
import { useTheme } from "next-themes"

const Appearance = () => {
  const { theme, setTheme } = useTheme()

  return (
    <>
      <Container maxW="full">
        <Heading size="sm" py={4}>
          Appearance
        </Heading>
        <RadioGroup onValueChange={(e) => setTheme(e.value)} value={theme}>
          <Stack>
            <Radio value="system" colorScheme="teal">
              System
              <Badge ml="1" colorScheme="teal">
                Default
              </Badge>
            </Radio>
            <Radio value="light" colorScheme="teal">
              Light Mode
            </Radio>
            <Radio value="dark" colorScheme="teal">
              Dark Mode
            </Radio>
          </Stack>
        </RadioGroup>
      </Container>
    </>
  )
}
export default Appearance
