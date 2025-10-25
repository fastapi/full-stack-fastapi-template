import { describe, expect, it } from "vitest"
import { formatFileSize, formatFileSizeWithUnit } from "./fileFormatting"

describe("fileFormatting", () => {
  describe("formatFileSize", () => {
    it("should format bytes to MB with 2 decimal places", () => {
      const bytes = 5 * 1024 * 1024 // 5MB
      expect(formatFileSize(bytes)).toBe("5.00")
    })

    it("should handle fractional megabytes", () => {
      const bytes = 5.5 * 1024 * 1024 // 5.5MB
      expect(formatFileSize(bytes)).toBe("5.50")
    })

    it("should round to 2 decimal places", () => {
      const bytes = 5.123 * 1024 * 1024 // 5.123MB
      expect(formatFileSize(bytes)).toBe("5.12")
    })

    it("should handle very small files", () => {
      const bytes = 1024 // 1KB = 0.00097MB
      expect(formatFileSize(bytes)).toBe("0.00")
    })

    it("should handle large files", () => {
      const bytes = 100 * 1024 * 1024 // 100MB
      expect(formatFileSize(bytes)).toBe("100.00")
    })

    it("should handle zero bytes", () => {
      expect(formatFileSize(0)).toBe("0.00")
    })

    it("should format 25MB (max limit) correctly", () => {
      const bytes = 25 * 1024 * 1024
      expect(formatFileSize(bytes)).toBe("25.00")
    })

    it("should format 30MB correctly", () => {
      const bytes = 30 * 1024 * 1024
      expect(formatFileSize(bytes)).toBe("30.00")
    })
  })

  describe("formatFileSizeWithUnit", () => {
    it("should include MB unit in output", () => {
      const bytes = 5 * 1024 * 1024
      expect(formatFileSizeWithUnit(bytes)).toBe("5.00 MB")
    })

    it("should format with unit for small files", () => {
      const bytes = 1024
      expect(formatFileSizeWithUnit(bytes)).toBe("0.00 MB")
    })

    it("should format with unit for large files", () => {
      const bytes = 100 * 1024 * 1024
      expect(formatFileSizeWithUnit(bytes)).toBe("100.00 MB")
    })
  })
})
