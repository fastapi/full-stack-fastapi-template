import { getAuthToken } from "./auth-helper"

const API_BASE_URL = import.meta.env.VITE_API_URL ?? ""
const API_PREFIX = "/api/v1"

class BillingAPI {
  private readonly baseUrl: string
  private readonly apiPrefix: string

  constructor(baseUrl: string = API_BASE_URL, apiPrefix: string = API_PREFIX) {
    this.baseUrl = baseUrl
    this.apiPrefix = apiPrefix
  }

  private async getAuthHeaders(): Promise<HeadersInit> {
    const token = await getAuthToken()
    return {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    }
  }

  async createCheckoutSession(
    priceId: string,
  ): Promise<{ checkout_url: string }> {
    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/billing/create-checkout-session`,
      {
        method: "POST",
        headers: await this.getAuthHeaders(),
        body: JSON.stringify({ price_id: priceId }),
      },
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to create checkout session")
    }

    return response.json()
  }

  async createPortalSession(): Promise<{ portal_url: string }> {
    const response = await fetch(
      `${this.baseUrl}${this.apiPrefix}/billing/create-portal-session`,
      {
        method: "POST",
        headers: await this.getAuthHeaders(),
      },
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to create portal session")
    }

    return response.json()
  }
}

export const billingAPI = new BillingAPI()
