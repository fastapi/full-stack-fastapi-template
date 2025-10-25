/**
 * File formatting utilities
 */

/**
 * Format file size from bytes to megabytes
 * @param bytes - File size in bytes
 * @returns Formatted string like "5.00 MB"
 */
export function formatFileSize(bytes: number): string {
  return (bytes / 1024 / 1024).toFixed(2)
}

/**
 * Format file size with unit
 * @param bytes - File size in bytes
 * @returns Formatted string like "5.00 MB"
 */
export function formatFileSizeWithUnit(bytes: number): string {
  return `${formatFileSize(bytes)} MB`
}
