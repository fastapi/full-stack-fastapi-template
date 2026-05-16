import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Plus, Pencil, Trash2 } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import {
  type RaceCategoryCreate,
  type RaceCategoryPublic,
  type RaceCategoryUpdate,
  RaceCategoriesService,
} from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const categoryFormSchema = z.object({
  name: z.string().min(1, { message: "Category name is required" }),
  distance_km: z.string().min(1, { message: "Distance is required" }),
  distance_unit: z.string().optional(),
  start_time: z.string().optional(),
  end_time: z.string().optional(),
  cutoff_time_minutes: z.string().optional(),
  registration_start: z.string().optional(),
  registration_end: z.string().optional(),
  price: z.string().optional(),
  early_bird_price: z.string().optional(),
  early_bird_deadline: z.string().optional(),
  max_participants: z.string().optional(),
  min_age: z.string().optional(),
  max_age: z.string().optional(),
  gender_restriction: z.string().optional(),
  description: z.string().optional(),
  display_order: z.string().optional(),
  is_active: z.boolean().optional(),
})

type CategoryFormData = z.infer<typeof categoryFormSchema>

interface RaceCategoryManagerProps {
  raceId: string
  title?: string
  description?: string
}

const RaceCategoryManager = ({
  raceId,
  title = "Race Categories",
  description = "Manage distance categories for this race (e.g., 5K, 10K, Half Marathon, Full Marathon).",
}: RaceCategoryManagerProps) => {
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [editingCategory, setEditingCategory] = useState<RaceCategoryPublic | null>(null)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<CategoryFormData>({
    resolver: zodResolver(categoryFormSchema),
    defaultValues: {
      name: "",
      distance_km: "",
      distance_unit: "km",
      display_order: "0",
      is_active: true,
    },
  })

  // Fetch categories for this race
  const { data: categoriesData, isLoading } = useQuery({
    queryKey: ["race-categories", raceId],
    queryFn: () => RaceCategoriesService.readRaceCategories({ raceId, limit: 100 }),
  })

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: RaceCategoryCreate) =>
      RaceCategoriesService.createRaceCategory({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Category created successfully")
      setIsAddDialogOpen(false)
      form.reset()
      queryClient.invalidateQueries({ queryKey: ["race-categories", raceId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ categoryId, data }: { categoryId: string; data: RaceCategoryUpdate }) =>
      RaceCategoriesService.updateRaceCategory({ categoryId, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Category updated successfully")
      setEditingCategory(null)
      form.reset()
      queryClient.invalidateQueries({ queryKey: ["race-categories", raceId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (categoryId: string) =>
      RaceCategoriesService.deleteRaceCategory({ categoryId }),
    onSuccess: () => {
      showSuccessToast("Category deleted successfully")
      queryClient.invalidateQueries({ queryKey: ["race-categories", raceId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: CategoryFormData) => {
    // Clean up empty strings to undefined and convert numbers
    const cleanedData = {
      name: data.name,
      distance_km: Number(data.distance_km),
      distance_unit: data.distance_unit || "km",
      start_time: data.start_time || undefined,
      end_time: data.end_time || undefined,
      registration_start: data.registration_start || undefined,
      registration_end: data.registration_end || undefined,
      early_bird_deadline: data.early_bird_deadline || undefined,
      cutoff_time_minutes: data.cutoff_time_minutes ? Number(data.cutoff_time_minutes) : undefined,
      price: data.price ? Number(data.price) : undefined,
      early_bird_price: data.early_bird_price ? Number(data.early_bird_price) : undefined,
      max_participants: data.max_participants ? Number(data.max_participants) : undefined,
      min_age: data.min_age ? Number(data.min_age) : undefined,
      max_age: data.max_age ? Number(data.max_age) : undefined,
      gender_restriction: data.gender_restriction || undefined,
      description: data.description || undefined,
      display_order: data.display_order ? Number(data.display_order) : 0,
      is_active: data.is_active ?? true,
    }

    if (editingCategory) {
      updateMutation.mutate({
        categoryId: editingCategory.id,
        data: cleanedData as RaceCategoryUpdate,
      })
    } else {
      createMutation.mutate({
        ...cleanedData,
        race_id: raceId,
      } as RaceCategoryCreate)
    }
  }

  const handleEdit = (category: RaceCategoryPublic) => {
    setEditingCategory(category)
    form.reset({
      name: category.name,
      distance_km: String(category.distance_km),
      distance_unit: category.distance_unit,
      start_time: category.start_time ? new Date(category.start_time).toISOString().slice(0, 16) : "",
      end_time: category.end_time ? new Date(category.end_time).toISOString().slice(0, 16) : "",
      cutoff_time_minutes: category.cutoff_time_minutes ? String(category.cutoff_time_minutes) : "",
      registration_start: category.registration_start ? new Date(category.registration_start).toISOString().slice(0, 16) : "",
      registration_end: category.registration_end ? new Date(category.registration_end).toISOString().slice(0, 16) : "",
      price: category.price ? String(category.price) : "",
      early_bird_price: category.early_bird_price ? String(category.early_bird_price) : "",
      early_bird_deadline: category.early_bird_deadline ? new Date(category.early_bird_deadline).toISOString().slice(0, 16) : "",
      max_participants: category.max_participants ? String(category.max_participants) : "",
      min_age: category.min_age ? String(category.min_age) : "",
      max_age: category.max_age ? String(category.max_age) : "",
      gender_restriction: category.gender_restriction || "",
      description: category.description || "",
      display_order: String(category.display_order),
      is_active: category.is_active,
    })
  }

  const handleDelete = (categoryId: string) => {
    if (confirm("Are you sure you want to delete this category?")) {
      deleteMutation.mutate(categoryId)
    }
  }

  const formatPrice = (price: number | null | undefined) => {
    return price ? `${price.toLocaleString()} VND` : "—"
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">{title}</h3>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
        <Dialog open={isAddDialogOpen || !!editingCategory} onOpenChange={(open) => {
          if (!open) {
            setIsAddDialogOpen(false)
            setEditingCategory(null)
            form.reset()
          }
        }}>
          <DialogTrigger asChild>
            <Button onClick={() => setIsAddDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Category
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {editingCategory ? "Edit Category" : "Add New Category"}
              </DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem className="md:col-span-2">
                        <FormLabel>Category Name *</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g., Full Marathon, 5K" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="distance_km"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Distance *</FormLabel>
                        <FormControl>
                          <Input type="number" step="0.01" placeholder="42.195" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="distance_unit"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Distance Unit</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="km">Kilometers (km)</SelectItem>
                            <SelectItem value="mi">Miles (mi)</SelectItem>
                            <SelectItem value="m">Meters (m)</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="price"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Price (VND)</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            step="1000"
                            placeholder="300000"
                            {...field}
                            value={field.value ?? ""}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="max_participants"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Max Participants</FormLabel>
                        <FormControl>
                          <Input
                            type="number"
                            placeholder="500"
                            {...field}
                            value={field.value ?? ""}
                          />
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
                            placeholder="Describe this category..."
                            {...field}
                          />
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
                    onClick={() => {
                      setIsAddDialogOpen(false)
                      setEditingCategory(null)
                      form.reset()
                    }}
                  >
                    Cancel
                  </Button>
                  <LoadingButton
                    type="submit"
                    loading={createMutation.isPending || updateMutation.isPending}
                  >
                    {editingCategory ? "Update" : "Create"}
                  </LoadingButton>
                </div>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="text-center py-8 text-muted-foreground">Loading categories...</div>
      ) : categoriesData?.data.length === 0 ? (
        <div className="text-center py-8 border rounded-lg bg-muted/50">
          <p className="text-muted-foreground">No categories added yet.</p>
          <p className="text-sm text-muted-foreground mt-1">
            Add distance categories to allow runners to register.
          </p>
        </div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Distance</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Max Participants</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {categoriesData?.data
                .sort((a, b) => (a.display_order ?? 0) - (b.display_order ?? 0))
                .map((category) => (
                  <TableRow key={category.id}>
                    <TableCell className="font-medium">{category.name}</TableCell>
                    <TableCell>
                      {category.distance_km} {category.distance_unit}
                    </TableCell>
                    <TableCell>{formatPrice(category.price)}</TableCell>
                    <TableCell>
                      {category.max_participants || "Unlimited"}
                    </TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                          category.is_active
                            ? "bg-green-50 text-green-700"
                            : "bg-gray-50 text-gray-700"
                        }`}
                      >
                        {category.is_active ? "Active" : "Inactive"}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEdit(category)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(category.id)}
                          disabled={deleteMutation.isPending}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}

export default RaceCategoryManager
