/**
 * File validation utilities for upload form
 */

export const MAX_FILE_SIZE = 25 * 1024 * 1024 // 25MB in bytes
export const ALLOWED_MIME_TYPE = "application/pdf"

export interface FileValidationError {
  type: "invalid_type" | "file_too_large"
  message: string
}

/**
 * Validate if file is a PDF
 */
export function isPDF(file: File): boolean {
  return file.type === ALLOWED_MIME_TYPE
}

/**
 * Validate if file size is within limit
 */
export function isWithinSizeLimit(
  file: File,
  maxSize: number = MAX_FILE_SIZE,
): boolean {
  return file.size <= maxSize
}

/**
 * Comprehensive file validation
 * Returns null if valid, or error object if invalid
 */
export function validateFile(file: File): string | null {
  // Check MIME type
  if (!isPDF(file)) {
    return "Invalid file type. Only PDF files are supported."
  }

  // Check file size
  if (!isWithinSizeLimit(file)) {
    const fileSizeMB = (file.size / 1024 / 1024).toFixed(2)
    return `File too large. Maximum size: 25MB. Your file: ${fileSizeMB}MB.`
  }

  return null
}
