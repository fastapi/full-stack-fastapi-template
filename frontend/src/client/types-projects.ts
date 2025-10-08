// Temporary types for Projects and Galleries until we regenerate the full client

export interface Project {
  id: string
  name: string
  client_name: string
  client_email?: string
  description?: string
  status: string
  deadline?: string
  start_date?: string
  budget?: string
  progress: number
  created_at: string
  updated_at: string
  organization_id: string
}

export interface ProjectsPublic {
  data: Project[]
  count: number
}

export interface Gallery {
  id: string
  name: string
  date?: string
  photo_count: number
  photographer?: string
  status: string
  cover_image_url?: string
  created_at: string
  project_id: string
}

export interface GalleriesPublic {
  data: Gallery[]
  count: number
}

export interface DashboardStats {
  active_projects: number
  upcoming_deadlines: number
  team_members: number
  completed_this_month: number
}

