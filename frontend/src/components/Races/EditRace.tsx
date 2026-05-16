import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type RacePublic, type RaceUpdate, RacesService, ProvincesService } from "@/client"
import MediaGalleryManager from "@/components/Media/MediaGalleryManager"
import RaceCategoryManager from "@/components/Races/RaceCategoryManager"
import { RaceTranslationManager } from "@/components/Admin/RaceTranslationManager"
import { Button } from "@/components/ui/button"
import { RichTextEditor } from "@/components/ui/rich-text-editor"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const formSchema = z.object({
  name: z.string().min(1, { message: "Race name is required" }),
  description: z.string().optional(),
  event_start_date: z.string().optional(),
  event_end_date: z.string().optional(),
  location: z.string().optional(),
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

interface EditRaceProps {
  race: RacePublic
}

const EditRace = ({ race }: EditRaceProps) => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: race.name,
      description: race.description || "",
      event_start_date: race.event_start_date ? new Date(race.event_start_date).toISOString().slice(0, 16) : "",
      event_end_date: race.event_end_date ? new Date(race.event_end_date).toISOString().slice(0, 16) : "",
      location: race.location || "",
      country: race.country || "Vietnam",
      province_code: race.province_code || "",
      ward_code: race.ward_code || "",
      registration_start: race.registration_start ? new Date(race.registration_start).toISOString().slice(0, 16) : "",
      registration_end: race.registration_end ? new Date(race.registration_end).toISOString().slice(0, 16) : "",
      base_price: race.base_price || undefined,
      currency: race.currency || "VND",
      status: race.status,
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
    mutationFn: (data: RaceUpdate) =>
      RacesService.updateRace({ raceId: race.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Race updated successfully")
      navigate({ to: "/admin/races" })
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["races"] })
    },
  })

  const onSubmit = (data: FormData) => {
    // Transform empty datetime strings to undefined for proper validation
    const cleanedData = {
      ...data,
      event_start_date: data.event_start_date || undefined,
      event_end_date: data.event_end_date || undefined,
      registration_start: data.registration_start || undefined,
      registration_end: data.registration_end || undefined,
      province_code: data.province_code || undefined,
      ward_code: data.ward_code || undefined,
    }
    mutation.mutate(cleanedData as RaceUpdate)
  }

  return (
    <div className="max-w-4xl space-y-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">Edit Race</h2>
        <p className="text-muted-foreground">Update the race details below.</p>
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
                      <RichTextEditor
                        placeholder="Describe the race event..."
                        value={field.value}
                        onChange={field.onChange}
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
                    <FormLabel>Event Start Date</FormLabel>
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
                    <FormLabel>Location</FormLabel>
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
          </div>

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate({ to: "/admin/races" })}
            >
              Cancel
            </Button>
            <LoadingButton type="submit" loading={mutation.isPending}>
              Save Changes
            </LoadingButton>
          </div>
        </form>
      </Form>

      <RaceCategoryManager
        raceId={race.id}
        title="Race Categories"
        description="Manage distance categories for this race (e.g., 5K, 10K, Half Marathon, Full Marathon)."
      />

      <RaceTranslationManager raceId={race.id} race={race} />

      <MediaGalleryManager
        contentType="race"
        contentId={race.id}
        title="Race Media"
        description="Manage cover, banner, and gallery images for this race."
      />
    </div>
  )
}

export default EditRace
