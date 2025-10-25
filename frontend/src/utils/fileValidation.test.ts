import { describe, expect, it } from "vitest"
import {
  ALLOWED_MIME_TYPE,
  isPDF,
  isWithinSizeLimit,
  MAX_FILE_SIZE,
  validateFile,
} from "./fileValidation"

describe("fileValidation", () => {
  describe("isPDF", () => {
    it("should return true for PDF files", () => {
      const pdfFile = new File(["content"], "test.pdf", {
        type: "application/pdf",
      })
      expect(isPDF(pdfFile)).toBe(true)
    })

    it("should return false for DOCX files", () => {
      const docxFile = new File(["content"], "test.docx", {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      })
      expect(isPDF(docxFile)).toBe(false)
    })

    it("should return false for PNG files", () => {
      const pngFile = new File(["content"], "test.png", {
        type: "image/png",
      })
      expect(isPDF(pngFile)).toBe(false)
    })

    it("should return false for files with no type", () => {
      const unknownFile = new File(["content"], "test.unknown", {
        type: "",
      })
      expect(isPDF(unknownFile)).toBe(false)
    })
  })

  describe("isWithinSizeLimit", () => {
    it("should return true for files under 25MB", () => {
      const smallFile = new File(["x".repeat(5 * 1024 * 1024)], "small.pdf", {
        type: "application/pdf",
      })
      expect(isWithinSizeLimit(smallFile)).toBe(true)
    })

    it("should return true for files exactly at 25MB limit", () => {
      const exactFile = new File(["x".repeat(MAX_FILE_SIZE)], "exact.pdf", {
        type: "application/pdf",
      })
      expect(isWithinSizeLimit(exactFile)).toBe(true)
    })

    it("should return false for files over 25MB", () => {
      const largeFile = new File(["x".repeat(30 * 1024 * 1024)], "large.pdf", {
        type: "application/pdf",
      })
      expect(isWithinSizeLimit(largeFile)).toBe(false)
    })

    it("should accept custom size limit", () => {
      const file = new File(["x".repeat(10 * 1024 * 1024)], "test.pdf", {
        type: "application/pdf",
      })
      const customLimit = 5 * 1024 * 1024 // 5MB
      expect(isWithinSizeLimit(file, customLimit)).toBe(false)
    })
  })

  describe("validateFile", () => {
    it("should return null for valid PDF under size limit", () => {
      const validFile = new File(["x".repeat(5 * 1024 * 1024)], "valid.pdf", {
        type: "application/pdf",
      })
      expect(validateFile(validFile)).toBeNull()
    })

    it("should return error for non-PDF files", () => {
      const docxFile = new File(["content"], "test.docx", {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      })
      const error = validateFile(docxFile)
      expect(error).toBe("Invalid file type. Only PDF files are supported.")
    })

    it("should return error for PDF files over 25MB", () => {
      const largeFile = new File(["x".repeat(30 * 1024 * 1024)], "large.pdf", {
        type: "application/pdf",
      })
      const error = validateFile(largeFile)
      expect(error).toContain("File too large")
      expect(error).toContain("Maximum size: 25MB")
      expect(error).toContain("Your file:")
    })

    it("should show correct file size in error message", () => {
      const file = new File(["x".repeat(30 * 1024 * 1024)], "test.pdf", {
        type: "application/pdf",
      })
      const error = validateFile(file)
      expect(error).toMatch(/Your file: \d+\.\d{2}MB/)
    })
  })

  describe("constants", () => {
    it("should have correct MAX_FILE_SIZE", () => {
      expect(MAX_FILE_SIZE).toBe(25 * 1024 * 1024)
    })

    it("should have correct ALLOWED_MIME_TYPE", () => {
      expect(ALLOWED_MIME_TYPE).toBe("application/pdf")
    })
  })
})
