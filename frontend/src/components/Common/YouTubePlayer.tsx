import { useEffect, useRef } from "react"
import YouTube, { YouTubeEvent, YouTubePlayer as YTPlayer } from "react-youtube"
import { Box } from "@chakra-ui/react"

interface YouTubePlayerProps {
  videoId: string
  start?: number // Start time in seconds
  end?: number // End time in seconds
  onReady?: (duration: number) => void
  className?: string
}

export function YouTubePlayer({
  videoId,
  start,
  end,
  onReady,
  className,
}: YouTubePlayerProps) {
  const playerRef = useRef<YTPlayer>()
  const checkIntervalRef = useRef<ReturnType<typeof setInterval>>()

  useEffect(() => {
    return () => {
      if (checkIntervalRef.current) {
        clearInterval(checkIntervalRef.current)
      }
    }
  }, [])

  const handleReady = (event: YouTubeEvent) => {
    const player = event.target
    playerRef.current = player

    // Get video duration and notify parent
    const duration = player.getDuration()
    onReady?.(duration)

    if (start) {
      player.seekTo(start, true)
    }

    // Set up interval to check time and reset if needed
    if (end) {
      checkIntervalRef.current = setInterval(() => {
        const currentTime = player.getCurrentTime()
        if (currentTime >= end) {
          player.seekTo(start || 0, true)
          player.pauseVideo()
        }
      }, 1000)
    }
  }

  const handleStateChange = (event: YouTubeEvent) => {
    const player = event.target
    // If video starts playing and we have a start time, ensure we're at the right point
    if (event.data === YouTube.PlayerState.PLAYING && start) {
      const currentTime = player.getCurrentTime()
      if (currentTime < start) {
        player.seekTo(start, true)
      }
    }
  }

  return (
    <Box className={className} width="100%" position="relative" paddingTop="56.25%">
      <Box position="absolute" top="0" left="0" width="100%" height="100%">
        <YouTube
          videoId={videoId}
          opts={{
            width: "100%",
            height: "100%",
            playerVars: {
              autoplay: 0,
              modestbranding: 1,
              rel: 0,
              start: start,
            },
          }}
          onReady={handleReady}
          onStateChange={handleStateChange}
          style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
        />
      </Box>
    </Box>
  )
}
