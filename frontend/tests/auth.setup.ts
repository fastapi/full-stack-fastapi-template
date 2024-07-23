import { test as setup } from "@playwright/test"

const authFile = "playwright/.auth/user.json"

const { FIRST_SUPERUSER, FIRST_SUPERUSER_PASSWORD } = process.env

setup("authenticate", async ({ page }) => {
  await page.goto("/login")
  await page.getByPlaceholder("Email").fill(FIRST_SUPERUSER)
  await page.getByPlaceholder("Password").fill(FIRST_SUPERUSER_PASSWORD)
  await page.getByRole("button", { name: "Log In" }).click()
  await page.waitForURL("/")
  await page.context().storageState({ path: authFile })
})
