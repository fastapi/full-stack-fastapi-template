/**
 * Projects API Client
 *
 * This module provides API client methods for managing projects.
 * Includes built-in caching functionality to minimize API calls.
 */

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
 * Request interface for creating a project
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
 * Standard API error response
 */
export interface ApiError {
  detail: string
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
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem("access_token")
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
  async getProjects(
    forceRefresh: boolean = false,
  ): Promise<ProjectListResponse> {
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
      headers: this.getAuthHeaders(),
    })

    if (response.status === 401) {
      throw new Error("Unauthorized - Please log in again")
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
   * Create a new project
   *
   * @param projectData - Project creation data
   * @returns ProjectCreateResponse with new project ID
   */
  async createProject(
    projectData: ProjectCreateRequest,
  ): Promise<ProjectCreateResponse> {
    console.log("[ProjectsAPI] Creating new project...")

    const url = `${this.baseUrl}${this.apiPrefix}/projects`

    const response = await fetch(url, {
      method: "POST",
      headers: this.getAuthHeaders(),
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
}

// Export singleton instance
export const projectsAPI = new ProjectsAPI()
