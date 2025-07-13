import {
  Box,
  Button,
  Container,
  HStack,
  Heading,
  Input,
  Spinner,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate, useParams } from "@tanstack/react-router"
import type React from "react"
import { useEffect, useState } from "react"
import { FiArrowLeft, FiSave } from "react-icons/fi"

import { AiSoulsService } from "@/client"
import type { AISoulEntity } from "@/client"
import { Field } from "@/components/ui/field"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/_layout/ai-souls-edit/$id")({
  component: EditAiSoul,
})

interface AISoulFormData {
  name: string
  description: string
  persona_type: string
  specializations: string
  base_prompt: string
  is_active: boolean
}

function EditAiSoul() {
  const navigate = useNavigate()
  const { id } = useParams({ from: "/_layout/ai-souls-edit/$id" })
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const [formData, setFormData] = useState<AISoulFormData>({
    name: "",
    description: "",
    persona_type: "",
    specializations: "",
    base_prompt: "",
    is_active: true,
  })

  // Fetch AI soul data
  const {
    data: aiSoul,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["ai-soul", id],
    queryFn: () => AiSoulsService.getAiSoul({ aiSoulId: id }),
    enabled: !!id,
  })

  // Update form data when AI soul data is loaded
  useEffect(() => {
    if (aiSoul) {
      setFormData({
        name: aiSoul.name || "",
        description: aiSoul.description || "",
        persona_type: aiSoul.persona_type || "",
        specializations: aiSoul.specializations || "",
        base_prompt: aiSoul.base_prompt || "",
        is_active: aiSoul.is_active ?? true,
      })
    }
  }, [aiSoul])

  // Update AI soul mutation
  const updateAiSoulMutation = useMutation({
    mutationFn: (data: AISoulFormData) =>
      AiSoulsService.updateAiSoul({
        aiSoulId: id,
        requestBody: {
          ...data,
          user_id: aiSoul?.user_id || "", // Preserve the user_id
        } as AISoulEntity,
      }),
    onSuccess: () => {
      showSuccessToast("AI soul updated successfully")
      queryClient.invalidateQueries({ queryKey: ["ai-souls"] })
      queryClient.invalidateQueries({ queryKey: ["ai-soul", id] })
      navigate({ to: "/ai-souls" })
    },
    onError: (error: any) => {
      showErrorToast(error.body?.detail || "Failed to update AI soul")
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (
      !formData.name ||
      !formData.persona_type ||
      !formData.specializations ||
      !formData.base_prompt
    ) {
      showErrorToast("Please fill in all required fields")
      return
    }
    updateAiSoulMutation.mutate(formData)
  }

  const handleInputChange = (
    field: keyof AISoulFormData,
    value: string | boolean,
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  if (isLoading) {
    return (
      <Container maxW="4xl" py={8}>
        <VStack gap={4}>
          <Spinner size="xl" />
          <Text>Loading AI soul...</Text>
        </VStack>
      </Container>
    )
  }

  if (error) {
    return (
      <Container maxW="4xl" py={8}>
        <Text color="red.500">Failed to load AI soul. Please try again.</Text>
      </Container>
    )
  }

  return (
    <Container maxW="4xl" py={8}>
      <VStack gap={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <VStack align="start" gap={1}>
            <Heading size="lg">Edit AI Soul</Heading>
            <Text color="gray.600">
              Update your AI soul's personality and behavior
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

            <Field label="Description">
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

            {/* Action Buttons */}
            <HStack gap={4} pt={4}>
              <Button
                type="submit"
                colorScheme="teal"
                size="lg"
                loading={updateAiSoulMutation.isPending}
                loadingText="Saving..."
              >
                <FiSave style={{ marginRight: "0.5rem" }} />
                Save Changes
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => navigate({ to: "/ai-souls" })}
                disabled={updateAiSoulMutation.isPending}
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
