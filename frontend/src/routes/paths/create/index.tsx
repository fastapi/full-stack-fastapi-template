import {
  Box,
  Button,
  Container,
  Divider,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Heading,
  HStack,
  IconButton,
  Input,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useForm } from "react-hook-form"
import { useState } from "react"
import { z } from "zod"
import { zodResolver } from "@hookform/resolvers/zod"
import { AddIcon, DeleteIcon, ViewIcon } from "@chakra-ui/icons"
import { YouTubePlayer } from "../../../components/Common/YouTubePlayer"
import { extractVideoId } from "../../../utils/youtube"
import { VideoRangeSlider } from "../../../components/Common/VideoRangeSlider"

const stepSchema = z.object({
  id: z.number(),
  title: z.string().min(1, "Title is required"),
  content: z.object({
    type: z.enum(["video", "text", "none"]),
    source: z.string(),
    segment: z.object({
      start: z.number().min(0),
      end: z.number().min(0),
    }).optional(),
  }),
  rolePrompt: z.string().min(1, "Role prompt is required"),
  validationPrompt: z.string().min(1, "Validation prompt is required"),
})

const createPathSchema = z.object({
  title: z.string().min(1, "Title is required"),
  path_summary: z.string().min(1, "Summary is required"),
  steps: z.array(stepSchema),
})

type CreatePathInput = z.infer<typeof createPathSchema>

export const Route = createFileRoute("/paths/create/")({
  component: CreatePath,
  validateSearch: () => ({}),
})

