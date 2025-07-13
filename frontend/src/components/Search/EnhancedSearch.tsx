import {
  Badge,
  Box,
  Button,
  Flex,
  HStack,
  Heading,
  Input,
  Spinner,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery } from "@tanstack/react-query"
import type React from "react"
import { useEffect, useRef, useState } from "react"
import { FiClock, FiFileText, FiSearch, FiTrendingUp } from "react-icons/fi"

import { EnhancedRagService, type SearchRequest } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"

interface EnhancedSearchProps {
  aiSoulId?: string
  onResultClick?: (result: any) => void
  placeholder?: string
  autoFocus?: boolean
}

export const EnhancedSearch: React.FC<EnhancedSearchProps> = ({
  aiSoulId,
  onResultClick,
  placeholder = "Search your documents...",
  autoFocus = false,
}) => {
  const [query, setQuery] = useState("")
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1)
  const inputRef = useRef<HTMLInputElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)
  const { showErrorToast } = useCustomToast()

  // Get search suggestions
  const { data: suggestions, isLoading: suggestionsLoading } = useQuery({
    queryKey: ["search-suggestions", query],
    queryFn: () => EnhancedRagService.getSearchSuggestions({ query, limit: 5 }),
    enabled: query.length > 2, // Only fetch suggestions for queries longer than 2 characters
    staleTime: 1000 * 60 * 5, // Cache suggestions for 5 minutes
  })

  // Search mutation
  const searchMutation = useMutation({
    mutationFn: async (searchRequest: SearchRequest) => {
      return EnhancedRagService.searchDocuments({ requestBody: searchRequest })
    },
    onError: (error: any) => {
      showErrorToast(`Search failed: ${error.message}`)
    },
  })

  // Handle search submission
  const handleSearch = async () => {
    if (!query.trim()) return

    const searchRequest: SearchRequest = {
      query: query.trim(),
      ai_soul_id: aiSoulId,
      filters: {},
      limit: 10,
    }

    searchMutation.mutate(searchRequest)
  }

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)
    setShowSuggestions(value.length > 2)
    setSelectedSuggestionIndex(-1)
  }

  // Handle input focus
  const handleInputFocus = () => {
    if (query.length > 2) {
      setShowSuggestions(true)
    }
  }

  // Handle input blur
  const handleInputBlur = () => {
    // Delay hiding suggestions to allow for clicks
    setTimeout(() => {
      setShowSuggestions(false)
    }, 200)
  }

  // Handle key navigation
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (!showSuggestions) {
      if (e.key === "Enter") {
        handleSearch()
      }
      return
    }

    const suggestionsList = Array.isArray(suggestions) ? suggestions : []

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault()
        setSelectedSuggestionIndex((prev) =>
          prev < suggestionsList.length - 1 ? prev + 1 : prev,
        )
        break
      case "ArrowUp":
        e.preventDefault()
        setSelectedSuggestionIndex((prev) => (prev > 0 ? prev - 1 : -1))
        break
      case "Enter":
        e.preventDefault()
        if (
          selectedSuggestionIndex >= 0 &&
          suggestionsList[selectedSuggestionIndex]
        ) {
          handleSuggestionClick(suggestionsList[selectedSuggestionIndex])
        } else {
          handleSearch()
        }
        break
      case "Escape":
        setShowSuggestions(false)
        setSelectedSuggestionIndex(-1)
        break
    }
  }

  // Handle suggestion click
  const handleSuggestionClick = (suggestion: any) => {
    const suggestionText =
      typeof suggestion === "string"
        ? suggestion
        : suggestion.query || suggestion.text || ""
    setQuery(suggestionText)
    setShowSuggestions(false)
    setSelectedSuggestionIndex(-1)

    // Auto-search when selecting a suggestion
    const searchRequest: SearchRequest = {
      query: suggestionText,
      ai_soul_id: aiSoulId,
      filters: {},
      limit: 10,
    }
    searchMutation.mutate(searchRequest)
  }

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [])

  // Handle result click
  const handleResultClick = (result: any) => {
    // Track the click for analytics
    EnhancedRagService.trackResultClick({
      requestBody: {
        search_query_id: searchMutation.data?.query || "",
        chunk_id: result.chunk_id,
        result_position: 0,
        similarity_score: result.similarity_score,
      },
    }).catch(console.error)

    onResultClick?.(result)
  }

  const searchResults = searchMutation.data
  const isLoading = searchMutation.isPending

  return (
    <VStack gap={4} align="stretch" w="100%">
      {/* Search Header */}
      <VStack gap={2} align="stretch">
        <Heading size="md">Enhanced Document Search</Heading>
        <Text fontSize="sm" color="gray.600">
          Search through your documents with AI-powered semantic understanding
        </Text>
      </VStack>

      {/* Search Input with Suggestions */}
      <Box position="relative">
        <Input
          ref={inputRef}
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyPress}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          placeholder={placeholder}
          autoFocus={autoFocus}
          size="lg"
          bg="white"
          border="2px"
          borderColor="gray.200"
          _focus={{
            borderColor: "blue.500",
            boxShadow: "0 0 0 1px var(--chakra-colors-blue-500)",
          }}
        />

        {/* Suggestions Dropdown */}
        {showSuggestions && (
          <Box
            ref={suggestionsRef}
            position="absolute"
            top="100%"
            left={0}
            right={0}
            bg="white"
            border="1px"
            borderColor="gray.200"
            borderRadius="md"
            shadow="lg"
            zIndex={1000}
            maxH="200px"
            overflowY="auto"
          >
            {suggestionsLoading ? (
              <Flex justify="center" align="center" p={4}>
                <Spinner size="sm" />
                <Text ml={2} fontSize="sm">
                  Loading suggestions...
                </Text>
              </Flex>
            ) : (
              <VStack gap={0} align="stretch">
                {Array.isArray(suggestions) && suggestions.length > 0 ? (
                  suggestions.map((suggestion: any, index: number) => {
                    const suggestionText =
                      typeof suggestion === "string"
                        ? suggestion
                        : suggestion.query || suggestion.text || "No text"

                    return (
                      <Box
                        key={index}
                        p={3}
                        cursor="pointer"
                        bg={
                          selectedSuggestionIndex === index
                            ? "blue.50"
                            : "white"
                        }
                        _hover={{ bg: "gray.50" }}
                        onClick={() => handleSuggestionClick(suggestion)}
                        borderBottom={
                          index < suggestions.length - 1 ? "1px" : "none"
                        }
                        borderColor="gray.100"
                      >
                        <HStack>
                          <FiTrendingUp size={14} color="#718096" />
                          <Text fontSize="sm">{suggestionText}</Text>
                        </HStack>
                      </Box>
                    )
                  })
                ) : (
                  <Box p={3}>
                    <Text fontSize="sm" color="gray.500">
                      No suggestions found
                    </Text>
                  </Box>
                )}
              </VStack>
            )}
          </Box>
        )}
      </Box>

      {/* Search Controls */}
      <HStack justify="space-between">
        <Button
          colorScheme="teal"
          onClick={handleSearch}
          loading={isLoading}
          loadingText="Searching..."
          disabled={!query.trim()}
        >
          <FiSearch style={{ marginRight: "8px" }} />
          Search
        </Button>

        {/* Search Stats */}
        {searchResults && (
          <HStack fontSize="sm" color="gray.600">
            <HStack>
              <FiFileText />
              <Text>{searchResults.total_found} results</Text>
            </HStack>
            <HStack>
              <FiClock />
              <Text>{searchResults.response_time_ms}ms</Text>
            </HStack>
            <Badge colorScheme="teal" variant="subtle">
              {searchResults.search_algorithm}
            </Badge>
          </HStack>
        )}
      </HStack>

      {/* Loading State */}
      {isLoading && (
        <Flex justify="center" py={8}>
          <VStack gap={4}>
            <Spinner size="lg" color="blue.500" />
            <Text>Searching your documents...</Text>
          </VStack>
        </Flex>
      )}

      {/* Search Results */}
      {searchResults &&
        !isLoading &&
        searchResults.results &&
        searchResults.results.length > 0 && (
          <VStack gap={4} align="stretch">
            <Heading size="sm">Search Results</Heading>
            {searchResults.results.map((result: any, index: number) => (
              <Box
                key={result.chunk_id || index}
                p={4}
                bg="white"
                border="1px"
                borderColor="gray.200"
                borderRadius="md"
                cursor="pointer"
                onClick={() => handleResultClick(result)}
                _hover={{
                  bg: "gray.50",
                  borderColor: "blue.300",
                }}
              >
                <VStack align="stretch" gap={2}>
                  <HStack justify="space-between">
                    <Badge colorScheme="teal" variant="subtle">
                      Score:{" "}
                      {result.similarity_score
                        ? (result.similarity_score * 100).toFixed(1)
                        : "N/A"}
                      %
                    </Badge>
                    <Text fontSize="xs" color="gray.500">
                      Chunk {result.chunk_index || index}
                    </Text>
                  </HStack>
                  <Text fontSize="sm">
                    {result.content || "No content available"}
                  </Text>
                  {result.document_id && (
                    <Text fontSize="xs" color="gray.500">
                      Document ID: {result.document_id}
                    </Text>
                  )}
                </VStack>
              </Box>
            ))}
          </VStack>
        )}

      {/* No Results */}
      {searchResults &&
        !isLoading &&
        searchResults.results &&
        searchResults.results.length === 0 && (
          <Box p={8} textAlign="center">
            <VStack gap={4}>
              <FiSearch size={48} color="gray.400" />
              <VStack gap={2}>
                <Heading size="md" color="gray.600">
                  No results found
                </Heading>
                <Text color="gray.500">
                  Try adjusting your search terms or check your documents
                </Text>
              </VStack>
            </VStack>
          </Box>
        )}

      {/* Empty State */}
      {!searchResults && !isLoading && !query && (
        <Box p={8} textAlign="center">
          <VStack gap={4}>
            <FiSearch size={48} color="gray.400" />
            <VStack gap={2}>
              <Heading size="md" color="gray.600">
                Ready to search
              </Heading>
              <Text color="gray.500">
                Enter your search query and press Enter or click Search
              </Text>
            </VStack>
          </VStack>
        </Box>
      )}
    </VStack>
  )
}
