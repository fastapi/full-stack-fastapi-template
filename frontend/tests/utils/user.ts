import { type Page, expect } from "@playwright/test"

export async function signUpNewUser(
  page: Page,
  name: string,
  email: string,
  password: string,
) {
  await page.goto("/signup")

  await page.getByPlaceholder("Full Name").fill(name)
  await page.getByPlaceholder("Email").fill(email)
  await page.getByPlaceholder("Password", { exact: true }).fill(password)
  await page.getByPlaceholder("Repeat Password").fill(password)
  await page.getByRole("button", { name: "Sign Up" }).click()
  await expect(
    page.getByText("Your account has been created successfully"),
  ).toBeVisible()
  await page.goto("/login")
}

export async function logInUser(page: Page, email: string, password: string) {
  await page.goto("/login")

  await page.getByPlaceholder("Email").fill(email)
  await page.getByPlaceholder("Password", { exact: true }).fill(password)
  await page.getByRole("button", { name: "Log In" }).click()
  await page.waitForURL("/")
  await expect(
    page.getByText("Welcome back, nice to see you again!"),
  ).toBeVisible()
}

export async function logOutUser(page: Page) {
  await page.getByTestId("user-menu").click()
  await page.getByRole("menuitem", { name: "Log out" }).click()
  await page.goto("/login")
}

export async function createNormalUser(
  page: Page,
  userEmail: string,
  userFullName: string,
  userPassword: string,
  userIsActive: boolean,
) {
  await page.goto("/admin")
  await page.getByRole("button", { name: "Add User" }).click()
  await page.getByPlaceholder("Email").fill(userEmail)
  await page.getByPlaceholder("Full name").fill(userFullName)
  await page.getByLabel("Set Password*").fill(userPassword)
  await page.getByLabel("Confirm Password*").fill(userPassword)
  if (userIsActive) {
    await page
      .locator("label")
      .filter({ hasText: "Is active?" })
      .locator("span")
      .first()
      .click()
  }
  await page.getByRole("button", { name: "Save" }).click()
  await expect(page.getByText("User created successfully.")).toBeVisible()
}

export async function createSuperUser(
  page: Page,
  userEmail: string,
  userFullName: string,
  userPassword: string,
  userIsActive: boolean,
) {
  await page.goto("/admin")
  await page.getByRole("button", { name: "Add User" }).click()
  await page.getByPlaceholder("Email").fill(userEmail)
  await page.getByPlaceholder("Full name").fill(userFullName)
  await page.getByLabel("Set Password*").fill(userPassword)
  await page.getByLabel("Confirm Password*").fill(userPassword)
  if (userIsActive) {
    await page
      .locator("label")
      .filter({ hasText: "Is active?" })
      .locator("span")
      .first()
      .click()
  }
  await page
    .locator("label")
    .filter({ hasText: "Is superuser?" })
    .locator("span")
    .first()
    .click()
  await page.getByRole("button", { name: "Save" }).click()
  await expect(page.getByText("User created successfully.")).toBeVisible()
}