function CreatePath() {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<CreatePathInput>({
    resolver: zodResolver(createPathSchema),
    defaultValues: {
      title: "",
      path_summary: "",
      steps: [],
    },
  })

  const steps = watch("steps") || []

  const addStep = () => {
    const newStep = {
      id: Date.now(),
      title: "",
      content: {
        type: "none" as const,
        source: "",
        segment: {
          start: 0,
          end: 0,
        },
      },
      rolePrompt: "",
      validationPrompt: "",
    }
    setValue("steps", [...steps, newStep])
  }

  const removeStep = (stepId: number) => {
    setValue(
      "steps",
      steps.filter((step) => step.id !== stepId)
    )
  }

  const [videoDurations, setVideoDurations] = useState<Record<number, number>>({})

  const onSubmit = async (data: CreatePathInput) => {
    try {
      // TODO: Implement path creation
      console.log("Form data:", data)
    } catch (error) {
      console.error("Error creating path:", error)
    }
  }

  return (
    <Container maxW="container.xl">
      <VStack spacing={8} align="stretch">
        <Heading>Create New Path</Heading>

        <form onSubmit={handleSubmit(onSubmit)}>
          <VStack spacing={8} align="stretch">
            {/* Path Information */}
            <Box>
              <Heading size="md" mb={4}>Path Information</Heading>
              <VStack spacing={4} align="stretch">
                <FormControl isInvalid={!!errors.title}>
                  <FormLabel>Title</FormLabel>
                  <Input
                    {...register("title")}
                    placeholder="Enter path title"
                  />
                  <FormErrorMessage>
                    {errors.title?.message}
                  </FormErrorMessage>
                </FormControl>

                <FormControl isInvalid={!!errors.path_summary}>
                  <FormLabel>Summary</FormLabel>
                  <Textarea
                    {...register("path_summary")}
                    placeholder="Enter path summary"
                    rows={3}
                  />
                  <FormErrorMessage>
                    {errors.path_summary?.message}
                  </FormErrorMessage>
                </FormControl>
              </VStack>
            </Box>

            <Divider />

            {/* Steps Section */}
            <Box>
              <Heading size="md" mb={4}>Steps</Heading>

              <VStack spacing={4} align="stretch">
                {steps.map((step, index) => (
                  <Box
                    key={step.id}
                    p={4}
                    borderWidth={1}
                    borderRadius="md"
                    position="relative"
                  >
                    <HStack justify="space-between" mb={4}>
                      <Heading size="sm">Step {index + 1}</Heading>
                      <HStack>
                        <IconButton
                          icon={<ViewIcon />}
                          aria-label="Preview step"
                          variant="ghost"
                          size="sm"
                        />
                        <IconButton
                          icon={<DeleteIcon />}
                          aria-label="Remove step"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeStep(step.id)}
                        />
                      </HStack>
                    </HStack>

                    <VStack spacing={4} align="stretch">
                      <FormControl
                        isInvalid={!!errors.steps?.[index]?.title}
                      >
                        <FormLabel>Title</FormLabel>
                        <Input
                          {...register(`steps.${index}.title`)}
                          placeholder="Enter step title"
                        />
                        <FormErrorMessage>
                          {errors.steps?.[index]?.title?.message}
                        </FormErrorMessage>
                      </FormControl>

                      {/* Exposition Section */}
                      <Box>
                        <FormLabel>Exposition</FormLabel>
                        <HStack spacing={2}>
                          <Button
                            size="sm"
                            variant={watch(`steps.${index}.content.type`) === "none" ? "solid" : "outline"}
                            colorScheme="blue"
                            onClick={() => {
                              setValue(`steps.${index}.content.type`, "none")
                              setValue(`steps.${index}.content.source`, "")
                            }}
                          >
                            None
                          </Button>
                          <Button
                            size="sm"
                            variant={watch(`steps.${index}.content.type`) === "video" ? "solid" : "outline"}
                            colorScheme="blue"
                            onClick={() => {
                              setValue(`steps.${index}.content.type`, "video")
                              setValue(`steps.${index}.content.source`, "")
                            }}
                          >
                            Video
                          </Button>
                          <Button
                            size="sm"
                            variant={watch(`steps.${index}.content.type`) === "text" ? "solid" : "outline"}
                            colorScheme="blue"
                            onClick={() => {
                              setValue(`steps.${index}.content.type`, "text")
                              setValue(`steps.${index}.content.source`, "")
                            }}
                          >
                            Text
                          </Button>
                        </HStack>
                      </Box>

                      {/* Conditional Content Input */}
                      {watch(`steps.${index}.content.type`) === "video" && (
                        <VStack spacing={2} mt={4} align="stretch">
                          <FormControl>
                            <FormLabel>YouTube URL</FormLabel>
                            <Input
                              {...register(`steps.${index}.content.source`)}
                              placeholder="Enter YouTube URL"
                            />
                          </FormControl>
                          {/* YouTube Player */}
                          {(() => {
                            const url = watch(`steps.${index}.content.source`)
                            const videoId = url ? extractVideoId(url) : null
                            if (!videoId) return null
                            
                            return (
                              <Box mt={2}>
                                <YouTubePlayer
                                  videoId={videoId}
                                  start={watch(`steps.${index}.content.segment.start`)}
                                  end={watch(`steps.${index}.content.segment.end`)}
                                  onReady={(duration: number) => {
                                    setVideoDurations(prev => ({ ...prev, [index]: duration }))
                                    // If end time isn't set, set it to video duration
                                    if (!watch(`steps.${index}.content.segment.end`)) {
                                      setValue(`steps.${index}.content.segment.end`, Math.floor(duration))
                                    }
                                  }}
                                />
                              </Box>
                            )
                          })()}
                          <FormControl mt={8}>
                            {(() => {
                              const url = watch(`steps.${index}.content.source`)
                              const videoId = url ? extractVideoId(url) : null
                              if (!videoId) return null

                              return (
                                <VideoRangeSlider
                                  duration={videoDurations[index] || 0}
                                  start={watch(`steps.${index}.content.segment.start`) || 0}
                                  end={watch(`steps.${index}.content.segment.end`) || videoDurations[index] || 0}
                                  onChange={(start, end) => {
                                    setValue(`steps.${index}.content.segment.start`, start)
                                    setValue(`steps.${index}.content.segment.end`, end)
                                  }}
                                />
                              )
                            })()}
                          </FormControl>
                        </VStack>
                      )}

                      {watch(`steps.${index}.content.type`) === "text" && (
                        <FormControl mt={4}>
                          <FormLabel>Expositional Text</FormLabel>
                          <Textarea
                            {...register(`steps.${index}.content.source`)}
                            placeholder="Enter expositional text"
                            rows={4}
                          />
                        </FormControl>
                      )}
                      <FormControl
                        isInvalid={!!errors.steps?.[index]?.rolePrompt}
                      >
                        <FormLabel>Role Prompt</FormLabel>
                        <Textarea
                          {...register(`steps.${index}.rolePrompt`)}
                          placeholder="Enter role prompt"
                          rows={2}
                        />
                        <FormErrorMessage>
                          {errors.steps?.[index]?.rolePrompt?.message}
                        </FormErrorMessage>
                      </FormControl>

                      <FormControl
                        isInvalid={!!errors.steps?.[index]?.validationPrompt}
                      >
                        <FormLabel>Validation Prompt</FormLabel>
                        <Textarea
                          {...register(`steps.${index}.validationPrompt`)}
                          placeholder="Enter validation prompt"
                          rows={2}
                        />
                        <FormErrorMessage>
                          {errors.steps?.[index]?.validationPrompt?.message}
                        </FormErrorMessage>
                      </FormControl>
                    </VStack>
                  </Box>
                ))}
                <Button
                  leftIcon={<AddIcon />}
                  onClick={addStep}
                  colorScheme="blue"
                  variant="outline"
                  alignSelf="center"
                  mt={2}
                >
                  Add Step
                </Button>
              </VStack>
            </Box>

            <Button
              type="submit"
              colorScheme="blue"
              isLoading={isSubmitting}
              alignSelf="flex-start"
            >
              Create Path
            </Button>
          </VStack>
        </form>
      </VStack>
    </Container>
  )
}
