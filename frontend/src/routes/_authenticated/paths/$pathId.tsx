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
  SkeletonText,
} from "@chakra-ui/react"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useQuery } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { useState } from "react"
import { z } from "zod"
import { zodResolver } from "@hookform/resolvers/zod"
import { AddIcon, DeleteIcon, ViewIcon } from "@chakra-ui/icons"
import { YouTubePlayer } from "../../../components/Common/YouTubePlayer"
import { extractVideoId } from "../../../utils/youtube"
import { VideoRangeSlider } from "../../../components/Common/VideoRangeSlider"
import { PathCreate, StepCreate, PathsService } from "../../../client"
import useCustomToast from "../../../hooks/useCustomToast"

const stepSchema = z.object({
  rolePrompt: z.string().optional(),
  validationPrompt: z.string().optional(),
  content: z.discriminatedUnion('type', [
    z.object({
      type: z.literal('video'),
      source: z.string(),  // Required for video
      segment: z.object({
        start: z.number(),
        end: z.number()
      })
    }),
    z.object({
      type: z.literal('text'),
      source: z.string().optional(),
      segment: z.object({
        start: z.number(),
        end: z.number()
      })
    }),
    z.object({
      type: z.literal('none'),
      source: z.string().optional(),
      segment: z.object({
        start: z.number(),
        end: z.number()
      })
    })
  ])
})

const formSchema = z.object({
  title: z.string().min(1, "Title is required"),
  pathSummary: z.string().optional(),
  steps: z.array(stepSchema)
})

type FormData = z.infer<typeof formSchema>

const transformFormToApi = (formData: FormData): PathCreate => {
  return {
    title: formData.title,
    path_summary: formData.pathSummary,
    steps: formData.steps.map((step, index): StepCreate => ({
      number: index + 1,
      role_prompt: step.rolePrompt,
      validation_prompt: step.validationPrompt,
      exposition: step.content.type === "video" ? {
        url: step.content.source,
        start_time: step.content.segment.start,
        end_time: step.content.segment.end
      } : null
    }))
  }
}

export const Route = createFileRoute("/_authenticated/paths/$pathId")({
  component: EditPath,
  parseParams: (rawParams: Record<string, string>) => ({
    pathId: z.string().parse(rawParams.pathId),
  }),
})

function EditPath() {
  const { pathId } = Route.useParams()
  const navigate = useNavigate()
  const toast = useCustomToast()
  const [videoDurations, setVideoDurations] = useState<Record<number, number>>({})
  
  const { data: currentPath, isLoading } = useQuery({
    queryKey: ["path", pathId],
    queryFn: () => PathsService.getPath({ pathId }).then(data => {
      console.log('=== API Response ===', data);
      return data;
    }),
  })

  console.log('=== Current Path ===', currentPath);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    values: currentPath ? {
      title: currentPath.title,
      pathSummary: currentPath.path_summary ?? "",
      steps: currentPath.steps.map(step => {
        // Check if exposition exists and has the expected shape
        const hasExposition = step.exposition !== null && 
                            typeof step.exposition === 'object' &&
                            'url' in step.exposition;
        console.log('=== Step Data ===', {
          step,
          hasExposition,
          exposition: step.exposition
        });
        return {
          rolePrompt: step.role_prompt ?? "",
          validationPrompt: step.validation_prompt ?? "",
          content: hasExposition && step.exposition ? {
            type: "video" as const,
            source: step.exposition.url,
            segment: {
              start: step.exposition.start_time ?? 0,
              end: step.exposition.end_time ?? 0
            }
          } : {
            type: "none" as const,
            source: "",
            segment: { start: 0, end: 0 }
          }
        }
      })
    } : undefined
  })

  const steps = watch("steps") || []
  console.log('=== Form Values ===', { steps });

  const addStep = () => {
    const newStep = {
      rolePrompt: "",
      validationPrompt: "",
      content: {
        type: "none" as const,
        source: "",
        segment: {
          start: 0,
          end: 0,
        },
      }
    }
    setValue("steps", [...steps, newStep])
  }

  const removeStep = (stepId: number) => {
    setValue(
      "steps",
      steps.filter((_, index) => index !== stepId)
    )
  }

  const getStepContentType = (index: number) => {
    return watch(`steps.${index}.content.type`) as "video" | "text" | "none"
  }

  const onSubmit = async (data: FormData) => {
    console.log('Form submitted with data:', data)
    try {
      const apiData = transformFormToApi(data)
      console.log('Transformed API data:', apiData)
      await PathsService.updatePath({ 
        pathId,
        requestBody: apiData
      })
      
      toast(
        "Success",
        "Learning path updated successfully",
        "success"
      )
      navigate({ to: "/paths" })
    } catch (error) {
      console.error('Error updating path:', error)
      toast(
        "Error",
        "Failed to update learning path",
        "error"
      )
    }
  }

  if (isLoading) {
    return (
      <Container maxW="container.xl">
        <VStack spacing={8} align="stretch">
          <SkeletonText noOfLines={1} skeletonHeight="40px" />
          <SkeletonText noOfLines={4} spacing="4" />
        </VStack>
      </Container>
    )
  }

  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Edit Learning Path
      </Heading>

      <Box py={8}>
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

                <FormControl isInvalid={!!errors.pathSummary}>
                  <FormLabel>Summary</FormLabel>
                  <Textarea
                    {...register("pathSummary")}
                    placeholder="Enter path summary"
                    rows={3}
                  />
                  <FormErrorMessage>
                    {errors.pathSummary?.message}
                  </FormErrorMessage>
                </FormControl>
              </VStack>
            </Box>

            <Divider />

            {/* Steps Section */}
            <Box>
              <Heading size="md" mb={4}>Steps</Heading>

              <VStack spacing={4} align="stretch">
                {steps.map((_, index) => (
                  <Box
                    key={index}
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
                          onClick={() => removeStep(index)}
                        />
                      </HStack>
                    </HStack>

                    <VStack spacing={4} align="stretch">
                      {/* Exposition Section */}
                      <Box>
                        <FormLabel>Exposition</FormLabel>
                        <HStack spacing={2}>
                          <Button
                            size="sm"
                            variant={getStepContentType(index) === "none" ? "primary" : "outline"}
                            onClick={() => {
                              setValue(`steps.${index}.content.type`, "none")
                              setValue(`steps.${index}.content.source`, "")
                            }}
                          >
                            None
                          </Button>
                          <Button
                            size="sm"
                            variant={getStepContentType(index) === "video" ? "primary" : "outline"}
                            onClick={() => {
                              setValue(`steps.${index}.content.type`, "video")
                              // Only clear source if we're not already in video mode
                              if (getStepContentType(index) !== "video") {
                                setValue(`steps.${index}.content.source`, "")
                              }
                            }}
                          >
                            Video
                          </Button>
                          <Button
                            size="sm"
                            variant={getStepContentType(index) === "text" ? "primary" : "outline"}
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
                      {getStepContentType(index) === "video" && (
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

                      {getStepContentType(index) === "text" && (
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
                  variant="primary"
                  size="md"
                  alignSelf="center"
                  mt={2}
                >
                  Add Step
                </Button>
              </VStack>
            </Box>

            <Button
              type="submit"
              variant="primary"
              isLoading={isSubmitting}
              alignSelf="flex-start"
            >
              Update Path
            </Button>
          </VStack>
        </form>
      </Box>
    </Container>
  )
}
