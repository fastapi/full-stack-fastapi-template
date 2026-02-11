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

import { Loader2, Plus } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"
import { type Project, projectsAPI } from "@/clients/projects"
import {
  type ProjectFormData,
  ProjectSetupForm,
} from "@/components/app/ProjectSetupForm"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
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
  const [isSubmitting, setIsSubmitting] = useState(false)

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
      setError(errorMessage)
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
    setShowSetupForm(true)
  }

  const handleCancelSetup = () => {
    setShowSetupForm(false)
  }

  const handleSubmitProject = async (formData: ProjectFormData) => {
    console.log("[Projects] Submitting project:", formData)

    try {
      setIsSubmitting(true)

      // Create the project via API
      const result = await projectsAPI.createProject({
        project_name: formData.projectName,
        description: formData.projectDescription || undefined,
      })

      console.log("[Projects] Project created:", result)

      // TODO: Save brand settings and segments to backend
      // This will be implemented when we add the backend API for brand settings

      toast.success("Project created successfully!")

      // Hide form and refresh project list
      setShowSetupForm(false)
      await fetchProjects()
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to create project"
      toast.error(errorMessage)
      console.error("[Projects] Error creating project:", err)
    } finally {
      setIsSubmitting(false)
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
          {!showSetupForm && (
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
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Project Setup Form (shown when adding new project) */}
      {showSetupForm && (
        <ProjectSetupForm
          onCancel={handleCancelSetup}
          onSubmit={handleSubmitProject}
        />
      )}

      {/* Submitting Overlay */}
      {isSubmitting && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg flex items-center gap-4">
            <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
            <span>Creating project...</span>
          </div>
        </div>
      )}
    </div>
  )
}
