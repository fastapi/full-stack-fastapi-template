import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Plus, Video, FileText, X, Eye } from "lucide-react"
import { useState } from "react"
import { ToastProvider, Toast, ToastTitle, ToastDescription, ToastViewport } from "@/components/ui/toast"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { StepPreview } from "./step-preview"
import { PathPreview } from "./path-preview"
import { YouTubePlayer } from "@/components/ui/youtube-player"
import { VideoRangeSlider } from "@/components/ui/video-range-slider"
import { extractVideoId } from "@/lib/youtube"

// Validation schema for a single step
const stepSchema = z.object({
  id: z.number(),
  title: z.string().min(1, "Titel ist erforderlich"),
  content: z.object({
    type: z.enum(["video", "text"]),
    source: z.string(),
    segment: z.object({
      start: z.number(),
      end: z.number(),
    }),
    continueFromPrevious: z.boolean(),
  }),
  rolePrompt: z.string().min(1, "Rolle ist erforderlich"),
  validationPrompt: z.string().min(1, "Validierung ist erforderlich")
})

// Validation schema for the entire path
const pathSchema = z.object({
  title: z.string().min(1, "Titel ist erforderlich"),
  pathSummary: z.string().min(1, "Lernziel ist erforderlich"),
  overallObjective: z.string().min(1, "Gesamtziel ist erforderlich"),
  interactionStyle: z.literal("chat"),
  language: z.literal("de"),
  moduleId: z.number().optional(),
  steps: z.array(stepSchema),
})

// Type for the form state
type FormStep = {
  id: number
  title: string
  content: {
    type: "video" | "text"
    source: string
    segment: {
      start: number
      end: number
    }
    continueFromPrevious: boolean
  }
  rolePrompt: string
  validationPrompt: string
}

type FormData = {
  title: string
  pathSummary: string
  overallObjective: string
  interactionStyle: "chat"
  language: "de"
  moduleId?: number
  steps: FormStep[]
}

const defaultValues: Partial<FormData> = {
  title: "",
  pathSummary: "",
  overallObjective: "",
  interactionStyle: "chat",
  language: "de",
  steps: [],
}

