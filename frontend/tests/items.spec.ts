import { expect, test } from "@playwright/test"

test("Items route redirects to dashboard (page hidden for delivery)", async ({
  page,
}) => {
  await page.goto("/items")
  await expect(page).toHaveURL("/")
  await expect(
    page.getByText("Welcome back, nice to see you again!"),
  ).toBeVisible()
})
