/**
 * ProjectEditForm Component
 *
 * Form for viewing and editing an existing project with brand monitoring settings.
 * Features:
 * - Two tabs: Project Information and Brand Setting
 * - View-only mode by default (all fields disabled)
 * - Edit button in the tab row to enable editing
 * - Project Information: Name, Description, and Active status toggle
 * - Brand Setting: Brand name and up to 3 segments with prompts
 * - Content persists when switching between tabs
 * - Loads existing data from backend on mount
 */

import { Loader2, Pencil, Plus, Sparkles, X } from "lucide-react"
import { useEffect, useState } from "react"
import {
  type Project,
  type ProjectDetailResponse,
  projectsAPI,
} from "@/clients/projects"
import { QuotaGate } from "@/components/app/QuotaGate"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

/**
 * Segment data structure
 */
interface Segment {
  id: string
  segmentName: string
  prompts: string
}

/**
 * Form data structure for editing
 */
export interface ProjectEditFormData {
  projectName: string
  projectDescription: string
  isActive: boolean
  brandName: string
  segments: Segment[]
}

/**
 * Props for the component
 */
interface ProjectEditFormProps {
  project: Project
  onCancel: () => void
  onSubmit: (projectId: string, data: ProjectEditFormData) => void
}

/**
 * Generate a unique ID for segments
 */
