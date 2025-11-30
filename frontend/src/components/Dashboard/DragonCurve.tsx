import { useEffect, useRef, useState } from "react"
import { Box, Input, Text, VStack } from "@chakra-ui/react"
import LSystem from "lindenmayer"

/**
 * DragonCurve Component
 *
 * Renders an animated dragon curve fractal using L-systems.
 * The dragon curve is created using the Lindenmayer system with turtle graphics.
 *
 * L-System Rules:
 * - Axiom: FX
 * - X → X+YF+
 * - Y → -FX-Y
 * - F → F (draw forward)
 * - + → turn right 90°
 * - - → turn left 90°
 *
 * Animation loops through iterations 0-12, showing the fractal's evolution.
 */
export default function DragonCurve() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [iteration, setIteration] = useState(0)
  const [maxIterations, setMaxIterations] = useState(12)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas size
    const size = Math.min(window.innerWidth - 40, 600)
    canvas.width = size
    canvas.height = size

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Create dragon curve L-system
    const dragonCurve = new LSystem({
      axiom: "FX",
      productions: {
        X: "X+YF+",
        Y: "-FX-Y",
      },
    })

    // Generate the current iteration
    dragonCurve.iterate(iteration)
    const result = dragonCurve.getString()

    // Turtle graphics rendering
    drawDragonCurve(ctx, result, canvas.width, canvas.height, iteration)

    // Animation loop - advance to next iteration
    const timer = setTimeout(() => {
      setIteration((prev) => (prev + 1) % (maxIterations + 1))
    }, 800) // 800ms between iterations

    return () => clearTimeout(timer)
  }, [iteration, maxIterations])

  return (
    <VStack gap={4} align="stretch">
      <Box p={4} bg="gray.50" borderRadius="md" boxShadow="sm">
        <Text mb={2} fontWeight="medium">
          Max Iterations
        </Text>
        <Input
          type="number"
          value={maxIterations}
          onChange={(e) => {
            const val = parseInt(e.target.value)
            if (val >= 1 && val <= 15) {
              setMaxIterations(val)
            }
          }}
          min={1}
          max={15}
          step={1}
          bg="white"
        />
      </Box>

      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        p={4}
        bg="gray.50"
        borderRadius="md"
        boxShadow="sm"
      >
        <canvas
          ref={canvasRef}
          style={{
            border: "1px solid #e2e8f0",
            borderRadius: "4px",
            backgroundColor: "white",
          }}
        />
      </Box>
    </VStack>
  )
}

/**
 * Draw dragon curve using turtle graphics
 *
 * Interprets the L-system string and draws it on canvas using turtle graphics.
 * The turtle starts at a calculated position and draws based on the commands:
 * - F: move forward and draw
 * - +: turn right 90°
 * - -: turn left 90°
 * - X, Y: no-op (structure only)
 *
 * @param ctx - Canvas 2D context
 * @param commands - L-system result string
 * @param width - Canvas width
 * @param height - Canvas height
 * @param iteration - Current iteration number (affects line length)
 */
function drawDragonCurve(
  ctx: CanvasRenderingContext2D,
  commands: string,
  width: number,
  height: number,
  iteration: number,
) {
  // Calculate line length based on iteration
  // Smaller lengths for higher iterations to fit the curve
  const baseLength = Math.min(width, height) / 3
  const length = baseLength / Math.pow(1.4, iteration)

  // Starting position (centered, offset down)
  let x = width / 2.5
  let y = height / 2

  // Turtle state
  let angle = 0 // Degrees
  const turnAngle = 90 // 90° turns

  // Style
  ctx.strokeStyle = `hsl(${(iteration * 30) % 360}, 70%, 50%)` // Color changes with iteration
  ctx.lineWidth = 2
  ctx.lineCap = "round"
  ctx.lineJoin = "round"

  ctx.beginPath()
  ctx.moveTo(x, y)

  // Process each command
  for (const command of commands) {
    switch (command) {
      case "F":
        // Move forward and draw
        const radians = (angle * Math.PI) / 180
        x += length * Math.cos(radians)
        y += length * Math.sin(radians)
        ctx.lineTo(x, y)
        break

      case "+":
        // Turn right
        angle += turnAngle
        break

      case "-":
        // Turn left
        angle -= turnAngle
        break

      case "X":
      case "Y":
        // Structure symbols - no action
        break
    }
  }

  ctx.stroke()
}
