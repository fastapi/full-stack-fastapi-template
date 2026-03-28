import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type RaceCreate, type RacePublic, RacesService } from "@/client"
import MediaGalleryManager from "@/components/Media/MediaGalleryManager"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { uploadMediaAsset } from "@/lib/media-api"
import { handleError } from "@/utils"

const formSchema = z.object({
  name: z.string().min(1, { message: "Race name is required" }),
  description: z.string().optional(),
  event_start_date: z.string().min(1, { message: "Start date is required" }),
  event_end_date: z.string().optional(),
  location: z.string().min(1, { message: "Location is required" }),
  city: z.string().optional(),
  state: z.string().optional(),
  country: z.string().optional(),
  registration_start: z.string().optional(),
  registration_end: z.string().optional(),
  base_price: z.coerce.number().min(0).optional(),
  currency: z.string().optional(),
  status: z.enum(["draft", "published", "registration_open", "registration_closed", "completed", "cancelled"]).optional(),
})

type FormData = z.infer<typeof formSchema>

const AddRace = () => {
  const navigate = useNavigate()
  const [createdRaceId, setCreatedRaceId] = useState<string | null>(null)
  const [createdRaceName, setCreatedRaceName] = useState<string>("")
  const [coverFile, setCoverFile] = useState<File | null>(null)
  const [bannerFile, setBannerFile] = useState<File | null>(null)
  const [galleryFiles, setGalleryFiles] = useState<File[]>([])
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
      description: "",
      location: "",
      city: "",
      state: "",
      country: "USA",
      currency: "USD",
      status: "draft",
    },
  })

  const mutation = useMutation({
    mutationFn: async (
      data: RaceCreate
    ): Promise<{ race: RacePublic; mediaUploadFailed: boolean }> => {
      const race = await RacesService.createRace({ requestBody: data })
      let mediaUploadFailed = false

      try {
        const uploads: Promise<unknown>[] = []

        if (coverFile) {
          uploads.push(
            uploadMediaAsset({
              file: coverFile,
              contentType: "race",
              contentId: race.id,
              kind: "cover",
              isPrimary: true,
            })
          )
        }

        if (bannerFile) {
          uploads.push(
            uploadMediaAsset({
              file: bannerFile,
              contentType: "race",
              contentId: race.id,
              kind: "banner",
              isPrimary: true,
            })
          )
        }

        galleryFiles.forEach((file, index) => {
          uploads.push(
            uploadMediaAsset({
              file,
              contentType: "race",
              contentId: race.id,
              kind: "gallery",
              displayOrder: index,
            })
          )
        })

        if (uploads.length > 0) {
          await Promise.all(uploads)
        }
      } catch {
        mediaUploadFailed = true
      }

      return { race, mediaUploadFailed }
    },
    onSuccess: ({ race, mediaUploadFailed }) => {
      if (mediaUploadFailed) {
        showErrorToast("Race was created, but some images could not be uploaded.")
      } else {
        showSuccessToast("Race and images saved successfully.")
      }

      setCreatedRaceId(race.id)
      setCreatedRaceName(race.name)
      setCoverFile(null)
      setBannerFile(null)
      setGalleryFiles([])
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["races"] })
    },
  })

  const onSubmit = (data: FormData) => {
    mutation.mutate(data as RaceCreate)
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">Add New Race</h2>
        <p className="text-muted-foreground">
          Create a new race event. Fill in the details below.
        </p>
      </div>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem className="md:col-span-2">
                    <FormLabel>Race Name *</FormLabel>
                    <FormControl>
                      <Input placeholder="City Marathon 2026" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem className="md:col-span-2">
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Describe the race event..."
                        className="min-h-[100px]"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="event_start_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Event Start Date *</FormLabel>
                    <FormControl>
                      <Input type="datetime-local" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="event_end_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Event End Date</FormLabel>
                    <FormControl>
                      <Input type="datetime-local" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="location"
                render={({ field }) => (
                  <FormItem className="md:col-span-2">
                    <FormLabel>Location *</FormLabel>
                    <FormControl>
                      <Input placeholder="Main Street, Downtown" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="city"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>City</FormLabel>
                    <FormControl>
                      <Input placeholder="Boston" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="state"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>State</FormLabel>
                    <FormControl>
                      <Input placeholder="Massachusetts" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="country"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Country</FormLabel>
                    <FormControl>
                      <Input placeholder="USA" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="status"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Status</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select status" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="draft">Draft</SelectItem>
                        <SelectItem value="published">Published</SelectItem>
                        <SelectItem value="registration_open">Registration Open</SelectItem>
                        <SelectItem value="registration_closed">Registration Closed</SelectItem>
                        <SelectItem value="completed">Completed</SelectItem>
                        <SelectItem value="cancelled">Cancelled</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="registration_start"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Registration Start</FormLabel>
                    <FormControl>
                      <Input type="datetime-local" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="registration_end"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Registration End</FormLabel>
                    <FormControl>
                      <Input type="datetime-local" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="base_price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Base Price</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="50.00"
                        name={field.name}
                        ref={field.ref}
                        onBlur={field.onBlur}
                        value={typeof field.value === "number" ? field.value : ""}
                        onChange={(event) => {
                          const value = event.target.value
                          field.onChange(value === "" ? undefined : Number(value))
                        }}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="currency"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Currency</FormLabel>
                    <FormControl>
                      <Input placeholder="USD" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="md:col-span-2 space-y-4 rounded-lg border p-4">
                <h3 className="text-sm font-semibold">Images (saved on race creation)</h3>

                <div className="space-y-2">
                  <FormLabel>Cover Image</FormLabel>
                  <Input
                    type="file"
                    accept="image/*"
                    onChange={(event) => {
                      const file = event.target.files?.[0] || null
                      setCoverFile(file)
                    }}
                  />
                  {coverFile ? (
                    <p className="text-xs text-muted-foreground">Selected: {coverFile.name}</p>
                  ) : null}
                </div>

                <div className="space-y-2">
                  <FormLabel>Banner Image</FormLabel>
                  <Input
                    type="file"
                    accept="image/*"
                    onChange={(event) => {
                      const file = event.target.files?.[0] || null
                      setBannerFile(file)
                    }}
                  />
                  {bannerFile ? (
                    <p className="text-xs text-muted-foreground">Selected: {bannerFile.name}</p>
                  ) : null}
                </div>

                <div className="space-y-2">
                  <FormLabel>Gallery Images</FormLabel>
                  <Input
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={(event) => {
                      const files = Array.from(event.target.files || [])
                      setGalleryFiles(files)
                    }}
                  />
                  {galleryFiles.length > 0 ? (
                    <p className="text-xs text-muted-foreground">
                      {galleryFiles.length} file(s) selected
                    </p>
                  ) : null}
                </div>
              </div>
          </div>

          <div className="flex justify-end gap-2">
            {createdRaceId ? (
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  form.reset()
                  setCreatedRaceId(null)
                  setCreatedRaceName("")
                  setCoverFile(null)
                  setBannerFile(null)
                  setGalleryFiles([])
                }}
              >
                Create Another Race
              </Button>
            ) : null}
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate({ to: "/admin/races" })}
            >
              Cancel
            </Button>
            <LoadingButton type="submit" loading={mutation.isPending}>
              Create Race
            </LoadingButton>
          </div>
        </form>
      </Form>

      {createdRaceId ? (
        <div className="mt-8">
          <MediaGalleryManager
            contentType="race"
            contentId={createdRaceId}
            title={`Race Media${createdRaceName ? `: ${createdRaceName}` : ""}`}
            description="Manage cover, banner, and gallery images for this new race."
          />
        </div>
      ) : null}
    </div>
  )
}

export default AddRace
