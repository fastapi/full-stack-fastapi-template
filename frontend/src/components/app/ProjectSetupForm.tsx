/**
 * ProjectSetupForm Component
 *
 * Multi-step form for creating a new project with brand monitoring settings.
 * Features:
 * - Two tabs: Project Information and Brand Setting
 * - Project Information: Name and Description fields
 * - Brand Setting: Brand name and up to 3 segments with prompts
 * - Content persists when switching between tabs
 * - Save & Submit button to create the project
 */

import { Plus, Sparkles, X } from "lucide-react"
import { useState } from "react"
import { QuotaGate } from "@/components/app/QuotaGate"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
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
 * Form data structure
 */
interface ProjectFormData {
  projectName: string
  projectDescription: string
  brandName: string
  segments: Segment[]
}

/**
 * Props for the component
 */
interface ProjectSetupFormProps {
  onCancel: () => void
  onSubmit: (data: ProjectFormData) => void
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

export function ProjectSetupForm({
  onCancel,
  onSubmit,
}: ProjectSetupFormProps) {
  // ============================================================================
  // State Management
  // ============================================================================

  const [activeTab, setActiveTab] = useState<string>("project-info")

  // Form data state - persists across tab switches
  const [formData, setFormData] = useState<ProjectFormData>({
    projectName: "",
    projectDescription: "",
    brandName: "",
    segments: [
      {
        id: generateId(),
        segmentName: "",
        prompts: "",
      },
    ],
  })

  // ============================================================================
  // Event Handlers
  // ============================================================================

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
      return // Don't update if exceeds max length
    }
    setFormData((prev) => ({
      ...prev,
      [field]: value,
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
    if (formData.segments.length <= 1) return // Keep at least one segment

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
    console.log("[ProjectSetupForm] Get suggestion for segment:", segmentId)
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
    onSubmit(formData)
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
  // Render
  // ============================================================================

  return (
    <Card className="mt-6">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-xl font-bold">New Project Setup</CardTitle>
        <Button variant="ghost" size="sm" onClick={onCancel} type="button">
          <X className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="project-info">Project Information</TabsTrigger>
            <TabsTrigger value="brand-setting">Brand Setting</TabsTrigger>
          </TabsList>

          {/* ================================================================ */}
          {/* Project Information Tab */}
          {/* ================================================================ */}
          <TabsContent value="project-info" className="space-y-6">
            {/* Project Name */}
            <div className="space-y-2">
              <Label htmlFor="project-name">Project Name</Label>
              <Input
                id="project-name"
                placeholder="Enter project name"
                value={formData.projectName}
                onChange={(e) =>
                  handleProjectInfoChange("projectName", e.target.value)
                }
              />
            </div>

            {/* Project Description */}
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <Label htmlFor="project-description">Project Description</Label>
                <span className="text-xs text-gray-500">
                  {formData.projectDescription.length}/{MAX_DESCRIPTION_LENGTH}
                </span>
              </div>
              <textarea
                id="project-description"
                className="w-full min-h-[120px] px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                placeholder="Describe your project (optional)"
                value={formData.projectDescription}
                onChange={(e) =>
                  handleProjectInfoChange("projectDescription", e.target.value)
                }
                maxLength={MAX_DESCRIPTION_LENGTH}
              />
            </div>

            {/* Next Button */}
            <div className="flex justify-end pt-4">
              <Button
                onClick={handleNext}
                disabled={!formData.projectName.trim()}
                type="button"
              >
                Next
              </Button>
            </div>
          </TabsContent>

          {/* ================================================================ */}
          {/* Brand Setting Tab */}
          {/* ================================================================ */}
          <TabsContent value="brand-setting" className="space-y-6">
            {/* Brand Name */}
            <div className="space-y-2">
              <Label htmlFor="brand-name">Brand To Be Monitored</Label>
              <Input
                id="brand-name"
                placeholder="Enter brand name"
                value={formData.brandName}
                onChange={(e) => handleBrandNameChange(e.target.value)}
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
                    {formData.segments.length > 1 && (
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
                    <Label htmlFor={`segment-name-${segment.id}`}>
                      Segment
                    </Label>
                    <Input
                      id={`segment-name-${segment.id}`}
                      placeholder="Enter segment name (e.g., Consumer Electronics)"
                      value={segment.segmentName}
                      onChange={(e) =>
                        handleSegmentChange(
                          segment.id,
                          "segmentName",
                          e.target.value,
                        )
                      }
                    />
                  </div>

                  {/* Prompts Textarea */}
                  <div className="space-y-2">
                    <Label htmlFor={`segment-prompts-${segment.id}`}>
                      Prompts for Segment
                    </Label>
                    <textarea
                      id={`segment-prompts-${segment.id}`}
                      className="w-full min-h-[100px] px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                      placeholder="Enter prompts for AI search (e.g., What are the best brands for...)"
                      value={segment.prompts}
                      onChange={(e) =>
                        handleSegmentChange(
                          segment.id,
                          "prompts",
                          e.target.value,
                        )
                      }
                    />
                  </div>

                  {/* Give Me Suggestion Button */}
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

                  {/* Add Segment Button (shown at right edge of last segment if not at max) */}
                  {index === formData.segments.length - 1 &&
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

            {/* Save & Submit Button */}
            <div className="flex justify-end gap-3 pt-4 border-t">
              <Button variant="outline" onClick={onCancel} type="button">
                Cancel
              </Button>
              <Button
                onClick={handleSubmit}
                disabled={!isFormValid()}
                type="button"
              >
                Save & Submit
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

// Export the form data type for use in parent components
export type { ProjectFormData, Segment }
