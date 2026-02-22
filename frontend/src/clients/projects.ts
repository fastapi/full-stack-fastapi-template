/**
 * Projects API Client
 *
 * This module provides API client methods for managing projects.
 * Includes built-in caching functionality to minimize API calls.
 */

import { getAuthToken } from "./auth-helper"

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
const API_PREFIX = "/api/v1"

// Cache configuration
const CACHE_EXPIRATION_HOURS = 10
const CACHE_KEY_PROJECTS = "projects_list"

/**
 * Interface for cached data wrapper
 */
interface CachedData<T> {
  data: T
  timestamp: number
}

/**
 * Response interface for a single project
 */
export interface Project {
  project_id: string
  project_name: string
  description: string | null
  company_id: string | null
  created_by: string
  created_at: string // ISO datetime string
  is_active: boolean
}

/**
 * Response interface for project list
 */
export interface ProjectListResponse {
  projects: Project[]
  total_count: number
}

/**
 * Request interface for creating a project (simple)
 */
export interface ProjectCreateRequest {
  project_name: string
  description?: string
  company_id?: string
}

/**
 * Response interface for project creation
 */
export interface ProjectCreateResponse {
  project_id: string
  message: string
}

/**
 * Segment data for project setup
 */
export interface SegmentData {
  segment_name: string
  prompts: string
}

/**
 * Request interface for complete project setup
 */
export interface ProjectSetupRequest {
  project_name: string
  project_description?: string
  brand_name: string
  segments: SegmentData[]
}

/**
 * Response interface for project setup
 */
export interface ProjectSetupResponse {
  project_id: string
  brand_id: string
  prompt_count: number
  message: string
}

/**
 * Request interface for updating a project
 */
export interface ProjectUpdateRequest {
  project_name?: string
  description?: string
  is_active?: boolean
}

/**
 * Response interface for project update
 */
export interface ProjectUpdateResponse {
  project_id: string
  message: string
}

/**
 * Segment detail from backend
 */
export interface SegmentDetail {
  prompt_id: string
  segment_name: string
  prompts: string
  is_active: boolean
}

/**
 * Response interface for project details including brand and prompts
 */
export interface ProjectDetailResponse {
  project_id: string
  project_name: string
  description: string | null
  company_id: string | null
  created_by: string
  created_at: string
  is_active: boolean
  brand_id: string | null
  brand_name: string | null
  segments: SegmentDetail[]
}

/**
 * Request interface for full project update
 */
export interface ProjectFullUpdateRequest {
  project_name: string
  project_description?: string
  is_active: boolean
  brand_name: string
  segments: SegmentData[]
}

/**
 * Standard API error response
 */
export interface ApiError {
  detail: string
}

/**
 * Error type for 409 Conflict responses (e.g. brand already exists)
 */
export interface ApiConflictError extends Error {
  isConflict: boolean
}

/**
 * Projects API Client Class
 */
class ProjectsAPI {
  private readonly baseUrl: string
  private readonly apiPrefix: string

  constructor(baseUrl: string = API_BASE_URL, apiPrefix: string = API_PREFIX) {
    this.baseUrl = baseUrl
    this.apiPrefix = apiPrefix
  }

  /**
   * Get authorization headers
   */
  private async getAuthHeaders(): Promise<HeadersInit> {
    const token = await getAuthToken()
    return {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    }
  }

  /**
   * Check if cached data is still valid
   */
  private isCacheValid(timestamp: number): boolean {
    const now = Date.now()
    const expirationMs = CACHE_EXPIRATION_HOURS * 60 * 60 * 1000
    return now - timestamp < expirationMs
  }

  /**
   * Retrieve cached data from localStorage
   */
  private getCachedData<T>(key: string): T | null {
    try {
      const cachedString = localStorage.getItem(key)
      if (!cachedString) return null

      const cached: CachedData<T> = JSON.parse(cachedString)
      if (this.isCacheValid(cached.timestamp)) {
        console.log(`[ProjectsAPI] Using cached data for key: ${key}`)
        return cached.data
      }

      localStorage.removeItem(key)
      return null
    } catch {
      localStorage.removeItem(key)
      return null
    }
  }

