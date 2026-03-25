import { getAuthToken } from "./auth-helper"

const API_BASE_URL = import.meta.env.VITE_API_URL ?? ""
const API_PREFIX = "/api/v1"

export interface BlogPostListItem {
  id: number
  slug: string
  title: string
  excerpt: string
  category: string
  read_time_minutes: number
  author_name: string
  published_at: string
}

export interface BlogPostPublicResponse {
  id: number
  slug: string
  title: string
  excerpt: string
  content: string
  category: string
  read_time_minutes: number
  author_name: string
  published_at: string
}

export interface BlogPostAdminResponse {
  id: number
  slug: string
  title: string
  excerpt: string
  content: string
  category: string
  read_time_minutes: number
  author_name: string
  is_published: boolean
  published_at: string | null
  created_at: string
  updated_at: string | null
}

export interface BlogPostCreateRequest {
  slug: string
  title: string
  excerpt: string
  content: string
  category: string
  read_time_minutes: number
  author_name?: string
}

export interface BlogPostUpdateRequest {
  slug?: string
  title?: string
  excerpt?: string
  content?: string
  category?: string
  read_time_minutes?: number
  author_name?: string
}

class BlogAPI {
  private readonly base = `${API_BASE_URL}${API_PREFIX}/blog`

  private async authHeaders(): Promise<HeadersInit> {
    const token = await getAuthToken()
    return {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    }
  }

  // ── Public ──────────────────────────────────────────────────────────────

  async getPosts(): Promise<BlogPostListItem[]> {
    const res = await fetch(`${this.base}/posts`)
    if (!res.ok) throw new Error("Failed to fetch posts")
    return res.json()
  }

  async getPost(slug: string): Promise<BlogPostPublicResponse> {
    const res = await fetch(`${this.base}/posts/${slug}`)
    if (res.status === 404) throw new Error("Post not found")
    if (!res.ok) throw new Error("Failed to fetch post")
    return res.json()
  }

  // ── Admin ────────────────────────────────────────────────────────────────

  async adminGetPost(id: number): Promise<BlogPostAdminResponse> {
    const res = await fetch(`${this.base}/admin/posts/${id}`, {
      headers: await this.authHeaders(),
    })
    if (res.status === 404) throw new Error("Post not found")
    if (!res.ok) throw new Error("Failed to fetch post")
    return res.json()
  }

  async adminListPosts(): Promise<BlogPostAdminResponse[]> {
    const res = await fetch(`${this.base}/admin/posts`, {
      headers: await this.authHeaders(),
    })
    if (!res.ok) throw new Error("Failed to fetch posts")
    return res.json()
  }

  async adminCreatePost(data: BlogPostCreateRequest): Promise<BlogPostAdminResponse> {
    const res = await fetch(`${this.base}/admin/posts`, {
      method: "POST",
      headers: await this.authHeaders(),
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error("Failed to create post")
    return res.json()
  }

  async adminUpdatePost(id: number, data: BlogPostUpdateRequest): Promise<BlogPostAdminResponse> {
    const res = await fetch(`${this.base}/admin/posts/${id}`, {
      method: "PUT",
      headers: await this.authHeaders(),
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error("Failed to update post")
    return res.json()
  }

  async adminDeletePost(id: number): Promise<void> {
    const res = await fetch(`${this.base}/admin/posts/${id}`, {
      method: "DELETE",
      headers: await this.authHeaders(),
    })
    if (!res.ok) throw new Error("Failed to delete post")
  }

  async adminTogglePublish(id: number): Promise<BlogPostAdminResponse> {
    const res = await fetch(`${this.base}/admin/posts/${id}/publish`, {
      method: "POST",
      headers: await this.authHeaders(),
    })
    if (!res.ok) throw new Error("Failed to toggle publish")
    return res.json()
  }
}

export const blogAPI = new BlogAPI()
