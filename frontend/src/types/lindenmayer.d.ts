/**
 * Type declarations for lindenmayer L-system library
 *
 * The lindenmayer library provides L-system functionality for generating
 * fractal patterns and natural structures through string rewriting.
 */
declare module "lindenmayer" {
  /**
   * L-System configuration options
   */
  interface LSystemOptions {
    /**
     * Starting string for the L-system
     */
    axiom: string

    /**
     * Production rules for string rewriting
     * Key: symbol to replace
     * Value: replacement string or function
     */
    productions: {
      [key: string]: string | ((context: ProductionContext) => string)
    }

    /**
     * Optional ignorable symbols for context-sensitive rules
     */
    ignoredSymbols?: string[]
  }

  /**
   * Context passed to production functions
   */
  interface ProductionContext {
    /**
     * Current position in the axiom
     */
    index: number

    /**
     * The full current axiom string
     */
    currentAxiom: string

    /**
     * Parameters for parametric L-systems
     */
    parameters?: any[]
  }

  /**
   * L-System class for generating fractals and patterns
   */
  export default class LSystem {
    /**
     * Create a new L-system
     * @param options - Configuration options
     */
    constructor(options: LSystemOptions)

    /**
     * Set the axiom (starting string)
     * @param axiom - New axiom string
     */
    setAxiom(axiom: string): LSystem

    /**
     * Set a production rule
     * @param symbol - Symbol to replace
     * @param replacement - Replacement string or function
     */
    setProduction(
      symbol: string,
      replacement: string | ((context: ProductionContext) => string),
    ): LSystem

    /**
     * Generate iterations of the L-system
     * @param iterations - Number of iterations to perform
     * @returns The L-system instance for chaining
     */
    iterate(iterations: number): LSystem

    /**
     * Get the current axiom string
     * @returns Current state of the L-system
     */
    getString(): string

    /**
     * Execute final visualization functions
     * @returns The L-system instance for chaining
     */
    final(): LSystem

    /**
     * Reset the L-system to initial axiom
     * @returns The L-system instance for chaining
     */
    reset(): LSystem
  }
}