  /**
   * Store data in localStorage cache
   */
  private setCachedData<T>(key: string, data: T): void {
    try {
      const cached: CachedData<T> = {
        data,
        timestamp: Date.now(),
      }
      localStorage.setItem(key, JSON.stringify(cached))
      console.log(`[ProjectsAPI] Data cached for key: ${key}`)
    } catch (error) {
      console.error(`[ProjectsAPI] Error caching data: ${error}`)
    }
  }

  /**
   * Clear projects cache
   */
  public clearCache(): void {
    localStorage.removeItem(CACHE_KEY_PROJECTS)
    console.log("[ProjectsAPI] Cache cleared")
  }

  /**
   * Fetch list of projects for the current user
   *
   * @param forceRefresh - If true, bypasses cache
   * @returns ProjectListResponse with projects array
   */
  async getProjects(forceRefresh: boolean = false): Promise<ProjectListResponse> {
    // Check cache first
    if (!forceRefresh) {
      const cached = this.getCachedData<ProjectListResponse>(CACHE_KEY_PROJECTS)
      if (cached) {
        return cached
      }
    }

    console.log("[ProjectsAPI] Fetching projects from API...")

    const url = `${this.baseUrl}${this.apiPrefix}/projects`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      // In case the token was invalidated
      console.error("[ProjectsAPI] Authentication failed, clearing cache and trying again...")
      this.clearCache()
      // Retry once with fresh headers and force refresh
      return await this.getProjects(true)
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch projects")
    }

    const data: ProjectListResponse = await response.json()

    // Cache the result
    this.setCachedData(CACHE_KEY_PROJECTS, data)

