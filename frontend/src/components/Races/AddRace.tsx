import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { Sparkles } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type RaceCreate, type RacePublic, RacesService, ProvincesService } from "@/client"
import MediaGalleryManager from "@/components/Media/MediaGalleryManager"
import RaceCategoryManager from "@/components/Races/RaceCategoryManager"
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
  country: z.string().optional(),
  province_code: z.string().optional(),
  ward_code: z.string().optional(),
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
      country: "Vietnam",
      province_code: "",
      ward_code: "",
      currency: "VND",
      status: "draft",
    },
  })

  const selectedProvinceCode = form.watch("province_code")

  // Fetch provinces
  const { data: provincesData } = useQuery({
    queryKey: ["provinces"],
    queryFn: () => ProvincesService.readProvinces({ limit: 100 }),
  })

  // Fetch wards for selected province
  const { data: wardsData } = useQuery({
    queryKey: ["wards", selectedProvinceCode],
    queryFn: async () => {
      if (!selectedProvinceCode) {
        return { data: [], count: 0 }
      }
      return ProvincesService.readWardsByProvince({
        provinceCode: selectedProvinceCode,
        limit: 500,
      })
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

  const aiAssistMutation = useMutation({
    mutationFn: async (raceName: string) => {
      return RacesService.generateRaceDetails({ requestBody: { name: raceName } })
    },
    onSuccess: (data) => {
      showSuccessToast("AI has generated race details!")
      
      // Populate form fields with AI-generated data
      if (data.description) {
        form.setValue("description", data.description)
      }
      if (data.location) {
        form.setValue("location", data.location)
      }
      // Note: terrain_type, difficulty_level, elevation_gain_m are not part of the basic race form
      // They would need to be added to formSchema and the form if needed
    },
    onError: (error) => {
      showErrorToast("Failed to generate race details. Please try again.")
      console.error("AI assist error:", error)
    },
  })

  const handleAIAssist = () => {
    const raceName = form.getValues("name")
    if (!raceName) {
      showErrorToast("Please enter a race name first.")
      return
    }
    aiAssistMutation.mutate(raceName)
  }

  const onSubmit = (data: FormData) => {
    // Transform empty datetime strings to undefined for proper validation
    const cleanedData = {
      ...data,
      event_end_date: data.event_end_date || undefined,
      registration_start: data.registration_start || undefined,
      registration_end: data.registration_end || undefined,
      province_code: data.province_code || undefined,
      ward_code: data.ward_code || undefined,
    }
    mutation.mutate(cleanedData as RaceCreate)
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
                    <div className="flex items-center justify-between">
                      <FormLabel>Race Name *</FormLabel>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={handleAIAssist}
                        disabled={aiAssistMutation.isPending}
                        className="gap-2"
                      >
                        <Sparkles className="h-4 w-4" />
                        {aiAssistMutation.isPending ? "Generating..." : "AI Assist"}
                      </Button>
                    </div>
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
                name="country"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Country</FormLabel>
                    <FormControl>
                      <Input placeholder="Vietnam" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="province_code"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Province/City (Optional)</FormLabel>
                    <Select
                      onValueChange={(value) => {
                        field.onChange(value)
                        form.setValue("ward_code", "") // Reset ward when province changes
                      }}
                      value={field.value || undefined}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select province" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {provincesData?.data?.map((province) => (
                          <SelectItem key={province.code} value={province.code}>
                            {province.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="ward_code"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>District/Ward (Optional)</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      value={field.value || undefined}
                      disabled={!selectedProvinceCode}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder={selectedProvinceCode ? "Select district/ward" : "Select province first"} />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {wardsData?.data?.map((ward) => (
                          <SelectItem key={ward.code} value={ward.code}>
                            {ward.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
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
        <div className="mt-8 space-y-8">
          <RaceCategoryManager
            raceId={createdRaceId}
            title={`Categories${createdRaceName ? ` for ${createdRaceName}` : ""}`}
            description="Add distance categories (e.g., 5K, 10K, Marathon) for runners to register."
          />
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
