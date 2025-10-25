import { Box, Button, HStack, Icon, Text, VStack } from "@chakra-ui/react"
import { useRef, useState } from "react"
import { FiCheckCircle, FiFile, FiUpload, FiXCircle } from "react-icons/fi"
import useCustomToast from "@/hooks/useCustomToast"
import { useFileUpload } from "@/hooks/useFileUpload"
import { formatFileSize } from "@/utils/fileFormatting"
import { validateFile } from "@/utils/fileValidation"

export function UploadForm() {
  const [file, setFile] = useState<File | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [extractionId, setExtractionId] = useState<string | null>(null)

  const fileInputRef = useRef<HTMLInputElement>(null)
  const { upload, isUploading, error } = useFileUpload()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Handle file selection (from picker or drag-and-drop)
  const handleFileSelect = (selectedFile: File | null) => {
    if (!selectedFile) {
      setFile(null)
      setValidationError(null)
      return
    }

    const error = validateFile(selectedFile)
    if (error) {
      setValidationError(error)
      setFile(null)
      return
    }

    setValidationError(null)
    setFile(selectedFile)
  }

  // Handle file input change
  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0] || null
    handleFileSelect(selectedFile)
  }

  // Handle drag-and-drop
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()

    const droppedFiles = e.dataTransfer.files
    if (droppedFiles.length > 1) {
      showErrorToast("Only one file allowed. Using the first file.")
    }

    const droppedFile = droppedFiles[0] || null
    handleFileSelect(droppedFile)
  }

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }

  // Handle form submit
  const handleSubmit = async () => {
    if (!file) return

    const result = await upload(file)

    if (result.success && result.data) {
      setUploadSuccess(true)
      setExtractionId(result.data.id)
      showSuccessToast(
        `✓ Uploaded successfully! Extraction ID: ${result.data.id}`,
      )

      // Auto-redirect after 2 seconds
      // Note: The review route will be created in a separate story
      setTimeout(() => {
        // TODO: Navigate to review page when route is implemented
        // navigate({
        //   to: "/ingestions/$id/review",
        //   params: { id: result.data?.id },
        // })
        if (result.data) {
          console.log("Would redirect to review page:", result.data.id)
        }
      }, 2000)
    } else {
      showErrorToast(result.error || "Upload failed. Please try again.")
    }
  }

  // Handle cancel
  const handleCancel = () => {
    setFile(null)
    setValidationError(null)
    setUploadSuccess(false)
    setExtractionId(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  return (
    <VStack gap={6} align="stretch">
      {/* Upload Success State */}
      {uploadSuccess && extractionId && (
        <Box
          p={6}
          borderRadius="md"
          bg="green.50"
          borderWidth="1px"
          borderColor="green.200"
        >
          <HStack gap={3}>
            <Icon fontSize="2xl" color="green.500">
              <FiCheckCircle />
            </Icon>
            <VStack align="start" gap={1}>
              <Text fontWeight="semibold" color="green.700">
                Upload successful!
              </Text>
              <Text fontSize="sm" color="green.600">
                Extraction ID: {extractionId}
              </Text>
              <Text fontSize="sm" color="green.600">
                Redirecting to review page in 2 seconds...
              </Text>
            </VStack>
          </HStack>
          <Button
            mt={4}
            size="sm"
            colorPalette="green"
            onClick={() => {
              // TODO: Navigate to review page when route is implemented
              console.log("Would navigate to review page:", extractionId)
            }}
          >
            View Extraction Now
          </Button>
        </Box>
      )}

      {/* Drag-and-Drop Zone */}
      {!uploadSuccess && (
        <Box
          p={12}
          borderWidth="2px"
          borderStyle="dashed"
          borderColor={validationError ? "red.300" : "gray.300"}
          borderRadius="md"
          textAlign="center"
          bg={validationError ? "red.50" : "gray.50"}
          cursor="pointer"
          transition="all 0.2s"
          _hover={{ borderColor: validationError ? "red.400" : "blue.400" }}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={() => fileInputRef.current?.click()}
        >
          <VStack gap={4}>
            <Icon
              fontSize="4xl"
              color={validationError ? "red.400" : "gray.400"}
            >
              <FiUpload />
            </Icon>
            <VStack gap={2}>
              <Text fontSize="lg" fontWeight="medium">
                Drag and drop a PDF file here, or click to select
              </Text>
              <Text fontSize="sm" color="gray.600">
                PDF files only, max 25MB
              </Text>
            </VStack>
            <input
              ref={fileInputRef}
              type="file"
              accept="application/pdf"
              onChange={handleFileInputChange}
              style={{ display: "none" }}
              aria-label="Upload PDF file"
            />
            <Button colorPalette="blue" size="md">
              Choose File
            </Button>
          </VStack>
        </Box>
      )}

      {/* Validation Error */}
      {validationError && (
        <Box
          p={4}
          borderRadius="md"
          bg="red.50"
          borderWidth="1px"
          borderColor="red.200"
        >
          <HStack gap={2}>
            <Icon color="red.500">
              <FiXCircle />
            </Icon>
            <Text color="red.700" fontWeight="medium">
              {validationError}
            </Text>
          </HStack>
        </Box>
      )}

      {/* Selected File Info */}
      {file && !isUploading && !uploadSuccess && (
        <Box
          p={4}
          borderRadius="md"
          bg="blue.50"
          borderWidth="1px"
          borderColor="blue.200"
        >
          <HStack gap={3}>
            <Icon fontSize="xl" color="blue.500">
              <FiFile />
            </Icon>
            <VStack align="start" gap={0} flex={1}>
              <Text fontWeight="medium">{file.name}</Text>
              <Text fontSize="sm" color="gray.600">
                {formatFileSize(file.size)} MB
              </Text>
            </VStack>
          </HStack>
        </Box>
      )}

      {/* Upload Error */}
      {error && (
        <Box
          p={4}
          borderRadius="md"
          bg="red.50"
          borderWidth="1px"
          borderColor="red.200"
        >
          <HStack gap={2}>
            <Icon color="red.500">
              <FiXCircle />
            </Icon>
            <VStack align="start" gap={1} flex={1}>
              <Text color="red.700" fontWeight="medium">
                ✗ Upload failed
              </Text>
              <Text fontSize="sm" color="red.600">
                {error}
              </Text>
              <Text fontSize="xs" color="red.500">
                If issue persists, contact support
              </Text>
            </VStack>
          </HStack>
        </Box>
      )}

      {/* Action Buttons */}
      {!uploadSuccess && (
        <HStack gap={3}>
          <Button
            flex={1}
            colorPalette="blue"
            onClick={handleSubmit}
            disabled={!file || isUploading}
            loading={isUploading}
            loadingText="Uploading..."
          >
            Upload
          </Button>
          <Button
            variant="outline"
            colorPalette="gray"
            onClick={handleCancel}
            disabled={isUploading}
          >
            Cancel
          </Button>
        </HStack>
      )}
    </VStack>
  )
}
