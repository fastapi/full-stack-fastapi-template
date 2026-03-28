import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type RacePublic, type RaceUpdate, RacesService } from "@/client"
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
import { handleError } from "@/utils"

const formSchema = z.object({
  name: z.string().min(1, { message: "Race name is required" }),
  description: z.string().optional(),
  event_start_date: z.string().optional(),
  event_end_date: z.string().optional(),
  location: z.string().optional(),
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
      city: race.city || "",
      state: race.state || "",
      country: race.country || "USA",
      registration_start: race.registration_start ? new Date(race.registration_start).toISOString().slice(0, 16) : "",
      registration_end: race.registration_end ? new Date(race.registration_end).toISOString().slice(0, 16) : "",
      base_price: race.base_price || undefined,
      currency: race.currency || "USD",
      status: race.status,
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
    mutation.mutate(data as RaceUpdate)
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
