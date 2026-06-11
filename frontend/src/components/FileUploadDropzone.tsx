import { File, FolderOpen, Upload, X } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100 MB

const ACCEPTED_TYPES = [
  "application/pdf",
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/gif",
  "image/tiff",
  "image/bmp",
]

function isAcceptedType(type: string) {
  return type === "application/pdf" || type.startsWith("image/")
}

function validateFile(file: File): string | null {
  if (!isAcceptedType(file.type)) {
    return `"${file.name}" is not allowed. Only images and PDFs are accepted.`
  }
  if (file.size > MAX_FILE_SIZE) {
    return `"${file.name}" exceeds the 100 MB limit (${(file.size / 1024 / 1024).toFixed(1)} MB).`
  }
  return null
}

async function collectFilesFromItems(
  items: DataTransferItemList,
): Promise<{ files: File[]; folderName: string | null }> {
  const files: File[] = []
  let folderName: string | null = null

  const readEntry = (entry: FileSystemEntry): Promise<void> => {
    return new Promise((resolve) => {
      if (entry.isFile) {
        ;(entry as FileSystemFileEntry).file((f) => {
          files.push(f)
          resolve()
        })
      } else if (entry.isDirectory) {
        const reader = (entry as FileSystemDirectoryEntry).createReader()

        const readAllEntries = (acc: FileSystemEntry[] = []) => {
          reader.readEntries(async (batch) => {
            if (batch.length === 0) {
              await Promise.all(acc.map(readEntry))
              resolve()
            } else {
              readAllEntries([...acc, ...batch])
            }
          })
        }

        readAllEntries()
      } else {
        resolve()
      }
    })
  }

  const entries = Array.from(items)
    .map((item) => item.webkitGetAsEntry())
    .filter((e): e is FileSystemEntry => e !== null)

  // Capture folder name if user dropped a single directory
  if (entries.length === 1 && entries[0].isDirectory) {
    folderName = entries[0].name
  }

  await Promise.all(entries.map(readEntry))

  return { files, folderName }
}

interface Selection {
  files: File[]
  folderName: string | null // null means individual file(s), not a folder
}

interface FileUploadDropzoneProps {
  onFilesSelect?: (files: File[]) => void
  uploading?: boolean
}

export function FileUploadDropzone({ onFilesSelect }: FileUploadDropzoneProps) {
  const [isDragActive, setIsDragActive] = useState(false)
  const [selection, setSelection] = useState<Selection | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true)
    } else if (e.type === "dragleave") {
      setIsDragActive(false)
    }
  }

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
    setError(null)

    let files: File[]
    let folderName: string | null = null

    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      const result = await collectFilesFromItems(e.dataTransfer.items)
      files = result.files
      folderName = result.folderName
    } else {
      files = Array.from(e.dataTransfer.files)
    }

    // Filter out system/hidden files with no MIME type
    files = files.filter((f) => f.type !== "")

    const validationError = runValidation(files)
    if (validationError) {
      setError(validationError)
      return
    }

    commit(files, folderName)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null)

    const files = Array.from(e.target.files ?? [])
    if (files.length === 0) return

    // webkitRelativePath is "folderName/file.pdf" when a directory is picked
    const firstRelative = files[0].webkitRelativePath
    const folderName = firstRelative ? firstRelative.split("/")[0] : null

    const validationError = runValidation(files)
    if (validationError) {
      setError(validationError)
      return
    }

    commit(files, folderName)
  }

  /** Validates a list of files against all rules. Returns an error string or null. */
  function runValidation(files: File[]): string | null {
    if (files.length === 0) return "No valid files found."

    for (const file of files) {
      const err = validateFile(file)
      if (err) return err
    }

    if (files.length > 1) {
      const allPdf = files.every((f) => f.type === "application/pdf")
      const allImages = files.every((f) => f.type.startsWith("image/"))
      if (!allPdf && !allImages) {
        return "A folder must contain only images or only PDFs, not a mix of both."
      }
    }

    return null
  }

  function commit(files: File[], folderName: string | null) {
    setSelection({ files, folderName })
    onFilesSelect?.(files)
  }

  const handleClear = () => {
    setSelection(null)
    setError(null)
  }

  const totalSize = selection?.files.reduce((sum, f) => sum + f.size, 0) ?? 0

  return (
    <div className="space-y-2">
      <Card
        className={`border-2 border-dashed transition-all ${
          error
            ? "border-destructive bg-destructive/5"
            : isDragActive
              ? "border-primary bg-primary/5 scale-105"
              : "border-border hover:border-primary/50"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {!selection ? (
          <div className="p-12 flex flex-col items-center justify-center text-center">
            <div className="mb-4">
              <Upload className="w-12 h-12 text-primary/60 mx-auto" />
            </div>
            <h3 className="text-lg font-semibold mb-2">
              Upload bank statement
            </h3>
            <p className="text-sm text-foreground/60 mb-6">
              Drag and drop a file or folder here, or click to browse
            </p>
            <div className="flex gap-3">
              {/* Single-file picker */}
              <label className="cursor-pointer">
                <Button asChild variant="outline">
                  <span>
                    <File className="w-4 h-4 mr-2" />
                    Select File
                  </span>
                </Button>
                <input
                  type="file"
                  accept={ACCEPTED_TYPES.join(",")}
                  onChange={handleChange}
                  className="hidden"
                />
              </label>

              {/* Folder picker */}
              <label className="cursor-pointer">
                <Button asChild>
                  <span>
                    <FolderOpen className="w-4 h-4 mr-2" />
                    Select Folder
                  </span>
                </Button>
                <input
                  type="file"
                  // @ts-expect-error – webkitdirectory is not in standard typings
                  webkitdirectory=""
                  multiple
                  onChange={handleChange}
                  className="hidden"
                />
              </label>
            </div>
            <p className="text-xs text-foreground/50 mt-4">
              Accepted: images (JPEG, PNG, WebP, …) or PDF · Max 100 MB per file
              <br />
              Folders must contain only images or only PDFs
            </p>
          </div>
        ) : (
          <div className="p-8 flex flex-col items-center justify-center">
            <div className="mb-4 p-3 rounded-full bg-accent/10">
              {selection.folderName ? (
                <FolderOpen className="w-8 h-8 text-accent" />
              ) : (
                <File className="w-8 h-8 text-accent" />
              )}
            </div>

            <h4 className="text-sm font-semibold mb-1 text-center break-all max-w-xs">
              {selection.folderName ?? selection.files[0].name}
            </h4>

            <p className="text-xs text-foreground/60 mb-1">
              {selection.folderName
                ? `${selection.files.length} file${selection.files.length !== 1 ? "s" : ""}`
                : null}
            </p>

            <p className="text-xs text-foreground/60 mb-6">
              {(totalSize / 1024).toFixed(2)} KB total
            </p>

            <div className="flex gap-3">
              <Button variant="outline" size="sm" onClick={handleClear}>
                <X className="w-4 h-4 mr-1" />
                Clear
              </Button>
            </div>
          </div>
        )}
      </Card>

      {error && (
        <p className="text-sm text-destructive flex items-start gap-1.5 px-1">
          <span className="mt-0.5">⚠</span>
          <span>{error}</span>
        </p>
      )}
    </div>
  )
}
