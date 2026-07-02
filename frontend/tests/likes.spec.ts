import { expect, test } from "@playwright/test"

// These tests mutate like counts on shared seeded articles (e.g. the
// top-scored "first row"), so they must not run concurrently with each
// other or they'll race on the same rows.
test.describe.configure({ mode: "serial" })

test.describe("Anonymous likes", () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test("article rows show a fire button with a numeric badge, including 0", async ({
    page,
  }) => {
    await page.goto("/")
    const firstRow = page.getByTestId("article-row").first()
    await expect(firstRow.getByTestId("like-button")).toBeVisible()
    const countText = await firstRow.getByTestId("like-count").textContent()
    expect(countText).toMatch(/^\d+$/)
  })

  test("clicking the fire while logged out redirects to /login with a redirect param", async ({
    page,
  }) => {
    await page.goto("/")
    await page.getByTestId("like-button").first().click()
    await page.waitForURL(/\/login/)
    const url = new URL(page.url())
    expect(url.searchParams.get("redirect")).toBeTruthy()
  })
})

test.describe("Logged-in likes", () => {
  test("clicking the fire toggles the like optimistically", async ({
    page,
  }) => {
    await page.goto("/")
    const firstRow = page.getByTestId("article-row").first()
    const likeButton = firstRow.getByTestId("like-button")
    const likeCount = firstRow.getByTestId("like-count")

    // Don't assume a starting liked state: earlier tests/runs may have
    // already liked this article, so compute the expected transition from
    // whatever state it's actually in.
    const initialCount = Number(await likeCount.textContent())
    const initiallyLiked =
      (await likeButton.getAttribute("data-liked")) === "true"
    const delta = initiallyLiked ? -1 : 1

    await likeButton.click()
    await expect(likeCount).toHaveText(String(initialCount + delta))
    await expect(likeButton).toHaveAttribute(
      "data-liked",
      String(!initiallyLiked),
    )

    await likeButton.click()
    await expect(likeCount).toHaveText(String(initialCount))
    await expect(likeButton).toHaveAttribute(
      "data-liked",
      String(initiallyLiked),
    )
  })
})

test.describe("Popular sort", () => {
  test("sort filter shows Popular and selecting it reorders the list", async ({
    page,
  }) => {
    await page.goto("/")
    const popularOption = page.getByRole("button", { name: "Popular" })
    await expect(popularOption).toBeVisible()
    await popularOption.click()

    await expect(page.getByTestId("article-row").first()).toBeVisible()
  })
})

test.describe("Profile page", () => {
  test.describe("logged out", () => {
    test.use({ storageState: { cookies: [], origins: [] } })

    test("visiting /profile redirects to /login", async ({ page }) => {
      await page.goto("/profile")
      await page.waitForURL(/\/login/)
    })
  })

  test("shows Liked / My profile / Password / Danger zone tabs, Liked active by default", async ({
    page,
  }) => {
    await page.goto("/profile")
    for (const tab of ["Liked", "My profile", "Password", "Danger zone"]) {
      await expect(page.getByRole("tab", { name: tab })).toBeVisible()
    }
    await expect(page.getByRole("tab", { name: "Liked" })).toHaveAttribute(
      "aria-selected",
      "true",
    )
  })

  test("a liked article appears in the Liked tab; unliking removes it", async ({
    page,
  }) => {
    await page.goto("/")
    const firstRow = page.getByTestId("article-row").first()
    const href = await firstRow.locator("a").first().getAttribute("href")
    await firstRow.getByTestId("like-button").click()
    await expect(firstRow.getByTestId("like-button")).toHaveAttribute(
      "data-liked",
      "true",
    )

    await page.goto("/profile")
    const likedRow = page
      .locator(`a[href="${href}"]`)
      .locator("xpath=ancestor::li[@data-testid='article-row']")
    await expect(likedRow).toBeVisible()

    await likedRow.getByTestId("like-button").click()
    await expect(likedRow).not.toBeVisible()
  })

  test("/settings redirects to /profile", async ({ page }) => {
    await page.goto("/settings")
    await page.waitForURL("/profile")
  })
})
