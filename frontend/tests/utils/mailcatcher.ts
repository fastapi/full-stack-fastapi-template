import type { APIRequestContext } from "@playwright/test"

// Mailhog email format is different from Mailcatcher
type MailhogEmail = {
  ID: string
  From: {
    Mailbox: string
    Domain: string
    Relays: null
  }
  To: Array<{
    Mailbox: string
    Domain: string
    Relays: null
  }>
  Content: {
    Headers: {
      Subject: string
      To: string
      From: string
      "Content-Type": string
    }
    Body: string
    Size: number
    MIME: null
  }
  Created: string
  MIME: null
  Raw: {
    From: string
    To: string[]
    Data: string
    Helo: string
  }
}

// Keep the same interface for backward compatibility
type Email = {
  id: string
  recipients: string[]
  subject: string
}

async function findEmail({
  request,
  filter,
}: { request: APIRequestContext; filter?: (email: Email) => boolean }) {
  // Mailhog API endpoint is different
  const response = await request.get(`${process.env.MAILCATCHER_HOST}/api/v2/messages`)

  const result = await response.json()

  // Convert Mailhog format to our Email format
  let emails: Email[] = result.items.map((item: MailhogEmail) => {
    return {
      id: item.ID,
      recipients: item.Raw.To,
      subject: item.Content.Headers.Subject
    }
  })

  if (filter) {
    emails = emails.filter(filter)
  }

  const email = emails[emails.length - 1]

  if (email) {
    return email as Email
  }

  return null
}

export function findLastEmail({
  request,
  filter,
  timeout = 5000,
}: {
  request: APIRequestContext
  filter?: (email: Email) => boolean
  timeout?: number
}) {
  const timeoutPromise = new Promise<never>((_, reject) =>
    setTimeout(
      () => reject(new Error("Timeout while trying to get latest email")),
      timeout,
    ),
  )

  const checkEmails = async () => {
    while (true) {
      const emailData = await findEmail({ request, filter })

      if (emailData) {
        return emailData
      }
      // Wait for 100ms before checking again
      await new Promise((resolve) => setTimeout(resolve, 100))
    }
  }

  return Promise.race([timeoutPromise, checkEmails()])
}
