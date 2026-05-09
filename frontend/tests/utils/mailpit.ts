import type { APIRequestContext } from "@playwright/test"

export type MailpitRecipient = {
  Address: string
  Name: string
}

export type MailpitEmail = {
  ID: string
  To: MailpitRecipient[]
  Subject: string
}

type MailpitMessagesResponse = {
  total: number
  unread: number
  count: number
  messages: MailpitEmail[]
}

async function findEmail({
  request,
  filter,
}: {
  request: APIRequestContext
  filter?: (email: MailpitEmail) => boolean
}) {
  const response = await request.get(
    `${process.env.MAILPIT_HOST}/api/v1/messages`,
  )

  const data: MailpitMessagesResponse = await response.json()
  let emails = data.messages || []

  if (filter) {
    emails = emails.filter(filter)
  }

  const email = emails[0] // Mailpit returns newest first

  if (email) {
    return email
  }

  return null
}

export function findLastEmail({
  request,
  filter,
  timeout = 5000,
}: {
  request: APIRequestContext
  filter?: (email: MailpitEmail) => boolean
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
