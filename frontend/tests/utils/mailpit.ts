import type { APIRequestContext } from "@playwright/test"

type EmailSummary = {
  ID: string
}

export async function waitForEmailHtml({
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
    const response = await request.get(
      `${process.env.MAILPIT_HOST}/api/v1/search`,
      {
        params: { query, limit: 1 },
      },
    )
    const { messages }: { messages: EmailSummary[] } = await response.json()
    const email = messages[0]

    if (email) {
      const htmlResponse = await request.get(
        `${process.env.MAILPIT_HOST}/view/${email.ID}.html`,
      )

      if (!htmlResponse.ok()) {
        throw new Error(
          `Could not get the HTML for email "${email.ID}": ${htmlResponse.status()}`,
        )
      }

      return htmlResponse.text()
    }

    await new Promise((resolve) => setTimeout(resolve, 100))
  }

  throw new Error(`Timeout while trying to get the latest email for "${query}"`)
}
