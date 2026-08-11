import type { APIRequestContext } from "@playwright/test"

type Address = {
  Name: string
  Address: string
}

type Email = {
  ID: string
  To: Address[]
  Subject: string
}

async function findEmail({
  request,
  query,
}: {
  request: APIRequestContext
  query: string
}) {
  const response = await request.get(
    `${process.env.MAILPIT_HOST}/api/v1/search`,
    {
      params: { query, limit: 1 },
    },
  )

  const { messages }: { messages: Email[] } = await response.json()

  return messages[0] ?? null
}

export async function findLastEmail({
  request,
  query,
  timeout = 5000,
}: {
  request: APIRequestContext
  query: string
  timeout?: number
}) {
  const deadline = Date.now() + timeout

  while (Date.now() < deadline) {
    const email = await findEmail({ request, query })

    if (email) {
      return email
    }

    await new Promise((resolve) => setTimeout(resolve, 100))
  }

  throw new Error(`Timeout while trying to get the latest email for "${query}"`)
}

export function emailUrl(email: Email) {
  return `${process.env.MAILPIT_HOST}/view/${email.ID}.html`
}
