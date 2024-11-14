// This test suite verifies the password recovery process, covering scenarios such as UI visibility, successful password reset, 
// handling of expired or invalid reset links, and password strength validation. Each test simulates user interactions to 
// confirm expected behaviors, including email retrieval, form validation, and error handling.

import { expect, test } from "@playwright/test"
import { findLastEmail } from "./utils/mailcatcher"
import { randomEmail, randomPassword } from "./utils/random"
import { logInUser, signUpNewUser } from "./utils/user"

// Use a clean session state for each test to ensure isolation
test.use({ storageState: { cookies: [], origins: [] } })

// Test to check if the "Password Recovery" title is visible
test("Password Recovery title is visible", async ({ page }) => {
  await page.goto("/recover-password")
  await expect(page.getByRole("heading", { name: "Password Recovery" })).toBeVisible()
})

// Test to verify if the email input is visible, empty, and editable
test("Input is visible, empty and editable", async ({ page }) => {
  await page.goto("/recover-password")
  await expect(page.getByPlaceholder("Email")).toBeVisible()
  await expect(page.getByPlaceholder("Email")).toHaveText("")
  await expect(page.getByPlaceholder("Email")).toBeEditable()
})

// Test to ensure the "Continue" button is visible
test("Continue button is visible", async ({ page }) => {
  await page.goto("/recover-password")
  await expect(page.getByRole("button", { name: "Continue" })).toBeVisible()
})

// Test for a successful password reset using a reset link sent to the user's email
test("User can reset password successfully using the link", async ({ page, request }) => {
  const fullName = "Test User"
  const email = randomEmail()
  const password = randomPassword()
  const newPassword = randomPassword()

  // Step 1: Register a new user
  await signUpNewUser(page, fullName, email, password)

  // Step 2: Request password recovery
  await page.goto("/recover-password")
  await page.getByPlaceholder("Email").fill(email)
  await page.getByRole("button", { name: "Continue" }).click()

  // Step 3: Retrieve the last email sent to the user
  const emailData = await findLastEmail({
    request,
    filter: (e) => e.recipients.includes(`<${email}>`),
    timeout: 5000,
  })

  // Step 4: Access the password reset link in the email
  await page.goto(`http://localhost:1080/messages/${emailData.id}.html`)
  const selector = 'a[href*="/reset-password?token="]'
  let url = await page.getAttribute(selector, "href")
  url = url!.replace("http://localhost/", "http://localhost:5173/")

  // Step 5: Set and confirm the new password
  await page.goto(url)
  await page.getByLabel("Set Password").fill(newPassword)
  await page.getByLabel("Confirm Password").fill(newPassword)
  await page.getByRole("button", { name: "Reset Password" }).click()

  // Verify the success message
  await expect(page.getByText("Password updated successfully")).toBeVisible()

  // Step 6: Log in with the new password to confirm success
  await logInUser(page, email, newPassword)
})

// Test to handle expired or invalid reset link
test("Expired or invalid reset link", async ({ page }) => {
  const password = randomPassword()
  const invalidUrl = "/reset-password?token=invalidtoken"

  // Attempt to use an invalid token for password reset
  await page.goto(invalidUrl)
  await page.getByLabel("Set Password").fill(password)
  await page.getByLabel("Confirm Password").fill(password)
  await page.getByRole("button", { name: "Reset Password" }).click()

  // Confirm that the appropriate error message is displayed
  await expect(page.getByText("Invalid token")).toBeVisible()
})

// Test to validate weak password prevention during password reset
test("Weak new password validation", async ({ page, request }) => {
  const fullName = "Test User"
  const email = randomEmail()
  const password = randomPassword()
  const weakPassword = "123" // Example weak password

  // Step 1: Register a new user
  await signUpNewUser(page, fullName, email, password)

  // Step 2: Request password recovery
  await page.goto("/recover-password")
  await page.getByPlaceholder("Email").fill(email)
  await page.getByRole("button", { name: "Continue" }).click()

  // Step 3: Retrieve the password recovery email
  const emailData = await findLastEmail({
    request,
    filter: (e) => e.recipients.includes(`<${email}>`),
    timeout: 5000,
  })

  // Step 4: Access the reset link from the email
  await page.goto(`http://localhost:1080/messages/${emailData.id}.html`)
  const selector = 'a[href*="/reset-password?token="]'
  let url = await page.getAttribute(selector, "href")
  url = url!.replace("http://localhost/", "http://localhost:5173/")

  // Step 5: Attempt to set a weak password
  await page.goto(url)
  await page.getByLabel("Set Password").fill(weakPassword)
  await page.getByLabel("Confirm Password").fill(weakPassword)
  await page.getByRole("button", { name: "Reset Password" }).click()

  // Confirm that the weak password error message is shown
  await expect(page.getByText("Password must be at least 8 characters")).toBeVisible()
})
