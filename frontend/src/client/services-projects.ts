// Temporary API services for Projects and Galleries
import type { DashboardStats, GalleriesPublic, Project, ProjectsPublic } from "./types-projects"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

async function getAuthToken(): Promise<string> {
  return localStorage.getItem("access_token") || ""
}

export class ProjectsServiceTemp {
  static async readProjects(params: { skip?: number; limit?: number } = {}): Promise<ProjectsPublic> {
    const token = await getAuthToken()
    const { skip = 0, limit = 100 } = params
    
    const response = await fetch(
      `${API_URL}/api/v1/projects?skip=${skip}&limit=${limit}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    )
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  }
  
  static async readProject(id: string): Promise<Project> {
    const token = await getAuthToken()
    
    const response = await fetch(`${API_URL}/api/v1/projects/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  }
  
  static async getDashboardStats(): Promise<DashboardStats> {
    const token = await getAuthToken()
    
    const response = await fetch(`${API_URL}/api/v1/projects/stats`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  }
}

export class GalleriesServiceTemp {
  static async readGalleries(params: { skip?: number; limit?: number; project_id?: string } = {}): Promise<GalleriesPublic> {
    const token = await getAuthToken()
    const { skip = 0, limit = 100, project_id } = params
    
    let url = `${API_URL}/api/v1/galleries?skip=${skip}&limit=${limit}`
    if (project_id) {
      url += `&project_id=${project_id}`
    }
    
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  }
}