    console.log(`[ProjectsAPI] Fetched ${data.total_count} projects`)
    return data
  }

  /**
   * Create a new project (simple version)
   *
   * @param projectData - Project creation data
   * @returns ProjectCreateResponse with new project ID
   */
  async createProject(
    projectData: ProjectCreateRequest
  ): Promise<ProjectCreateResponse> {
    console.log("[ProjectsAPI] Creating new project...")

    const url = `${this.baseUrl}${this.apiPrefix}/projects`

    const response = await fetch(url, {
      method: "POST",
      headers: await this.getAuthHeaders(),
      body: JSON.stringify(projectData),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to create project")
    }

    const data: ProjectCreateResponse = await response.json()

    // Clear cache so next fetch gets fresh data
    this.clearCache()

    console.log(`[ProjectsAPI] Project created: ${data.project_id}`)
    return data
  }

  /**
   * Complete project setup with brand and prompts
   *
   * This creates:
   * 1. A new project
   * 2. A brand (if not exists)
   * 3. Brand prompts for each segment
   *
   * @param setupData - Complete project setup data
   * @returns ProjectSetupResponse with project ID, brand ID, and prompt count
   */
  async setupProject(
    setupData: ProjectSetupRequest
  ): Promise<ProjectSetupResponse> {
    console.log("[ProjectsAPI] Setting up project with brand and prompts...")

    const url = `${this.baseUrl}${this.apiPrefix}/projects/setup`

    const response = await fetch(url, {
      method: "POST",
      headers: await this.getAuthHeaders(),
      body: JSON.stringify(setupData),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (response.status === 409) {
      const error: ApiError = await response.json()
      const conflictError = new Error(error.detail || "Brand already exists in another project")
      ;(conflictError as ApiConflictError).isConflict = true
      throw conflictError
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to setup project")
    }

    const data: ProjectSetupResponse = await response.json()

    // Clear cache so next fetch gets fresh data
    this.clearCache()

    console.log(
      `[ProjectsAPI] Project setup completed: project=${data.project_id}, brand=${data.brand_id}, prompts=${data.prompt_count}`
    )
    return data
  }

  /**
   * Update an existing project
   *
   * @param projectId - The project ID to update
   * @param updateData - Fields to update
   * @returns ProjectUpdateResponse with success message
   */
  async updateProject(
    projectId: string,
    updateData: ProjectUpdateRequest
  ): Promise<ProjectUpdateResponse> {
    console.log(`[ProjectsAPI] Updating project ${projectId}...`)

    const url = `${this.baseUrl}${this.apiPrefix}/projects/${projectId}`

    const response = await fetch(url, {
      method: "PATCH",
      headers: await this.getAuthHeaders(),
      body: JSON.stringify(updateData),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (response.status === 404) {
      throw new Error("Project not found or you don't have permission to update it")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to update project")
    }

    const data: ProjectUpdateResponse = await response.json()

    // Clear cache so next fetch gets fresh data
    this.clearCache()

    console.log(`[ProjectsAPI] Project updated: ${data.project_id}`)
    return data
  }

  /**
   * Get project details including brand and prompts
   *
   * @param projectId - The project ID to fetch
   * @returns ProjectDetailResponse with full project details
   */
  async getProjectDetail(projectId: string): Promise<ProjectDetailResponse> {
    console.log(`[ProjectsAPI] Fetching project detail ${projectId}...`)

    const url = `${this.baseUrl}${this.apiPrefix}/projects/${projectId}`

    const response = await fetch(url, {
      method: "GET",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (response.status === 404) {
      throw new Error("Project not found or you don't have permission to view it")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to fetch project details")
    }

    const data: ProjectDetailResponse = await response.json()

    console.log(
      `[ProjectsAPI] Project detail fetched: ${data.project_id}, brand=${data.brand_name}, segments=${data.segments.length}`
    )
    return data
  }

  /**
   * Full update of project including brand and prompts
   *
   * @param projectId - The project ID to update
   * @param updateData - Full project update data
   * @returns ProjectSetupResponse with project ID, brand ID, and prompt count
   */
  async updateProjectFull(
    projectId: string,
    updateData: ProjectFullUpdateRequest
  ): Promise<ProjectSetupResponse> {
    console.log(`[ProjectsAPI] Full update project ${projectId}...`)

    const url = `${this.baseUrl}${this.apiPrefix}/projects/${projectId}`

    const response = await fetch(url, {
      method: "PUT",
      headers: await this.getAuthHeaders(),
      body: JSON.stringify(updateData),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (response.status === 404) {
      throw new Error("Project not found or you don't have permission to update it")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to update project")
    }

    const data: ProjectSetupResponse = await response.json()

    // Clear cache so next fetch gets fresh data
    this.clearCache()

    console.log(
      `[ProjectsAPI] Project full update completed: project=${data.project_id}, brand=${data.brand_id}, prompts=${data.prompt_count}`
    )
    return data
  }

  /**
   * Delete a project and its associated brand prompts
   *
   * @param projectId - The project ID to delete
   * @returns ProjectUpdateResponse with success message
   */
  async deleteProject(projectId: string): Promise<ProjectUpdateResponse> {
    console.log(`[ProjectsAPI] Deleting project ${projectId}...`)

    const url = `${this.baseUrl}${this.apiPrefix}/projects/${projectId}`

    const response = await fetch(url, {
      method: "DELETE",
      headers: await this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
    }

    if (response.status === 404) {
      throw new Error("Project not found or you don't have permission to delete it")
    }

    if (!response.ok) {
      const error: ApiError = await response.json()
      throw new Error(error.detail || "Failed to delete project")
    }

    const data: ProjectUpdateResponse = await response.json()

    // Clear cache so next fetch gets fresh data
    this.clearCache()

    console.log(`[ProjectsAPI] Project deleted: ${data.project_id}`)
    return data
  }
}

// Export singleton instance
export const projectsAPI = new ProjectsAPI()
