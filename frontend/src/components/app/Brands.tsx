/**
 * Brands Component
 *
 * Displays a list of brands for the current user in a card with a table layout.
 * Features:
 * - Table with sequence number, brand name, description, created date, and active status
 * - Active status shown as checkbox
 * - Ordered by created date (newest first)
 * - Add new brand button that shows the BrandSetupForm
 * - Data fetched from backend API with caching
 */

import { AlertCircle, Eye, Loader2, Plus, Trash2 } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"
import { type ApiConflictError, type Brand, brandsAPI } from "@/clients/brands"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import {
  type BrandEditFormData,
  BrandEditForm,
} from "@/components/app/BrandEditForm"
import {
  type BrandFormData,
  BrandSetupForm,
} from "@/components/app/BrandSetupForm"
import { QuotaGate } from "@/components/app/QuotaGate"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

/**
 * Format datetime string to display format
 */
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

export default function Brands() {
  // ============================================================================
  // State Management
  // ============================================================================

  const [brands, setBrands] = useState<Brand[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showSetupForm, setShowSetupForm] = useState(false)
  const [editingBrand, setEditingBrand] = useState<Brand | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [deletingBrand, setDeletingBrand] = useState<Brand | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [brandConflictMessage, setBrandConflictMessage] = useState<string | null>(null)

  // ============================================================================
  // Data Fetching
  // ============================================================================

  const fetchBrands = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      const data = await brandsAPI.getBrands()
      setBrands(data.brands)

      console.log("[Brands] Loaded brands:", data.total_count)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load brands"

      // Check if it's an authentication error specifically
      if (errorMessage.includes("Unauthorized") || errorMessage.includes("401")) {
        console.error("[Brands] Authentication issue detected - please log in again")
        setError("Authentication failed. Please log in again to view your brands.")
      } else {
        setError(errorMessage)
      }
      console.error("[Brands] Error:", err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchBrands()
  }, [fetchBrands])

  // ============================================================================
  // Event Handlers
  // ============================================================================

  const handleAddNewBrand = () => {
    setEditingBrand(null) // Close edit form if open
    setBrandConflictMessage(null) // Clear any previous conflict message
    setShowSetupForm(true)
  }

  const handleCancelSetup = () => {
    setShowSetupForm(false)
    setBrandConflictMessage(null)
  }

  const handleViewBrand = (brand: Brand) => {
    setShowSetupForm(false) // Close setup form if open
    setEditingBrand(brand)
  }

  const handleCancelEdit = () => {
    setEditingBrand(null)
  }

  const handleSubmitEdit = async (
    brandId: string,
    formData: BrandEditFormData,
  ) => {
    console.log("[Brands] Updating brand:", brandId, formData)

    try {
      setIsSubmitting(true)

      // Call full update API with segments
      const result = await brandsAPI.updateBrandFull(brandId, {
        brand_name: formData.brandName,
        description: formData.brandDescription || undefined,
        is_active: formData.isActive,
        segments: formData.segments
          .filter((seg) => seg.segmentName.trim() && seg.prompts.trim())
          .map((seg) => ({
            segment_name: seg.segmentName,
            prompts: seg.prompts,
          })),
      })

      toast.success(
        `Brand updated successfully! Prompts: ${result.prompt_count}`,
      )

      // Close form and refresh brand list
      setEditingBrand(null)
      const freshData = await brandsAPI.getBrands(true)
      setBrands(freshData.brands)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to update brand"
      toast.error(errorMessage)
      console.error("[Brands] Error updating brand:", err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSubmitBrand = async (formData: BrandFormData) => {
    console.log("[Brands] Submitting brand setup:", formData)

    try {
      setIsSubmitting(true)
      setBrandConflictMessage(null)

      // Transform form data to API format and call setupBrand
      const result = await brandsAPI.setupBrand({
        brand_name: formData.brandName,
        description: formData.brandDescription || undefined,
        segments: formData.segments
          .filter((seg) => seg.segmentName.trim() && seg.prompts.trim())
          .map((seg) => ({
            segment_name: seg.segmentName,
            prompts: seg.prompts,
          })),
      })

      console.log("[Brands] Brand setup completed:", result)

      toast.success(
        `Brand created successfully! Prompts: ${result.prompt_count}`,
      )

      // Hide form and refresh brand list with force refresh to bypass cache
      setShowSetupForm(false)
      const freshData = await brandsAPI.getBrands(true)
      setBrands(freshData.brands)
    } catch (err) {
      if ((err as ApiConflictError).isConflict) {
        // Brand already exists — show info box
        setBrandConflictMessage(
          err instanceof Error ? err.message : "Brand already exists"
        )
      } else {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to create brand"
        toast.error(errorMessage)
      }
      console.error("[Brands] Error setting up brand:", err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteClick = (brand: Brand) => {
    setDeletingBrand(brand)
  }

  const handleCancelDelete = () => {
    setDeletingBrand(null)
  }

  const handleConfirmDelete = async () => {
    if (!deletingBrand) return

    console.log("[Brands] Deleting brand:", deletingBrand.brand_id)

    try {
      setIsDeleting(true)

      const result = await brandsAPI.deleteBrand(deletingBrand.brand_id)

      toast.success(result.message)

      // Close dialog and refresh brand list
      setDeletingBrand(null)
      const freshData = await brandsAPI.getBrands(true)
      setBrands(freshData.brands)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to delete brand"
      toast.error(errorMessage)
      console.error("[Brands] Error deleting brand:", err)
    } finally {
      setIsDeleting(false)
    }
  }

  // ============================================================================
  // Loading State
  // ============================================================================

  if (isLoading) {
    return (
      <div className="p-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <CardTitle className="text-xl font-bold">Brand List</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center h-64">
              <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
              <p className="mt-4 text-sm text-gray-500">Loading brands...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // ============================================================================
  // Error State
  // ============================================================================

  if (error) {
    return (
      <div className="p-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <CardTitle className="text-xl font-bold">Brand List</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center h-64">
              <div className="text-red-500 text-center">
                <p className="font-medium">Failed to load brands</p>
                <p className="text-sm mt-2">{error}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // ============================================================================
  // Main Render
  // ============================================================================

  return (
    <div className="p-6">
      {/* Brand List Card */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-xl font-bold">Brand List</CardTitle>
          {!showSetupForm && !editingBrand && (
            <QuotaGate resource="brands" currentCount={brands.length}>
              <Button size="sm" onClick={handleAddNewBrand} type="button">
                <Plus className="h-4 w-4 mr-2" />
                Add New Brand
              </Button>
            </QuotaGate>
          )}
        </CardHeader>
        <CardContent>
          {brands.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-gray-500">
              <p>No brands found</p>
              <p className="text-sm mt-2">
                Click "Add New Brand" to create your first brand
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[80px]">Seq No.</TableHead>
                  <TableHead>Brand Name</TableHead>
                  <TableHead className="max-w-[300px]">Description</TableHead>
                  <TableHead className="w-[150px]">Created At</TableHead>
                  <TableHead className="w-[80px] text-center">Active</TableHead>
                  <TableHead className="w-[60px] text-center">Detail</TableHead>
                  <TableHead className="w-[60px] text-center">Delete</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {brands.map((brand, index) => (
                  <TableRow key={brand.brand_id}>
                    <TableCell className="font-medium">{index + 1}</TableCell>
                    <TableCell className="font-semibold">
                      {brand.brand_name}
                    </TableCell>
                    <TableCell className="text-gray-600 max-w-[300px] truncate">
                      {brand.description || "-"}
                    </TableCell>
                    <TableCell>{formatDate(brand.created_at)}</TableCell>
                    <TableCell className="text-center">
                      <Checkbox
                        checked={brand.is_active}
                        disabled
                        aria-label={`Brand ${brand.brand_name} is ${brand.is_active ? "active" : "inactive"}`}
                      />
                    </TableCell>
                    <TableCell className="text-center">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleViewBrand(brand)}
                        className="h-8 w-8 p-0"
                        aria-label={`View brand ${brand.brand_name} details`}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </TableCell>
                    <TableCell className="text-center">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteClick(brand)}
                        className="h-8 w-8 p-0 text-gray-400 hover:text-red-500"
                        aria-label={`Delete brand ${brand.brand_name}`}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Brand Conflict Info Box */}
      {brandConflictMessage && showSetupForm && (
        <div className="mt-4">
          <Alert className="border-amber-300 bg-amber-50">
            <AlertCircle className="h-4 w-4 text-amber-600" />
            <AlertTitle className="text-amber-800">Brand Already Exists</AlertTitle>
            <AlertDescription className="text-amber-700">
              {brandConflictMessage}
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* Brand Setup Form (shown when adding new brand) */}
      {showSetupForm && (
        <BrandSetupForm
          onCancel={handleCancelSetup}
          onSubmit={handleSubmitBrand}
        />
      )}

      {/* Brand Edit Form (shown when editing a brand) */}
      {editingBrand && (
        <BrandEditForm
          brand={editingBrand}
          onCancel={handleCancelEdit}
          onSubmit={handleSubmitEdit}
        />
      )}

      {/* Submitting Overlay */}
      {isSubmitting && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg flex items-center gap-4">
            <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
            <span>{editingBrand ? "Updating" : "Creating"} brand...</span>
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deletingBrand} onOpenChange={(open) => !open && handleCancelDelete()}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Brand</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete the brand "{deletingBrand?.brand_name}"?
              This will also delete all associated segments and prompts. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={handleCancelDelete}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={isDeleting}
            >
              {isDeleting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Deleting...
                </>
              ) : (
                "Yes, Delete"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
