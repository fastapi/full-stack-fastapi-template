import {
  Box,
  RangeSlider,
  RangeSliderTrack,
  RangeSliderFilledTrack,
  RangeSliderThumb,
  Text,
} from "@chakra-ui/react"

interface VideoRangeSliderProps {
  duration: number
  start: number
  end: number
  onChange: (start: number, end: number) => void
}

function formatTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

export function VideoRangeSlider({
  duration,
  start,
  end,
  onChange,
}: VideoRangeSliderProps) {
  return (
    <Box>
      <RangeSlider
        aria-label={['start', 'end']}
        min={0}
        max={duration}
        step={1}
        value={[start, end]}
        onChange={([newStart, newEnd]) => onChange(newStart, newEnd)}
        colorScheme="teal"
      >
        <RangeSliderTrack>
          <RangeSliderFilledTrack bg="teal.600" />
        </RangeSliderTrack>
        <RangeSliderThumb index={0}>
          <Box
            position="absolute"
            top="-25px"
            left="50%"
            transform="translateX(-50%)"
          >
            <Text fontSize="xs">{formatTime(start)}</Text>
          </Box>
        </RangeSliderThumb>
        <RangeSliderThumb index={1}>
          <Box
            position="absolute"
            top="-25px"
            left="50%"
            transform="translateX(-50%)"
          >
            <Text fontSize="xs">{formatTime(end)}</Text>
          </Box>
        </RangeSliderThumb>
      </RangeSlider>
      <Text fontSize="xs" color="gray.500" mt={1}>
        Total Duration: {formatTime(duration)}
      </Text>
    </Box>
  )
}
