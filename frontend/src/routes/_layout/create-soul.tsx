import {
  Box,
  Button,
  Container,
  HStack,
  Heading,
  Input,
  Text,
  Textarea,
  VStack,
  Badge,
  Flex,
  IconButton,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useState, useRef } from "react"
import type { FormEvent } from "react"
import { FiArrowLeft, FiSave, FiUpload, FiX, FiFile } from "react-icons/fi"

import { AiSoulsService, TrainingService } from "@/client"
import { Field } from "@/components/ui/field"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/_layout/create-soul")({
  component: CreateSoul,
})

interface AISoulFormData {
  name: string
  description: string
  persona_type: string
  specializations: string
  base_prompt: string
}

function CreateSoul() {
  const navigate = useNavigate()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const [formData, setFormData] = useState<AISoulFormData>({
    name: "",
    description: "",
    persona_type: "",
    specializations: "",
    base_prompt: "",
  })

  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Create AI soul mutation
  const createAiSoulMutation = useMutation({
    mutationFn: async (data: AISoulFormData) => {
      // First create the AI soul
      const aiSoul = await AiSoulsService.createAiSoul({
        requestBody: {
          name: data.name,
          description: data.description || null,
          persona_type: data.persona_type,
          specializations: data.specializations,
          base_prompt: data.base_prompt,
          user_id: "current-user", // This will be set by the backend
        },
      })

      // Then upload documents if any are selected
      if (selectedFiles.length > 0) {
        for (const file of selectedFiles) {
          await TrainingService.uploadTrainingDocument({
            aiSoulId: aiSoul.id!,
            formData: {
              file: file,
              description: `Knowledge base document: ${file.name}`
            },
          })
        }
      }

      return aiSoul
    },
    onSuccess: () => {
      showSuccessToast(
        selectedFiles.length > 0 
          ? `AI soul created successfully with ${selectedFiles.length} documents uploaded`
          : "AI soul created successfully"
      )
      queryClient.invalidateQueries({ queryKey: ["ai-souls"] })
      navigate({ to: "/ai-souls" })
    },
    onError: (error: any) => {
      showErrorToast(error.body?.detail || "Failed to create AI soul")
    },
  })

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (
      !formData.name ||
      !formData.description ||
      !formData.persona_type ||
      !formData.specializations ||
      !formData.base_prompt
    ) {
      showErrorToast("Please fill in all required fields")
      return
    }
    createAiSoulMutation.mutate(formData)
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || [])
    setSelectedFiles((prev) => [...prev, ...files])
  }

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const handleInputChange = (field: keyof AISoulFormData, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  return (
    <Container maxW="4xl" py={8}>
      <VStack gap={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <VStack align="start" gap={1}>
            <Heading size="lg">Create New AI Soul</Heading>
            <Text color="gray.600">
              Design your AI companion's personality and behavior
            </Text>
          </VStack>
          <Button
            variant="outline"
            onClick={() => navigate({ to: "/ai-souls" })}
          >
            <FiArrowLeft style={{ marginRight: "0.5rem" }} />
            Back to AI Souls
          </Button>
        </HStack>

        {/* Form */}
        <Box as="form" onSubmit={handleSubmit}>
          <VStack gap={6} align="stretch">
            <Field label="Name" required>
              <Input
                value={formData.name}
                onChange={(e) => handleInputChange("name", e.target.value)}
                placeholder="Enter AI soul name"
              />
            </Field>

            <Field label="Description" required>
              <Textarea
                value={formData.description}
                onChange={(e) =>
                  handleInputChange("description", e.target.value)
                }
                placeholder="Describe your AI soul's purpose and personality"
                rows={3}
              />
            </Field>

            <Field label="Persona Type" required>
              <Input
                value={formData.persona_type}
                onChange={(e) =>
                  handleInputChange("persona_type", e.target.value)
                }
                placeholder="e.g., coach, counselor, guide, teacher"
              />
            </Field>

            <Field label="Specializations" required>
              <Input
                value={formData.specializations}
                onChange={(e) =>
                  handleInputChange("specializations", e.target.value)
                }
                placeholder="e.g., motivation, mindfulness, creativity, goal setting"
              />
            </Field>

            <Field label="Base Prompt" required>
              <Textarea
                value={formData.base_prompt}
                onChange={(e) =>
                  handleInputChange("base_prompt", e.target.value)
                }
                placeholder="Define your AI soul's personality, communication style, and approach"
                rows={6}
              />
            </Field>

            {/* Knowledge Base Documents */}
            <Field label="Knowledge Base Documents (Optional)">
              <VStack gap={4} align="stretch">
                <Text fontSize="sm" color="gray.600">
                  Upload documents to provide your AI soul with specific knowledge and context. 
                  Supported formats: .txt, .md, .pdf
                </Text>
                
                <Box>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".txt,.md,.pdf"
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                  />
                  <Button
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                    size="sm"
                  >
                    <FiUpload style={{ marginRight: "0.5rem" }} />
                    Select Documents
                  </Button>
                </Box>

                {selectedFiles.length > 0 && (
                  <VStack gap={2} align="stretch">
                    <Text fontSize="sm" fontWeight="medium">
                      Selected Files ({selectedFiles.length}):
                    </Text>
                    {selectedFiles.map((file, index) => (
                      <Flex
                        key={index}
                        justify="space-between"
                        align="center"
                        p={3}
                        bg="gray.50"
                        borderRadius="md"
                        border="1px"
                        borderColor="gray.200"
                      >
                        <Flex align="center" gap={2}>
                          <FiFile color="gray.500" />
                          <VStack align="start" gap={0}>
                            <Text fontSize="sm" fontWeight="medium">
                              {file.name}
                            </Text>
                            <Text fontSize="xs" color="gray.500">
                              {formatFileSize(file.size)}
                            </Text>
                          </VStack>
                        </Flex>
                        <IconButton
                          aria-label="Remove file"
                          size="sm"
                          variant="ghost"
                          colorScheme="red"
                          onClick={() => removeFile(index)}
                        >
                          <FiX />
                        </IconButton>
                      </Flex>
                    ))}
                  </VStack>
                )}
              </VStack>
            </Field>

            {/* Action Buttons */}
            <HStack gap={4} pt={4}>
              <Button
                type="submit"
                colorScheme="teal"
                size="lg"
                loading={createAiSoulMutation.isPending}
                loadingText={selectedFiles.length > 0 ? "Creating & Uploading..." : "Creating..."}
              >
                <FiSave style={{ marginRight: "0.5rem" }} />
                Create AI Soul
                {selectedFiles.length > 0 && (
                  <Badge ml={2} colorScheme="blue" variant="solid">
                    +{selectedFiles.length} docs
                  </Badge>
                )}
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => navigate({ to: "/ai-souls" })}
                disabled={createAiSoulMutation.isPending}
              >
                Cancel
              </Button>
            </HStack>
          </VStack>
        </Box>
      </VStack>
    </Container>
  )
}
