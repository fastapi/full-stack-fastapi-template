// Utility functions for fetching and filtering emails during Playwright tests.
// Provides functions to locate the latest email that matches specific criteria, with timeout support
// to handle cases where emails may be delayed.

import type { APIRequestContext } from "@playwright/test"

// Type definition for an email, specifying fields used in filtering and email retrieval
type Email = {
  id: number
  recipients: string[]
  subject: string
}

// findEmail: Fetches emails from the mailcatcher API and applies an optional filter.
// Returns the most recent email or null if no emails match.
async function findEmail({
  request,
  filter,
}: { request: APIRequestContext; filter?: (email: Email) => boolean }) {
  const response = await request.get("http://localhost:1080/messages")

  // Parse the response as JSON and filter emails if a filter is provided
  let emails = await response.json()

  if (filter) {
    emails = emails.filter(filter)
  }

  // Select the most recent email from the filtered list, if any
  const email = emails[emails.length - 1]

  if (email) {
    return email as Email
  }

  return null
}

// findLastEmail: Checks for the latest email that matches a specified filter, within a timeout period
// Useful for scenarios where we need to wait for an email to arrive.
export function findLastEmail({
  request,
  filter,
  timeout = 5000,
}: {
  request: APIRequestContext
  filter?: (email: Email) => boolean
  timeout?: number
}) {
  // Timeout promise: rejects if no email is found within the specified time
  const timeoutPromise = new Promise<never>((_, reject) =>
    setTimeout(
      () => reject(new Error("Timeout while trying to get latest email")),
      timeout,
    ),
  )

  // Function to repeatedly check for matching emails, every 100ms, until one is found or timeout occurs
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

  // Run checkEmails with a timeout constraint
  return Promise.race([timeoutPromise, checkEmails()])
}
