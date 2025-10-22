import { Box, Button, Flex, Image, Text } from "@chakra-ui/react"

import { useColorModeValue } from "@/components/ui/color-mode"

type MarketKey = "home" | "draw" | "away"
type OverUnderKey = "over" | "under"

interface BookInfo {
  name: string
  logoUrl?: string
}

interface Market {
  value: string
  book?: BookInfo
}

export interface OddsCardProps {
  homeTeam: string
  awayTeam: string
  marketLabel?: string
  home: Market
  draw: Market
  away: Market
  onSelect?: (market: MarketKey) => void
}

export interface OverUnderOddsCardProps {
  homeTeam: string
  awayTeam: string
  marketLabel?: string
  line?: string
  over: Market
  under: Market
  onSelect?: (market: OverUnderKey) => void
}

interface OddsPillProps extends Market {
  label: string
  onSelect?: () => void
}

function BookBadge({ logoUrl, name }: BookInfo) {
  const badgeBg = useColorModeValue("gray.100", "gray.700")
  const badgeColor = useColorModeValue("gray.600", "gray.300")

  return (
    <Flex
      mt={2}
      align="center"
      gap={2}
      bg={badgeBg}
      color={badgeColor}
      px={3}
      py={1}
      borderRadius="lg"
      fontSize="sm"
      maxW="100%"
    >
      {logoUrl ? (
        <Image src={logoUrl} alt={name} h={4} w="auto" objectFit="contain" />
      ) : (
        <Text fontWeight="medium">{name}</Text>
      )}
    </Flex>
  )
}

function OddsPill({ value, book, label, onSelect }: OddsPillProps) {
  const borderColor = useColorModeValue("gray.200", "gray.600")
  const hoverBg = useColorModeValue("gray.100", "gray.700")
  const textColor = useColorModeValue("teal.600", "teal.200")

  return (
    <Button
      onClick={onSelect}
      variant="outline"
      borderRadius="xl"
      borderColor={borderColor}
      minW="140px"
      py={50}
      px={4}
      display="flex"
      flexDir="column"
      alignItems="center"
      justifyContent="center"
      gap={2}
      transition="all 0.2s ease-in-out"
      _hover={{ transform: "translateY(-3px)", bg: hoverBg, shadow: "md" }}
    >
      <Text fontSize="2xl" fontWeight="semibold" letterSpacing="tight" color={textColor}>
        {value}
      </Text>
      {book ? <BookBadge {...book} /> : <Text fontSize="xs">{label}</Text>}
    </Button>
  )
}

function MarketColumn({
  title,
  market,
  onSelect,
}: {
  title: string
  market: Market
  onSelect?: () => void
}) {
  return (
    <Flex direction="column" align="center" gap={2}>
      <Text fontSize="xs" fontWeight="semibold" color="fg.muted" letterSpacing="wide">
        {title}
      </Text>
      <OddsPill label={title} value={market.value} book={market.book} onSelect={onSelect} />
    </Flex>
  )
}

export function OddsCard({
  homeTeam,
  awayTeam,
  marketLabel = "Moneyline",
  home,
  draw,
  away,
  onSelect,
}: OddsCardProps) {
  const wrapperBg = useColorModeValue("gray.50", "gray.800")
  const borderColor = useColorModeValue("gray.200", "gray.600")

  return (
    <Box
      borderWidth="1px"
      borderRadius="2xl"
      borderColor={borderColor}
      bg={wrapperBg}
      px={10}
      py={8}
      w="full"
      maxW="5xl"
    >
      <Flex
        direction={{ base: "column", sm: "row" }}
        justify="space-between"
        align={{ base: "stretch", sm: "center" }}
        gap={6}
      >
        <Flex
          direction={{ base: "column", md: "row" }}
          align="center"
          justify="center"
          gap={4}
          minW={{ base: "full", md: "sm" }}
        >
          <Text
            fontSize="2xl"
            fontWeight="semibold"
            textAlign={{ base: "center", md: "right" }}
            lineHeight="short"
          >
            {homeTeam}
          </Text>
          <Box
            px={3}
            py={1}
            borderRadius="full"
            bg="teal.600"
            color="white"
            fontWeight="bold"
            fontSize="sm"
          >
            VS
          </Box>
          <Text
            fontSize="2xl"
            fontWeight="semibold"
            textAlign={{ base: "center", md: "left" }}
            lineHeight="short"
          >
            {awayTeam}
          </Text>
        </Flex>
        <Flex direction="column" align="center" justify="center" w="full" maxW="3xl" gap={4}>
          <Text fontSize="sm" fontWeight="medium" color="teal.600" textTransform="uppercase">
            {marketLabel}
          </Text>
          <Flex justify="space-evenly" align="center" gap={10} w="full">
            <MarketColumn title="HOME" market={home} onSelect={() => onSelect?.("home")} />
            <MarketColumn title="DRAW" market={draw} onSelect={() => onSelect?.("draw")} />
            <MarketColumn title="AWAY" market={away} onSelect={() => onSelect?.("away")} />
          </Flex>
        </Flex>
      </Flex>
    </Box>
  )
}

export function OverUnderOddsCard({
  homeTeam,
  awayTeam,
  marketLabel = "Total",
  line,
  over,
  under,
  onSelect,
}: OverUnderOddsCardProps) {
  const wrapperBg = useColorModeValue("gray.50", "gray.800")
  const borderColor = useColorModeValue("gray.200", "gray.600")

  return (
    <Box
      borderWidth="1px"
      borderRadius="2xl"
      borderColor={borderColor}
      bg={wrapperBg}
      px={10}
      py={50}
      w="full"
      maxW="5xl"
    >
      <Flex
        direction={{ base: "column", sm: "row" }}
        justify="space-between"
        align={{ base: "stretch", sm: "center" }}
        gap={6}
      >
        <Flex
          direction={{ base: "column", md: "row" }}
          align="center"
          justify="center"
          gap={4}
          minW={{ base: "full", md: "sm" }}
        >
          <Text
            fontSize="2xl"
            fontWeight="semibold"
            textAlign={{ base: "center", md: "right" }}
            lineHeight="short"
          >
            {homeTeam}
          </Text>
          <Box
            px={3}
            py={1}
            borderRadius="full"
            bg="teal.600"
            color="white"
            fontWeight="bold"
            fontSize="sm"
          >
            VS
          </Box>
          <Text
            fontSize="2xl"
            fontWeight="semibold"
            textAlign={{ base: "center", md: "left" }}
            lineHeight="short"
          >
            {awayTeam}
          </Text>
        </Flex>
        <Flex direction="column" align="center" justify="center" w="full" maxW="2xl" gap={4}>
          <Text fontSize="sm" fontWeight="medium" color="teal.600" textTransform="uppercase">
            {marketLabel}
          </Text>
          {line && (
            <Text fontSize="3xl" fontWeight="semibold" color="fg.default">
              {line}
            </Text>
          )}
          <Flex justify="space-evenly" align="center" gap={10} w="full">
            <MarketColumn title="OVER" market={over} onSelect={() => onSelect?.("over")} />
            <MarketColumn title="UNDER" market={under} onSelect={() => onSelect?.("under")} />
          </Flex>
        </Flex>
      </Flex>
    </Box>
  )
}

export default OddsCard
