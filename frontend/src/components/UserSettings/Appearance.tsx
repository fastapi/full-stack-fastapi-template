import {  Heading, Stack } from "@chakra-ui/react"
import { useTheme } from "next-themes"

import { Radio, RadioGroup } from "@/components/ui/radio"

const Appearance = () => {
  const { theme, setTheme } = useTheme()

  return (
    <>
      <Box maxW="7xl" mx="auto" px={6}>
        <Heading size="sm" py={4}>
          Appearance
        </Heading>

        <RadioGroup
          onValueChange={(e) => setTheme(e.value)}
          value={theme}
          colorPalette="teal"
        >
          <Stack>
            <Radio value="system">System</Radio>
            <Radio value="light">Light Mode</Radio>
            <Radio value="dark">Dark Mode</Radio>
          </Stack>
        </RadioGroup>
      </Box>
    </>
  )
}
export default Appearance