export function PathEditor() {
  const [previewStep, setPreviewStep] = useState<number | null>(null)
  const [showFullPreview, setShowFullPreview] = useState(false)
  const [videoDurations, setVideoDurations] = useState<Record<string, number>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [previewMode, setPreviewMode] = useState(false)
  const [showToast, setShowToast] = useState(false)

  const form = useForm<FormData>({
    resolver: zodResolver(pathSchema),
    defaultValues,
  })

  async function onSubmit(data: FormData) {
    try {
      setIsSubmitting(true)
      setError(null)
      
      const response = await fetch('/api/create/paths', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...data,
          creatorId: 1, // TODO: Get from auth context
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || 'Failed to create path')
      }

      const path = await response.json()
      
      // After creating the path, create each step
      for (const step of data.steps) {
        const stepResponse = await fetch(`/api/create/paths/${path.id}/steps`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: step.title,
            role_prompt: {
              content: step.rolePrompt
            },
            validation_prompt: {
              content: step.validationPrompt
            },
            exposition: step.content.type ? {
              type: step.content.type,
              source: step.content.source,
              segment: step.content.segment
            } : undefined
          }),
        })

        if (!stepResponse.ok) {
          throw new Error('Failed to create step')
        }
      }

      setShowToast(true)
      
      // Redirect after a short delay to show the success message
      setTimeout(() => {
        window.location.href = `/paths/${path.id}`
      }, 2000)
    } catch (error) {
      console.error('Error creating path:', error)
      setError('Fehler beim Speichern des Lernpfads. Bitte versuchen Sie es erneut.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (previewMode) {
    return (
      <PathPreview
        path={{
          title: form.getValues("title"),
          pathSummary: form.getValues("pathSummary"),
          overallObjective: form.getValues("overallObjective"),
          interactionStyle: "chat",
          language: "de",
          steps: form.getValues("steps"),
        }}
        onBack={() => setPreviewMode(false)}
      />
    )
  }

  if (showFullPreview) {
    return (
      <PathPreview
        path={form.getValues()}
        onBack={() => setShowFullPreview(false)}
      />
    )
  }

  return (
    <div className="space-y-8">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          {/* Path Information */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Pfad-Informationen</h2>
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Titel</FormLabel>
                  <FormControl>
                    <Input placeholder="Geben Sie einen Titel ein" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="pathSummary"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Lernziel</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Was sollen die Lernenden nach Abschluss dieses Pfades können?"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="overallObjective"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Gesamtziel</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Was ist das übergeordnete Ziel dieses Lernpfads?"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          {/* Steps */}
          <div className="space-y-8">
            <h2 className="text-xl font-semibold">Schritte</h2>

            {form.watch("steps").map((step, index) => (
              <div key={step.id} className="space-y-4 p-4 border rounded-lg">
                <div className="flex justify-between items-start">
                  <h3 className="text-lg font-medium">Schritt {index + 1}</h3>
                  <div className="flex items-center gap-2">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => setPreviewStep(index)}
                    >
                      <Eye className="h-4 w-4" />
                      <span className="sr-only">Vorschau</span>
                    </Button>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        const steps = form.getValues("steps")
                        form.setValue(
                          "steps",
                          steps.filter((s) => s.id !== step.id)
                        )
                      }}
                    >
                      <X className="h-4 w-4" />
                      <span className="sr-only">Löschen</span>
                    </Button>
                  </div>
                </div>

                <FormField
                  control={form.control}
                  name={`steps.${index}.title`}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Titel</FormLabel>
                      <FormControl>
                        <Input placeholder="Geben Sie einen Titel ein" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                        <Button
                          type="button"
                      variant={
                        form.watch(`steps.${index}.content.type`) === "video"
                          ? "default"
                          : "outline"
                      }
                      onClick={() =>
                        form.setValue(`steps.${index}.content.type`, "video" as const)
                      }
                        >
                          <Video className="h-4 w-4 mr-2" />
                          Video
                        </Button>
                        <Button
                          type="button"
                      variant={
                        form.watch(`steps.${index}.content.type`) === "text"
                          ? "default"
                          : "outline"
                      }
                      onClick={() =>
                        form.setValue(`steps.${index}.content.type`, "text" as const)
                      }
                        >
                          <FileText className="h-4 w-4 mr-2" />
                          Text
                        </Button>
                      </div>

                  {form.watch(`steps.${index}.content.type`) === "video" && (
                    <>
                <FormField
                  control={form.control}
                  name={`steps.${index}.content.source`}
                  render={({ field }) => (
                    <FormItem>
                            <FormLabel>YouTube URL</FormLabel>
                      <FormControl>
                          <Input
                                placeholder="https://www.youtube.com/watch?v=..."
                            {...field}
                            onChange={(e) => {
                              field.onChange(e)
                              const videoId = extractVideoId(e.target.value)
                                  if (videoId && !videoDurations[videoId]) {
                                    form.setValue(`steps.${index}.content.segment`, {
                                      start: 0,
                                      end: 0,
                                    })
                              }
                            }}
                          />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                    <FormField
                      control={form.control}
                      name={`steps.${index}.content.segment`}
                        render={({ field }) => {
                          const videoId = extractVideoId(form.watch(`steps.${index}.content.source`) || "") || ""
                          const duration = videoDurations[videoId] || 0

                          return (
                        <FormItem>
                          <FormControl>
                                <div className="space-y-4">
                                  {videoId && (
                                    <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                                      <YouTubePlayer
                                        videoId={videoId}
                                        start={field.value.start}
                                        end={field.value.end}
                                        onReady={(duration) => {
                                          setVideoDurations((prev) => ({
                                            ...prev,
                                            [videoId]: duration,
                                          }))
                                          if (field.value.end === 0) {
                                            field.onChange({
                                              ...field.value,
                                              end: duration,
                                            })
                                          }
                                        }}
                                      />
                                    </div>
                                  )}
                            <VideoRangeSlider
                                    videoId={videoId}
                                    duration={duration}
                              value={[field.value.start, field.value.end]}
                              onValueChange={([start, end]) =>
                                field.onChange({ start, end })
                              }
                            />
                                </div>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                          )
                        }}
                    />

                    <FormField
                      control={form.control}
                      name={`steps.${index}.content.continueFromPrevious`}
                      render={({ field }) => (
                        <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                          <FormControl>
                            <Checkbox
                              checked={field.value}
                              onCheckedChange={field.onChange}
                            />
                          </FormControl>
                          <div className="space-y-1 leading-none">
                            <FormLabel>
                                Vom vorherigen Zeitpunkt fortsetzen
                            </FormLabel>
                            <FormDescription>
                                Beginnt das Video dort, wo der vorherige Schritt aufgehört hat
                            </FormDescription>
                          </div>
                        </FormItem>
                      )}
                    />
                  </>
                )}

                  {form.watch(`steps.${index}.content.type`) === "text" && (
                    <FormField
                      control={form.control}
                      name={`steps.${index}.content.source`}
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Inhalt</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="Geben Sie den Inhalt ein"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  )}
                </div>

                <FormField
                  control={form.control}
                  name={`steps.${index}.rolePrompt`}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Rolle</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Welche Interaktion sollen die Lernenden haben?"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name={`steps.${index}.validationPrompt`}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Validierung</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Was ist an der Stelle ausreichendes Verständnis?"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            ))}

            <div className="flex justify-center pt-4">
            <Button
              type="button"
              onClick={() => {
                const steps = form.getValues("steps")
                form.setValue("steps", [
                  ...steps,
                  {
                      id: steps.length + 1,
                    title: "",
                    content: {
                        type: "text",
                      source: "",
                        segment: { start: 0, end: 0 },
                      continueFromPrevious: false,
                    },
                    rolePrompt: "",
                    validationPrompt: ""
                  },
                ])
              }}
                variant="outline"
                className="flex items-center gap-2"
            >
                <Plus className="h-4 w-4" />
              Schritt hinzufügen
            </Button>
          </div>
          </div>

          <div className="flex justify-between">
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Wird gespeichert..." : "Speichern"}
            </Button>
            <Button type="button" variant="outline" onClick={() => setPreviewMode(true)}>
              Vorschau
            </Button>
          </div>
        </form>
      </Form>

      {previewStep !== null && (
        <StepPreview
          open={previewStep !== null}
          onOpenChange={() => setPreviewStep(null)}
          step={form.getValues("steps")[previewStep]}
        />
      )}

      {showToast && (
        <ToastProvider>
          <Toast>
            <div className="grid gap-1">
              <ToastTitle>Erfolgreich gespeichert</ToastTitle>
              <ToastDescription>
                Der Lernpfad wurde erfolgreich erstellt.
              </ToastDescription>
            </div>
          </Toast>
          <ToastViewport />
        </ToastProvider>
      )}
    </div>
  )
}
