import { Document, Page } from "react-pdf"
import { Box, Heading, Spinner, Text, VStack } from "@chakra-ui/react"

export function TestPDFWorker() {
  const testPDF =
    "https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf"

  return (
    <VStack p={8} gap={4} align="start">
      <Heading size="lg">PDF Worker Test</Heading>
      <Text>
        If you see a PDF page below, the worker is configured correctly.
      </Text>

      <Box border="1px" borderColor="gray.200" p={4} borderRadius="md">
        <Document
          file={testPDF}
          onLoadSuccess={(pdf) => {
            console.log("✅ PDF loaded successfully:", pdf.numPages, "pages")
          }}
          onLoadError={(error) => {
            console.error("❌ PDF load error:", error)
          }}
          loading={
            <VStack gap={2} py={8}>
              <Spinner size="xl" />
              <Text>Loading PDF...</Text>
            </VStack>
          }
          error={
            <Box bg="red.50" p={4} borderRadius="md">
              <Text color="red.600" fontWeight="bold">
                Failed to load PDF
              </Text>
              <Text color="red.600" fontSize="sm" mt={2}>
                Check browser console for errors. Worker may not be configured
                correctly.
              </Text>
            </Box>
          }
        >
          <Page
            pageNumber={1}
            width={600}
            loading={
              <VStack gap={2} py={8}>
                <Spinner />
                <Text fontSize="sm">Rendering page...</Text>
              </VStack>
            }
          />
        </Document>
      </Box>

      <Box bg="blue.50" p={4} borderRadius="md" w="full">
        <Text fontWeight="bold" color="blue.700">
          Testing Instructions:
        </Text>
        <Text fontSize="sm" color="blue.600" mt={2}>
          1. Check browser console for "INFO: PDF.js worker configured from
          CDN"
        </Text>
        <Text fontSize="sm" color="blue.600">
          2. Verify PDF page renders above
        </Text>
        <Text fontSize="sm" color="blue.600">
          3. Check for "✅ PDF loaded successfully" in console
        </Text>
        <Text fontSize="sm" color="blue.600">
          4. Confirm no errors or warnings
        </Text>
        <Text fontSize="sm" color="blue.600">
          5. Delete this test component after verification
        </Text>
      </Box>
    </VStack>
  )
}
