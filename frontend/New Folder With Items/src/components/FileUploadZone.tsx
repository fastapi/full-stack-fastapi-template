import type React from "react"
import { useRef, useState } from "react"

type Props = {
  onFileSelect?: (file: File) => void
  onClick?: () => void
  accept?: string
  className?: string
  title?: string
  description?: string
  sizeHint?: string
}

export default function FileUploadZone({
  onFileSelect,
  onClick,
  accept = ".pdf,.jpg,.jpeg,.png,.gif,.bmp",
  className,
  title = "Drag and drop your bank statement here",
  description = "PDF or image (JPG, PNG)",
  sizeHint = "Size up to 100 MB",
}: Props) {
  const [isDrag, setIsDrag] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDrag(true)
  }

  const handleDragLeave = () => {
    setIsDrag(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDrag(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      const isValidType =
        file.type === "application/pdf" || file.type.startsWith("image/")
      if (isValidType) {
        onFileSelect?.(file)
      }
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      onFileSelect?.(files[0])
    }
  }

  return (
    <div className="mt-6">
      <button
        type="button"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => (onClick ? onClick() : fileInputRef.current?.click())}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault()
            if (onClick) onClick()
            else fileInputRef.current?.click()
          }
        }}
        className={`cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-all ${
          isDrag
            ? "border-primary bg-secondary"
            : "border-border bg-muted hover:bg-secondary"
        } ${className ?? ""}`}
      >
        <svg
          className="mx-auto h-12 w-12 text-primary/60"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <title>Upload icon</title>
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 4v16m8-8H4"
          />
        </svg>
        <p className="mt-4 text-sm font-medium text-foreground">{title}</p>
        <p className="mt-1 text-xs text-muted-foreground">{description}</p>
        <p className="mt-2 text-xs text-muted-foreground">{sizeHint}</p>
      </button>
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        onChange={handleFileSelect}
        className="hidden"
      />
    </div>
  )
}
