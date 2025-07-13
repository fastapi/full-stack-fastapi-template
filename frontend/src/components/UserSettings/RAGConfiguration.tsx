import {
  Box,
  Button,
  Flex,
  Heading,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import React, { useState } from "react"
import { FiRefreshCw, FiSave } from "react-icons/fi"

import { type ConfigurationRequest, EnhancedRagService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { Field } from "../ui/field"

interface RAGConfigForm {
  chunking_strategy: string
  chunk_size: number
  chunk_overlap: number
  embedding_model: string
  search_algorithm: string
  similarity_threshold: number
  max_results: number
  enable_reranking: boolean
}

const RAGConfiguration: React.FC = () => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  // Get current RAG configuration
  const {
    data: currentConfig,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["rag-configuration"],
    queryFn: () => EnhancedRagService.getRagConfiguration(),
  })

  // Initialize form with current config or defaults
  const [formData, setFormData] = useState<RAGConfigForm>({
    chunking_strategy: "semantic",
    chunk_size: 500,
    chunk_overlap: 50,
    embedding_model: "text-embedding-3-small",
    search_algorithm: "hybrid",
    similarity_threshold: 0.7,
    max_results: 10,
    enable_reranking: true,
  })

  // Update form when config loads
  React.useEffect(() => {
    if (currentConfig && typeof currentConfig === "object") {
      const config = currentConfig as any
      setFormData({
        chunking_strategy: config.chunking_strategy || "semantic",
        chunk_size: config.chunk_size || 500,
        chunk_overlap: config.chunk_overlap || 50,
        embedding_model: config.embedding_model || "text-embedding-3-small",
        search_algorithm: config.search_algorithm || "hybrid",
        similarity_threshold: config.similarity_threshold || 0.7,
        max_results: config.max_results || 10,
        enable_reranking: config.enable_reranking ?? true,
      })
    }
  }, [currentConfig])

  // Update configuration mutation
  const updateConfigMutation = useMutation({
    mutationFn: (config: ConfigurationRequest) =>
      EnhancedRagService.updateRagConfiguration({ requestBody: config }),
    onSuccess: () => {
      showSuccessToast("RAG configuration updated successfully")
      queryClient.invalidateQueries({ queryKey: ["rag-configuration"] })
    },
    onError: (error: any) => {
      showErrorToast(`Failed to update configuration: ${error.message}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateConfigMutation.mutate(formData)
  }

  const handleInputChange = (
    field: keyof RAGConfigForm,
    value: string | number | boolean,
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const resetToDefaults = () => {
    setFormData({
      chunking_strategy: "semantic",
      chunk_size: 500,
      chunk_overlap: 50,
      embedding_model: "text-embedding-3-small",
      search_algorithm: "hybrid",
      similarity_threshold: 0.7,
      max_results: 10,
      enable_reranking: true,
    })
  }

  if (isLoading) {
    return (
      <Box>
        <Text>Loading RAG configuration...</Text>
      </Box>
    )
  }

  if (error) {
    return (
      <Box>
        <Text color="red.500">Failed to load RAG configuration</Text>
      </Box>
    )
  }

  return (
    <Box>
      <form onSubmit={handleSubmit}>
        <VStack gap={6} align="stretch">
          {/* Document Processing Settings */}
          <Box>
            <Heading size="sm" mb={4}>
              Document Processing
            </Heading>
            <VStack gap={4} align="stretch">
              <Field
                label="Chunking Strategy"
                helperText="How documents are split into chunks for processing"
              >
                <select
                  value={formData.chunking_strategy}
                  onChange={(e) =>
                    handleInputChange("chunking_strategy", e.target.value)
                  }
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    borderRadius: "6px",
                    border: "1px solid #e2e8f0",
                    fontSize: "14px",
                  }}
                >
                  <option value="semantic">Semantic (Recommended)</option>
                  <option value="sentence">Sentence-based</option>
                  <option value="paragraph">Paragraph-based</option>
                  <option value="simple">Simple (Fixed size)</option>
                </select>
              </Field>

              <Flex gap={4}>
                <Field
                  label="Chunk Size"
                  helperText="Characters per chunk (100-2000)"
                >
                  <Input
                    type="number"
                    value={formData.chunk_size}
                    onChange={(e) =>
                      handleInputChange(
                        "chunk_size",
                        Number.parseInt(e.target.value),
                      )
                    }
                    min={100}
                    max={2000}
                  />
                </Field>

                <Field
                  label="Chunk Overlap"
                  helperText="Overlap between chunks (0-200)"
                >
                  <Input
                    type="number"
                    value={formData.chunk_overlap}
                    onChange={(e) =>
                      handleInputChange(
                        "chunk_overlap",
                        Number.parseInt(e.target.value),
                      )
                    }
                    min={0}
                    max={200}
                  />
                </Field>
              </Flex>

              <Field
                label="Embedding Model"
                helperText="Model used to generate embeddings"
              >
                <select
                  value={formData.embedding_model}
                  onChange={(e) =>
                    handleInputChange("embedding_model", e.target.value)
                  }
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    borderRadius: "6px",
                    border: "1px solid #e2e8f0",
                    fontSize: "14px",
                  }}
                >
                  <option value="text-embedding-3-small">
                    OpenAI Small (Recommended)
                  </option>
                  <option value="text-embedding-3-large">
                    OpenAI Large (Higher quality)
                  </option>
                  <option value="text-embedding-ada-002">
                    OpenAI Ada (Legacy)
                  </option>
                </select>
              </Field>
            </VStack>
          </Box>

          {/* Search Settings */}
          <Box>
            <Heading size="sm" mb={4}>
              Search Settings
            </Heading>
            <VStack gap={4} align="stretch">
              <Field
                label="Search Algorithm"
                helperText="Search method for finding relevant content"
              >
                <select
                  value={formData.search_algorithm}
                  onChange={(e) =>
                    handleInputChange("search_algorithm", e.target.value)
                  }
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    borderRadius: "6px",
                    border: "1px solid #e2e8f0",
                    fontSize: "14px",
                  }}
                >
                  <option value="hybrid">Hybrid (Vector + Keyword)</option>
                  <option value="vector">Vector Only</option>
                  <option value="keyword">Keyword Only</option>
                </select>
              </Field>

              <Flex gap={4}>
                <Field
                  label="Similarity Threshold"
                  helperText="Minimum similarity score (0.0-1.0)"
                >
                  <Input
                    type="number"
                    step="0.1"
                    value={formData.similarity_threshold}
                    onChange={(e) =>
                      handleInputChange(
                        "similarity_threshold",
                        Number.parseFloat(e.target.value),
                      )
                    }
                    min={0}
                    max={1}
                  />
                </Field>

                <Field
                  label="Max Results"
                  helperText="Maximum search results (1-50)"
                >
                  <Input
                    type="number"
                    value={formData.max_results}
                    onChange={(e) =>
                      handleInputChange(
                        "max_results",
                        Number.parseInt(e.target.value),
                      )
                    }
                    min={1}
                    max={50}
                  />
                </Field>
              </Flex>

              <Field
                label="Result Reranking"
                helperText="Improve result relevance with advanced reranking"
              >
                <Flex align="center" gap={2}>
                  <input
                    type="checkbox"
                    checked={formData.enable_reranking}
                    onChange={(e) =>
                      handleInputChange("enable_reranking", e.target.checked)
                    }
                    style={{ marginRight: "8px" }}
                  />
                  <Text fontSize="sm">Enable result reranking</Text>
                </Flex>
              </Field>
            </VStack>
          </Box>

          {/* Action Buttons */}
          <Flex gap={4} pt={4}>
            <Button
              type="submit"
              colorScheme="teal"
              loading={updateConfigMutation.isPending}
              loadingText="Saving..."
            >
              <FiSave style={{ marginRight: "0.5rem" }} />
              Save Configuration
            </Button>
            <Button
              variant="outline"
              onClick={resetToDefaults}
              disabled={updateConfigMutation.isPending}
            >
              <FiRefreshCw style={{ marginRight: "0.5rem" }} />
              Reset to Defaults
            </Button>
          </Flex>
        </VStack>
      </form>
    </Box>
  )
}

export default RAGConfiguration
