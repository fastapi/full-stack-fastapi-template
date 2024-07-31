import { test } from "@playwright/test"
import { firstSuperuser, firstSuperuserPassword } from "./config"
import { randomEmail } from "./utils/random"
import { createSuperUser, logInUser } from "./utils/user"

// User Management

test.describe("Admin user can manage members", () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test("Admin user can create new normal user", async ({ page }) => {
    const userFullName = "Test User"
    const userEmail = randomEmail()
    const userPassword = "password"
    const userIsActive = true

    await logInUser(page, firstSuperuser, firstSuperuserPassword)

    await createSuperUser(
      page,
      userEmail,
      userFullName,
      userPassword,
      userIsActive,
    )
  })

  test("Admin user can create new superuser", async ({ page }) => {
    const userFullName = "Test User"
    const userEmail = randomEmail()
    const userPassword = "password"
    const userIsActive = true

    await logInUser(page, firstSuperuser, firstSuperuserPassword)

    await createSuperUser(
      page,
      userEmail,
      userFullName,
      userPassword,
      userIsActive,
    )
  })
})
