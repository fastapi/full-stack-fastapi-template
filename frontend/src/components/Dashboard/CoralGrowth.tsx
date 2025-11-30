import { useEffect, useRef, useState } from "react"
import { Box, Input, Text, VStack } from "@chakra-ui/react"

/**
 * CoralGrowth Component
 *
 * Renders an animated coral structure using parametric L-systems.
 * Coral grows with variable thickness, branching, and organic angles.
 *
 * L-System Rules:
 * - Axiom: F(1.0)
 * - F(t) → F(t*0.85)[+(30)F(t*0.65)][-(35)F(t*0.65)]F(t*0.9)
 * - (t) = thickness parameter
 * - [ = push state (save position, angle, thickness)
 * - ] = pop state (restore to saved state)
 * - + = turn right
 * - - = turn left
 * - F(t) = draw forward with thickness t
 *
 * Animation loops through iterations 0-6, showing coral growth evolution.
 */
export default function CoralGrowth() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [iteration, setIteration] = useState(0)
  const [maxIterations, setMaxIterations] = useState(6)
  const [seed, setSeed] = useState(12345)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas size
    const size = Math.min(window.innerWidth - 40, 800)
    canvas.width = size
    canvas.height = size

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Generate coral L-system string with stochastic parametric rules
    const coralString = generateCoralLSystem(iteration, seed)

    // Render coral with turtle graphics
    drawCoral(ctx, coralString, canvas.width, canvas.height, iteration)

    // Animation loop - advance to next iteration
    const timer = setTimeout(() => {
      setIteration((prev) => (prev + 1) % (maxIterations + 1))
    }, 1200) // 1200ms between iterations (slower for coral)

    return () => clearTimeout(timer)
  }, [iteration, maxIterations, seed])

  return (
    <VStack gap={4} align="stretch">
      <Box p={4} bg="gray.50" borderRadius="md" boxShadow="sm">
        <Text mb={2} fontWeight="medium">
          Growth Iterations
        </Text>
        <Input
          type="number"
          value={maxIterations}
          onChange={(e) => {
            const val = parseInt(e.target.value)
            if (val >= 1 && val <= 8) {
              setMaxIterations(val)
            }
          }}
          min={1}
          max={8}
          step={1}
          bg="white"
        />
      </Box>

      <Box p={4} bg="gray.50" borderRadius="md" boxShadow="sm">
        <Text mb={2} fontWeight="medium">
          Random Seed
        </Text>
        <Input
          type="number"
          value={seed}
          onChange={(e) => {
            const val = parseInt(e.target.value)
            if (!isNaN(val)) {
              setSeed(val)
            }
          }}
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
            backgroundColor: "#001a33", // Deep ocean blue background
          }}
        />
      </Box>
    </VStack>
  )
}


/**
 * Generate coral L-system string with parametric thickness using stochastic rules
 *
 * Uses manual string rewriting with multiple production rules and axioms selected
 * probabilistically based on seed for organic, varied growth patterns.
 *
 * Axioms (seed-selected):
 * - 25%: F(1.0) - Traditional central trunk
 * - 25%: [-(45)F(0.8)][+(45)F(0.8)] - Branch from base, no trunk
 * - 25%: [-(60)F(0.9)]F(0.4)[+(60)F(0.9)] - Tiny center with big side branches
 * - 25%: [-(30)F(0.85)][F(0.6)][+(30)F(0.85)] - Three-way split from base
 *
 * Production Rules (probabilistic):
 * - 60%: Normal branching - F(t*0.85)[+(30)F(t*0.65)][-(35)F(t*0.65)]F(t*0.9)
 * - 25%: Dominant straight - F(t*0.95)F(t*0.92)
 * - 10%: Asymmetric branching - F(t*0.85)[+(30)F(t*0.8)][-(35)F(t*0.5)]F(t*0.9)
 * - 5%: Minimal growth - F(t*0.9)
 *
 * @param iterations - Number of growth iterations
 * @param seed - Random seed for deterministic axiom and rule selection
 * @returns L-system command string with thickness annotations
 */