const generateId = (): string => {
  return `segment-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Maximum number of segments allowed
 */
const MAX_SEGMENTS = 3

/**
 * Maximum description length
 */
const MAX_DESCRIPTION_LENGTH = 255

export function ProjectEditForm({
  project,
  onCancel,
  onSubmit,
}: ProjectEditFormProps) {
  // ============================================================================
  // State Management
  // ============================================================================

  const [activeTab, setActiveTab] = useState<string>("project-info")
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [isEditMode, setIsEditMode] = useState(false)

  // Form data state - persists across tab switches
  const [formData, setFormData] = useState<ProjectEditFormData>({
    projectName: project.project_name,
    projectDescription: project.description || "",
    isActive: project.is_active,
    brandName: "",
    segments: [
      {
        id: generateId(),
        segmentName: "",
        prompts: "",
      },
    ],
  })

  // Original data for comparison and reset
  const [originalData, setOriginalData] = useState<ProjectEditFormData | null>(
    null,
  )

  // ============================================================================
  // Load Project Details
  // ============================================================================

  useEffect(() => {
    const loadProjectDetails = async () => {
      try {
        setIsLoading(true)
        setLoadError(null)

        const detail: ProjectDetailResponse = await projectsAPI.getProjectDetail(
          project.project_id,
        )

        // Transform segments from backend format
        const segments: Segment[] =
          detail.segments.length > 0
            ? detail.segments.map((seg) => ({
                id: generateId(),
                segmentName: seg.segment_name,
                prompts: seg.prompts,
              }))
            : [{ id: generateId(), segmentName: "", prompts: "" }]

        const loadedData: ProjectEditFormData = {
          projectName: detail.project_name,
          projectDescription: detail.description || "",
          isActive: detail.is_active,
          brandName: detail.brand_name || "",
          segments,
        }

        setFormData(loadedData)
        setOriginalData(loadedData)

        console.log("[ProjectEditForm] Loaded project details:", detail)
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to load project details"
        setLoadError(errorMessage)
        console.error("[ProjectEditForm] Error loading details:", err)
      } finally {
        setIsLoading(false)
      }
    }

    loadProjectDetails()
  }, [project.project_id])

  // ============================================================================
  // Event Handlers
  // ============================================================================

  /**
   * Enable edit mode
   */
  const handleEnableEdit = () => {
    setIsEditMode(true)
  }

  /**
   * Cancel editing and revert to original data
   */
  const handleCancelEdit = () => {
    if (originalData) {
      setFormData(originalData)
    }
    setIsEditMode(false)
  }

  /**
   * Update project information fields
   */
  const handleProjectInfoChange = (
    field: "projectName" | "projectDescription",
    value: string,
  ) => {
    if (
      field === "projectDescription" &&
      value.length > MAX_DESCRIPTION_LENGTH
    ) {
      return
    }
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  /**
   * Toggle active status
   */
  const handleActiveChange = (checked: boolean) => {
    setFormData((prev) => ({
      ...prev,
      isActive: checked,
    }))
  }

  /**
   * Update brand name
   */
  const handleBrandNameChange = (value: string) => {
    setFormData((prev) => ({
      ...prev,
      brandName: value,
    }))
  }

  /**
   * Update segment field
   */
  const handleSegmentChange = (
    segmentId: string,
    field: "segmentName" | "prompts",
    value: string,
  ) => {
    setFormData((prev) => ({
      ...prev,
      segments: prev.segments.map((seg) =>
        seg.id === segmentId ? { ...seg, [field]: value } : seg,
      ),
    }))
  }

  /**
   * Add a new segment
   */
  const handleAddSegment = () => {
    if (formData.segments.length >= MAX_SEGMENTS) return

    setFormData((prev) => ({
      ...prev,
      segments: [
        ...prev.segments,
        {
          id: generateId(),
          segmentName: "",
          prompts: "",
        },
      ],
    }))
  }

  /**
   * Remove a segment
   */
  const handleRemoveSegment = (segmentId: string) => {
    if (formData.segments.length <= 1) return

    setFormData((prev) => ({
      ...prev,
      segments: prev.segments.filter((seg) => seg.id !== segmentId),
    }))
  }

  /**
   * Handle "Give Me Suggestion" button click
   */
  const handleGetSuggestion = (segmentId: string) => {
    // TODO: Implement AI suggestion functionality
    console.log("[ProjectEditForm] Get suggestion for segment:", segmentId)
  }

  /**
   * Go to next tab
   */
  const handleNext = () => {
    setActiveTab("brand-setting")
  }

  /**
   * Handle form submission
   */
  const handleSubmit = () => {
    onSubmit(project.project_id, formData)
  }

  /**
   * Check if form is valid for submission
   */
  const isFormValid = (): boolean => {
    return (
      formData.projectName.trim().length > 0 &&
      formData.brandName.trim().length > 0 &&
      formData.segments.some(
        (seg) =>
          seg.segmentName.trim().length > 0 && seg.prompts.trim().length > 0,
      )
    )
  }

  // ============================================================================
  // Loading State
  // ============================================================================

  if (isLoading) {
    return (
      <Card className="mt-6">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-xl font-bold">Project Detail</CardTitle>
          <Button variant="ghost" size="sm" onClick={onCancel} type="button">
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center h-48">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            <p className="mt-4 text-sm text-gray-500">
              Loading project details...
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // ============================================================================
  // Error State
  // ============================================================================

  if (loadError) {
    return (
      <Card className="mt-6">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-xl font-bold">Project Detail</CardTitle>
          <Button variant="ghost" size="sm" onClick={onCancel} type="button">
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center h-48">
            <div className="text-red-500 text-center">
              <p className="font-medium">Failed to load project details</p>
              <p className="text-sm mt-2">{loadError}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <Card className="mt-6">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-xl font-bold">Project Detail</CardTitle>
        <Button variant="ghost" size="sm" onClick={onCancel} type="button">
          <X className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          {/* Tabs row with Edit button */}
          <div className="flex items-center justify-between mb-6">
            <TabsList className="grid w-[400px] grid-cols-2">
              <TabsTrigger value="project-info">Project Information</TabsTrigger>
              <TabsTrigger value="brand-setting">Brand Setting</TabsTrigger>
            </TabsList>
            {!isEditMode && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleEnableEdit}
                type="button"
              >
                <Pencil className="h-4 w-4 mr-2" />
                Edit
              </Button>
            )}
          </div>

          {/* ================================================================ */}
          {/* Project Information Tab */}
          {/* ================================================================ */}
          <TabsContent value="project-info" className="space-y-6">
            {/* Project Name */}
            <div className="space-y-2">
              <Label htmlFor="edit-project-name">Project Name</Label>
              <Input
                id="edit-project-name"
                placeholder="Enter project name"
                value={formData.projectName}
                onChange={(e) =>
                  handleProjectInfoChange("projectName", e.target.value)
                }
                disabled={!isEditMode}
              />
            </div>

            {/* Project Description */}
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label htmlFor="edit-project-description">
                  Project Description
                </Label>
                <span className="text-xs text-gray-500">
                  {formData.projectDescription.length}/{MAX_DESCRIPTION_LENGTH}
                </span>
              </div>
              <textarea
                id="edit-project-description"
                className="w-full min-h-[120px] px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none disabled:bg-gray-50 disabled:text-gray-500"
                placeholder="Describe your project (optional)"
                value={formData.projectDescription}
                onChange={(e) =>
                  handleProjectInfoChange("projectDescription", e.target.value)
                }
                maxLength={MAX_DESCRIPTION_LENGTH}
                disabled={!isEditMode}
              />
            </div>

            {/* Active Status Toggle */}
            <div className="flex items-center gap-4 p-4 border border-gray-200 rounded-lg">
              <Checkbox
                id="edit-is-active"
                checked={formData.isActive}
                onCheckedChange={(checked) =>
                  handleActiveChange(checked === true)
                }
                disabled={!isEditMode}
              />
              <div className="space-y-0.5">
                <Label
                  htmlFor="edit-is-active"
                  className="text-base font-medium cursor-pointer"
                >
                  Project Active
                </Label>
                <p className="text-sm text-gray-500">
                  {formData.isActive
                    ? "Project is active and visible"
                    : "Project is inactive and hidden"}
                </p>
              </div>
            </div>

            {/* Next Button - only show in edit mode */}
            {isEditMode && (
              <div className="flex justify-end pt-4">
                <Button
                  onClick={handleNext}
                  disabled={!formData.projectName.trim()}
                  type="button"
                >
                  Next
                </Button>
              </div>
            )}
          </TabsContent>

          {/* ================================================================ */}
          {/* Brand Setting Tab */}
          {/* ================================================================ */}
          <TabsContent value="brand-setting" className="space-y-6">
            {/* Brand Name */}
            <div className="space-y-2">
              <Label htmlFor="edit-brand-name">Brand To Be Monitored</Label>
              <Input
                id="edit-brand-name"
                placeholder="Enter brand name"
                value={formData.brandName}
                onChange={(e) => handleBrandNameChange(e.target.value)}
                disabled={!isEditMode}
              />
            </div>

            {/* Segments */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label className="text-base font-semibold">Segments</Label>
                <span className="text-xs text-gray-500">
                  {formData.segments.length}/{MAX_SEGMENTS} segments
                </span>
              </div>

              {formData.segments.map((segment, index) => (
                <div
                  key={segment.id}
                  className="relative border border-gray-200 rounded-lg p-4 space-y-4"
                >
                  {/* Segment Header */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">
                      Segment {index + 1}
                    </span>
                    {isEditMode && formData.segments.length > 1 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveSegment(segment.id)}
                        className="h-6 w-6 p-0 text-gray-400 hover:text-red-500"
                        type="button"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>

                  {/* Segment Name Input */}
                  <div className="space-y-2">
                    <Label htmlFor={`edit-segment-name-${segment.id}`}>
                      Segment
                    </Label>
                    <Input
                      id={`edit-segment-name-${segment.id}`}
                      placeholder="Enter segment name (e.g., Consumer Electronics)"
                      value={segment.segmentName}
                      onChange={(e) =>
                        handleSegmentChange(
                          segment.id,
                          "segmentName",
                          e.target.value,
                        )
                      }
                      disabled={!isEditMode}
                    />
                  </div>

                  {/* Prompts Textarea */}
                  <div className="space-y-2">
                    <Label htmlFor={`edit-segment-prompts-${segment.id}`}>
                      Prompts for Segment
                    </Label>
                    <textarea
                      id={`edit-segment-prompts-${segment.id}`}
                      className="w-full min-h-[100px] px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none disabled:bg-gray-50 disabled:text-gray-500"
                      placeholder="Enter prompts for AI search (e.g., What are the best brands for...)"
                      value={segment.prompts}
                      onChange={(e) =>
                        handleSegmentChange(
                          segment.id,
                          "prompts",
                          e.target.value,
                        )
                      }
                      disabled={!isEditMode}
                    />
                  </div>

                  {/* Give Me Suggestion Button - only show in edit mode */}
                  {isEditMode && (
                    <div className="flex justify-end">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleGetSuggestion(segment.id)}
                        disabled={!segment.prompts.trim()}
                        type="button"
                      >
                        <Sparkles className="h-4 w-4 mr-2" />
                        Give Me Suggestion
                      </Button>
                    </div>
                  )}

                  {/* Add Segment Button - only show in edit mode */}
                  {isEditMode &&
                    index === formData.segments.length - 1 &&
                    formData.segments.length < MAX_SEGMENTS && (
                      <QuotaGate
                        resource="segmentsPerBrand"
                        currentCount={formData.segments.length}
                        limitMessage="You've reached the segment limit for your plan. Upgrade to add more segments."
                      >
                        <TooltipProvider>
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                variant="outline"
                                size="icon"
                                className="absolute -right-4 top-1/2 -translate-y-1/2 h-8 w-8 rounded-full bg-white border-gray-300 hover:bg-blue-50 hover:border-blue-500"
                                onClick={handleAddSegment}
                                type="button"
                              >
                                <Plus className="h-4 w-4" />
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Add more segment</p>
                            </TooltipContent>
                          </Tooltip>
                        </TooltipProvider>
                      </QuotaGate>
                    )}
                </div>
              ))}
            </div>

            {/* Save & Submit Button - only show in edit mode */}
            {isEditMode && (
              <div className="flex justify-end gap-3 pt-4 border-t">
                <Button variant="outline" onClick={handleCancelEdit} type="button">
                  Cancel
                </Button>
                <Button
                  onClick={handleSubmit}
                  disabled={!isFormValid()}
                  type="button"
                >
                  Save &amp; Submit
                </Button>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
