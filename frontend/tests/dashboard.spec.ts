import { expect, test } from "@playwright/test";
import { randomEmail, randomPassword } from "./utils/random";
import { signUpNewUser, logInUser, logOutUser } from "./utils/user";

test.describe("Dashboard page", () => {
  test("is visible after login", async ({ page }) => {
    const email = randomEmail();
    const password = randomPassword();

    // Sign up a new user
    await signUpNewUser(page, "Playwright Dashboard Test", email, password);

    // Log in with the new user
    await logInUser(page, email, password);

    // Navigate to dashboard (root path)
    await page.goto("/");
    // Debug: take screenshot if fails
    try {
      await expect(
        page.getByText("Welcome back, nice to see you again!")
      ).toBeVisible({ timeout: 10000 });
    } catch (e) {
      await page.screenshot({
        path: "dashboard-visible-after-login-fail.png",
        fullPage: true,
      });
      throw e;
    }
    // Check for greeting (user's name or email)
    await expect(page.getByText(/^Hi, /)).toBeVisible({ timeout: 10000 });
    // Check for at least one button (UI loaded)
    const buttons = await page.getByRole("button").all();
    expect(buttons.length).toBeGreaterThan(0);
  });

  test("redirects to login when not authenticated", async ({ page }) => {
    await page.goto("/");
    // Wait for redirect to /login
    await page.waitForURL("/login", { timeout: 10000 });
    // Debug: take screenshot if fails
    try {
      await expect(page.getByPlaceholder("Email")).toBeVisible({
        timeout: 10000,
      });
      await expect(
        page.getByPlaceholder("Password", { exact: true })
      ).toBeVisible({ timeout: 10000 });
    } catch (e) {
      await page.screenshot({
        path: "dashboard-redirect-login-fail.png",
        fullPage: true,
      });
      throw e;
    }
  });

  test("user can log out from dashboard", async ({ page }) => {
    const email = randomEmail();
    const password = randomPassword();

    // Sign up and log in
    await signUpNewUser(page, "Playwright Logout Test", email, password);
    await logInUser(page, email, password);

    // Log out
    await logOutUser(page);
    // Debug: take screenshot if fails
    try {
      await expect(page.getByPlaceholder("Email")).toBeVisible({
        timeout: 10000,
      });
      await expect(
        page.getByPlaceholder("Password", { exact: true })
      ).toBeVisible({ timeout: 10000 });
    } catch (e) {
      await page.screenshot({
        path: "dashboard-logout-login-fail.png",
        fullPage: true,
      });
      throw e;
    }
  });
});
