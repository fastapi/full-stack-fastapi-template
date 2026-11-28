import { type APIRequestContext, expect, test } from "@playwright/test"
import { firstSuperuser, firstSuperuserPassword } from "./config.ts"
import { createUser } from "./utils/privateApi"
import { randomEmail, randomPassword } from "./utils/random"
import { logInUser } from "./utils/user"

const apiUrl = `${process.env.VITE_API_URL}/api/v1`

test.use({ storageState: { cookies: [], origins: [] } })

async function adminPatchUser(
  request: APIRequestContext,
  email: string,
  body: Record<string, unknown>,
) {
  const login = await request.post(`${apiUrl}/login/access-token`, {
    form: { username: firstSuperuser, password: firstSuperuserPassword },
  })
  const headers = {
    Authorization: `Bearer ${(await login.json()).access_token}`,
  }
  const users = await (
    await request.get(`${apiUrl}/users/`, { headers })
  ).json()
  const user = users.data.find((u: { email: string }) => u.email === email)
  const r = await request.patch(`${apiUrl}/users/${user.id}`, {
    headers,
    data: body,
  })
  expect(r.ok()).toBeTruthy()
}

test("Demoted manager keeps their session on authorization errors", async ({
  page,
  request,
}) => {
  const email = randomEmail()
  const password = randomPassword()
  await createUser({ email, password })
  await adminPatchUser(request, email, { role: "manager" })

  await logInUser(page, email, password)
  await page.goto("/admin")
  await expect(page.getByRole("row").filter({ hasText: email })).toBeVisible()

  await adminPatchUser(request, email, { role: "member" })
  let forbiddenCount = 0
  page.on("response", (r) => {
    if (r.url().includes("/api/v1/users/?") && r.status() === 403) {
      forbiddenCount++
    }
  })
  // Suspense queries stay fresh for at least 1s, so wait before refocusing.
  await page.waitForTimeout(1000)
  await page.evaluate(() => window.dispatchEvent(new Event("visibilitychange")))
  // The query errors only after the initial request and 3 default retries.
  await expect.poll(() => forbiddenCount, { timeout: 20000 }).toBe(4)
  await page.waitForTimeout(500)

  await expect(page.getByRole("link", { name: "Admin" })).toHaveCount(0)
  await page.getByRole("link", { name: "Items" }).click()
  await expect(page).toHaveURL(/\/items/)
  expect(
    await page.evaluate(() => localStorage.getItem("access_token")),
  ).not.toBeNull()
})

test("Deactivated user is logged out", async ({ page, request }) => {
  const email = randomEmail()
  const password = randomPassword()
  await createUser({ email, password })

  await logInUser(page, email, password)
  await adminPatchUser(request, email, { is_active: false })
  await page.goto("/settings")

  await page.waitForURL("/login")
  expect(
    await page.evaluate(() => localStorage.getItem("access_token")),
  ).toBeNull()
})