function generateCoralLSystem(iterations: number, seed: number): string {
  // Select axiom based on seed for varied starting patterns
  const axiomSelector = seededRandom(seed, 1)
  let current: string

  if (axiomSelector < 0.25) {
    // Axiom A (25%): Traditional central trunk
    current = "F(1.0)"
  } else if (axiomSelector < 0.5) {
    // Axiom B (25%): Branch from base, no central trunk
    current = "[-(45)F(0.8)][+(45)F(0.8)]"
  } else if (axiomSelector < 0.75) {
    // Axiom C (25%): Tiny stub center with big side branches
    current = "[-(60)F(0.9)]F(0.4)[+(60)F(0.9)]"
  } else {
    // Axiom D (25%): Three-way split from base
    current = "[-(30)F(0.85)][F(0.6)][+(30)F(0.85)]"
  }

  // Apply production rule for each iteration
  let growthIndex = 0 // Track position for seeded randomness

  for (let i = 0; i < iterations; i++) {
    let next = ""
    let j = 0

    while (j < current.length) {
      if (current[j] === "F" && current[j + 1] === "(") {
        // Extract thickness value
        const closeIdx = current.indexOf(")", j)
        const thickness = parseFloat(current.substring(j + 2, closeIdx))

        // Use seeded random to select production rule
        growthIndex++
        const randomValue = seededRandom(seed, growthIndex)

        // Apply stochastic production rules
        if (randomValue < 0.6) {
          // Rule A (60%): Normal balanced branching
          next += `F(${thickness * 0.85})[+(30)F(${thickness * 0.65})][-(35)F(${thickness * 0.65})]F(${thickness * 0.9})`
        } else if (randomValue < 0.85) {
          // Rule B (25%): Dominant straight growth
          next += `F(${thickness * 0.95})F(${thickness * 0.92})`
        } else if (randomValue < 0.95) {
          // Rule C (10%): Asymmetric branching (left branch dominant)
          next += `F(${thickness * 0.85})[+(30)F(${thickness * 0.8})][-(35)F(${thickness * 0.5})]F(${thickness * 0.9})`
        } else {
          // Rule D (5%): Minimal growth
          next += `F(${thickness * 0.9})`
        }

        j = closeIdx + 1
      } else {
        // Copy other symbols as-is
        next += current[j]
        j++
      }
    }

    current = next
  }

  return current
}

/**
 * Simple seeded random number generator
 *
 * @param seed - Seed value
 * @param index - Index/position value to vary the output
 * @returns Random number between 0 and 1
 */
function seededRandom(seed: number, index: number): number {
  return Math.abs(Math.sin(seed * index * 9999))
}

/**
 * Turtle state for drawing coral
 */
interface TurtleState {
  x: number
  y: number
  angle: number
  thickness: number
}

/**
 * Draw coral structure using turtle graphics with state stack
 *
 * Interprets the L-system string and draws coral with:
 * - Variable thickness based on parameters
 * - Branching via state stack ([ and ])
 * - Asymmetric angles for organic appearance
 * - Color variation based on depth
 *
 * @param ctx - Canvas 2D context
 * @param commands - L-system result string with parameters
 * @param width - Canvas width
 * @param height - Canvas height
 * @param iteration - Current iteration (affects overall scale)
 */
function drawCoral(
  ctx: CanvasRenderingContext2D,
  commands: string,
  width: number,
  height: number,
  iteration: number,
) {
  // Calculate base line length
  const baseLength = Math.min(width, height) / 8
  const length = baseLength / Math.pow(1.3, iteration * 0.5)

  // Starting position (bottom center)
  const turtle: TurtleState = {
    x: width / 2,
    y: height * 0.85,
    angle: -90, // Point upward
    thickness: 1.0,
  }

  // State stack for branching
  const stateStack: TurtleState[] = []

  // Process commands
  let i = 0
  while (i < commands.length) {
    const char = commands[i]

    switch (char) {
      case "F": {
        // Extract thickness if present
        if (commands[i + 1] === "(") {
          const closeIdx = commands.indexOf(")", i)
          const thickness = parseFloat(commands.substring(i + 2, closeIdx))

          // Draw forward with thickness
          const radians = (turtle.angle * Math.PI) / 180
          const newX = turtle.x + length * Math.cos(radians)
          const newY = turtle.y + length * Math.sin(radians)

          // Color based on depth (thickness) - thicker = darker (base), thinner = lighter (tips)
          const lightness = 40 + (1 - thickness) * 40 // 40-80% lightness
          ctx.strokeStyle = `hsl(${180 + iteration * 10}, 70%, ${lightness}%)`
          ctx.lineWidth = thickness * 8 // Scale thickness for visibility
          ctx.lineCap = "round"

          ctx.beginPath()
          ctx.moveTo(turtle.x, turtle.y)
          ctx.lineTo(newX, newY)
          ctx.stroke()

          turtle.x = newX
          turtle.y = newY
          turtle.thickness = thickness

          i = closeIdx + 1
        } else {
          i++
        }
        break
      }

      case "+": {
        // Turn right - extract angle if present
        if (commands[i + 1] === "(") {
          const closeIdx = commands.indexOf(")", i)
          const angle = parseFloat(commands.substring(i + 2, closeIdx))
          turtle.angle += angle
          i = closeIdx + 1
        } else {
          turtle.angle += 25 // Default angle
          i++
        }
        break
      }

      case "-": {
        // Turn left - extract angle if present
        if (commands[i + 1] === "(") {
          const closeIdx = commands.indexOf(")", i)
          const angle = parseFloat(commands.substring(i + 2, closeIdx))
          turtle.angle -= angle
          i = closeIdx + 1
        } else {
          turtle.angle -= 25 // Default angle
          i++
        }
        break
      }

      case "[":
        // Push state (start branch)
        stateStack.push({ ...turtle })
        i++
        break

      case "]":
        // Pop state (end branch, return to saved position)
        if (stateStack.length > 0) {
          const state = stateStack.pop()!
          turtle.x = state.x
          turtle.y = state.y
          turtle.angle = state.angle
          turtle.thickness = state.thickness
        }
        i++
        break

      default:
        i++
    }
  }
}
