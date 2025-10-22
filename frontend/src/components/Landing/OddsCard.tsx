import { Box, Button, Flex, Image, Text } from "@chakra-ui/react"

import { useColorModeValue } from "@/components/ui/color-mode"

type MarketKey = "home" | "draw" | "away"

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
      px={2}
      py={1}
      borderRadius="md"
      fontSize="xs"
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
  const hoverBg = useColorModeValue("gray.50", "gray.700")

  return (
    <Button
      onClick={onSelect}
      variant="outline"
      borderRadius="xl"
      borderColor={borderColor}
      w="100px"
      py={3}
      px={3}
      display="flex"
      flexDir="column"
      alignItems="center"
      transition="all 0.2s ease-in-out"
      _hover={{ transform: "translateY(-3px)", bg: hoverBg, shadow: "md" }}
    >
      <Text fontSize="lg" fontWeight="semibold" letterSpacing="tight" color="fg.default">
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
      p={6}
      w="full"
      maxW="3xl"
    >
      <Flex
        direction={{ base: "column", sm: "row" }}
        justify="space-between"
        align={{ base: "stretch", sm: "center" }}
        gap={6}
      >
        <Box>
          <Text fontSize="xl" fontWeight="semibold" lineHeight="shorter">
            {homeTeam}
          </Text>
          <Text fontSize="xl" fontWeight="semibold" lineHeight="shorter">
            {awayTeam}
          </Text>
          <Text mt={3} fontSize="sm" fontWeight="medium" color="teal.600">
            {marketLabel}
          </Text>
        </Box>

        <Flex
          justify="space-between"
          gap={4}
          w="full"
          maxW={{ base: "full", sm: "auto" }}
        >
          <MarketColumn
            title="HOME"
            market={home}
            onSelect={() => onSelect?.("home")}
          />
          <MarketColumn
            title="DRAW"
            market={draw}
            onSelect={() => onSelect?.("draw")}
          />
          <MarketColumn
            title="AWAY"
            market={away}
            onSelect={() => onSelect?.("away")}
          />
        </Flex>
      </Flex>
    </Box>
  )
}

export default OddsCard
