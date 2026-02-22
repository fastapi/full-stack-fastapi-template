/**
 * Projects Component
 *
 * Displays a list of projects for the current user in a card with a table layout.
 * Features:
 * - Table with sequence number, project name, description, created date, and active status
 * - Active status shown as checkbox
 * - Ordered by created date (newest first)
 * - Add new project button that shows the ProjectSetupForm
 * - Data fetched from backend API with caching
 */

import { AlertCircle, Eye, Loader2, Plus, Trash2 } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"
import { type ApiConflictError, type Project, projectsAPI } from "@/clients/projects"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import {
  type ProjectEditFormData,
  ProjectEditForm,
} from "@/components/app/ProjectEditForm"
import {
  type ProjectFormData,
  ProjectSetupForm,
} from "@/components/app/ProjectSetupForm"
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

export default function Projects() {
  // ============================================================================
  // State Management
  // ============================================================================

  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showSetupForm, setShowSetupForm] = useState(false)
  const [editingProject, setEditingProject] = useState<Project | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [deletingProject, setDeletingProject] = useState<Project | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [brandConflictMessage, setBrandConflictMessage] = useState<string | null>(null)

  // ============================================================================
  // Data Fetching
  // ============================================================================

  const fetchProjects = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      const data = await projectsAPI.getProjects()
      setProjects(data.projects)

      console.log("[Projects] Loaded projects:", data.total_count)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load projects"
      
      // Check if it's an authentication error specifically
      if (errorMessage.includes("Unauthorized") || errorMessage.includes("401")) {
        console.error("[Projects] Authentication issue detected - please log in again")
        // Show a specific message that indicates they might need to re-login
        setError("Authentication failed. Please log in again to view your projects.")
      } else {
        setError(errorMessage)
      }
      console.error("[Projects] Error:", err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  // ============================================================================
  // Event Handlers
  // ============================================================================

  const handleAddNewProject = () => {
    setEditingProject(null) // Close edit form if open
    setBrandConflictMessage(null) // Clear any previous conflict message
    setShowSetupForm(true)
  }

  const handleCancelSetup = () => {
    setShowSetupForm(false)
    setBrandConflictMessage(null)
  }

  const handleViewProject = (project: Project) => {
    setShowSetupForm(false) // Close setup form if open
    setEditingProject(project)
  }

  const handleCancelEdit = () => {
    setEditingProject(null)
  }

  const handleSubmitEdit = async (
    projectId: string,
    formData: ProjectEditFormData,
  ) => {
    console.log("[Projects] Updating project:", projectId, formData)

    try {
      setIsSubmitting(true)

      // Call full update API with brand and segments
      const result = await projectsAPI.updateProjectFull(projectId, {
        project_name: formData.projectName,
        project_description: formData.projectDescription || undefined,
        is_active: formData.isActive,
        brand_name: formData.brandName,
        segments: formData.segments
          .filter((seg) => seg.segmentName.trim() && seg.prompts.trim())
          .map((seg) => ({
            segment_name: seg.segmentName,
            prompts: seg.prompts,
          })),
      })

      toast.success(
        `Project updated successfully! Prompts: ${result.prompt_count}`,
      )

      // Close form and refresh project list
      setEditingProject(null)
      const freshData = await projectsAPI.getProjects(true)
      setProjects(freshData.projects)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to update project"
      toast.error(errorMessage)
      console.error("[Projects] Error updating project:", err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSubmitProject = async (formData: ProjectFormData) => {
    console.log("[Projects] Submitting project setup:", formData)

    try {
      setIsSubmitting(true)
      setBrandConflictMessage(null)

      // Transform form data to API format and call setupProject
      const result = await projectsAPI.setupProject({
        project_name: formData.projectName,
        project_description: formData.projectDescription || undefined,
        brand_name: formData.brandName,
        segments: formData.segments
          .filter((seg) => seg.segmentName.trim() && seg.prompts.trim())
          .map((seg) => ({
            segment_name: seg.segmentName,
            prompts: seg.prompts,
          })),
      })

      console.log("[Projects] Project setup completed:", result)

      toast.success(
        `Project created successfully! Brand: ${result.brand_id}, Prompts: ${result.prompt_count}`,
      )

      // Hide form and refresh project list with force refresh to bypass cache
      setShowSetupForm(false)
      // Note: setupProject already clears the cache, but we fetch fresh data anyway
      const freshData = await projectsAPI.getProjects(true)
      setProjects(freshData.projects)
    } catch (err) {
      if ((err as ApiConflictError).isConflict) {
        // Brand already exists in another project — show info box
        setBrandConflictMessage(
          err instanceof Error ? err.message : "Brand already exists in another project"
        )
      } else {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to create project"
        toast.error(errorMessage)
      }
      console.error("[Projects] Error setting up project:", err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteClick = (project: Project) => {
    setDeletingProject(project)
  }

  const handleCancelDelete = () => {
    setDeletingProject(null)
  }

  const handleConfirmDelete = async () => {
    if (!deletingProject) return

    console.log("[Projects] Deleting project:", deletingProject.project_id)

    try {
      setIsDeleting(true)

      const result = await projectsAPI.deleteProject(deletingProject.project_id)

      toast.success(result.message)

      // Close dialog and refresh project list
      setDeletingProject(null)
      const freshData = await projectsAPI.getProjects(true)
      setProjects(freshData.projects)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to delete project"
      toast.error(errorMessage)
      console.error("[Projects] Error deleting project:", err)
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
            <CardTitle className="text-xl font-bold">Project List</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center h-64">
              <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
              <p className="mt-4 text-sm text-gray-500">Loading projects...</p>
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
            <CardTitle className="text-xl font-bold">Project List</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center h-64">
              <div className="text-red-500 text-center">
                <p className="font-medium">Failed to load projects</p>
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
      {/* Project List Card */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-xl font-bold">Project List</CardTitle>
          {!showSetupForm && !editingProject && (
            <Button size="sm" onClick={handleAddNewProject} type="button">
              <Plus className="h-4 w-4 mr-2" />
              Add New Project
            </Button>
          )}
        </CardHeader>
        <CardContent>
          {projects.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-gray-500">
              <p>No projects found</p>
              <p className="text-sm mt-2">
                Click "Add New Project" to create your first project
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[80px]">Seq No.</TableHead>
                  <TableHead>Project Name</TableHead>
                  <TableHead className="max-w-[300px]">Description</TableHead>
                  <TableHead className="w-[150px]">Created At</TableHead>
                  <TableHead className="w-[80px] text-center">Active</TableHead>
                  <TableHead className="w-[60px] text-center">Detail</TableHead>
                  <TableHead className="w-[60px] text-center">Delete</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {projects.map((project, index) => (
                  <TableRow key={project.project_id}>
                    <TableCell className="font-medium">{index + 1}</TableCell>
                    <TableCell className="font-semibold">
                      {project.project_name}
                    </TableCell>
                    <TableCell className="text-gray-600 max-w-[300px] truncate">
                      {project.description || "-"}
                    </TableCell>
                    <TableCell>{formatDate(project.created_at)}</TableCell>
                    <TableCell className="text-center">
                      <Checkbox
                        checked={project.is_active}
                        disabled
                        aria-label={`Project ${project.project_name} is ${project.is_active ? "active" : "inactive"}`}
                      />
                    </TableCell>
                    <TableCell className="text-center">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleViewProject(project)}
                        className="h-8 w-8 p-0"
                        aria-label={`View project ${project.project_name} details`}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </TableCell>
                    <TableCell className="text-center">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteClick(project)}
                        className="h-8 w-8 p-0 text-gray-400 hover:text-red-500"
                        aria-label={`Delete project ${project.project_name}`}
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

      {/* Project Setup Form (shown when adding new project) */}
      {showSetupForm && (
        <ProjectSetupForm
          onCancel={handleCancelSetup}
          onSubmit={handleSubmitProject}
        />
      )}

      {/* Project Edit Form (shown when editing a project) */}
      {editingProject && (
        <ProjectEditForm
          project={editingProject}
          onCancel={handleCancelEdit}
          onSubmit={handleSubmitEdit}
        />
      )}

      {/* Submitting Overlay */}
      {isSubmitting && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg flex items-center gap-4">
            <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
            <span>{editingProject ? "Updating" : "Creating"} project...</span>
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deletingProject} onOpenChange={(open) => !open && handleCancelDelete()}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Project</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete the project "{deletingProject?.project_name}"?
              This will also delete all associated brand prompts. This action cannot be undone.
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
