import { expect, test } from "@playwright/test"
import { UserRole, verifyUserRow } from "./utils/admin"

test.describe("Admin Page", () => {
  test.beforeEach(async ({ page }) => {
    await test.step("Open the admin page", async () => {
      await page.goto("/admin")
    })
  })

  test("Admin tab table should be visible", async ({ page }) => {
    await test.step("Check elements visibility", async () => {
      await expect(
        page.getByRole("heading", { name: "Users", level: 1 }),
      ).toBeVisible()
      await expect(
        page.getByText("Manage user accounts and permissions"),
      ).toBeVisible()
      await expect(page.getByRole("button", { name: "Add User" })).toBeVisible()
      await expect(page.locator('th[data-slot="table-head"]')).toHaveText([
        "Full Name",
        "Email",
        "Role",
        "Status",
        "Actions",
      ])
    })

    await test.step("Check the user table", async () => {
      await verifyUserRow(
        page,
        "N/A",
        "admin@example.com",
        UserRole.SUPERUSER,
        "Active",
        true,
      )
    })
  })

  test("User Dialog should have all fields visible", async ({ page }) => {
    const addUserBtn = page.getByRole("button", { name: "Add User" })

    await test.step("Open the Dialog", async () => {
      await expect(addUserBtn).toBeVisible()
      await addUserBtn.click()
    })

    const dialog = page.getByRole("dialog", { name: "Add User" })

    await test.step("Fill Inputs", async () => {
      await expect(dialog).toBeVisible()
      await expect(
        page.getByRole("heading", { name: "Add User", level: 2 }),
      ).toBeVisible()
      await expect(
        dialog.getByText("Fill in the form below to add a new user"),
      ).toBeVisible()

      const fields = ["Email", "Full Name", "Set Password", "Confirm Password"]
      for (const field of fields) {
        await expect(dialog.getByLabel(field)).toBeVisible()
        await expect(
          dialog
            .locator('label[data-slot="form-label"]')
            .filter({ hasText: field }),
        ).toBeVisible()
      }

      // Checkboxes
      await expect(
        dialog.getByRole("checkbox", { name: "Is superuser?" }),
      ).toBeVisible()
      await expect(
        dialog.getByRole("checkbox", { name: "Is active?" }),
      ).toBeVisible()
    })

    await test.step("Close the Dialog", async () => {
      // Footer Buttons
      const cancelBtn = dialog.getByRole("button", { name: "Cancel" })
      await expect(cancelBtn).toBeVisible()
      await expect(dialog.getByRole("button", { name: "Save" })).toBeVisible()

      // Close the dialog
      await cancelBtn.click()
      // Check if Add User button is visible after closing the dialog
      await expect(addUserBtn).toBeVisible()
    })
  })

  test("User Dialog should have all error fields visible", async ({ page }) => {
    const addUserBtn = page.getByRole("button", { name: "Add User" })

    await test.step("Open the Dialog", async () => {
      await expect(addUserBtn).toBeVisible()
      await addUserBtn.click()
    })

    const dialog = page.getByRole("dialog", { name: "Add User" })

    await test.step("Trigger error messages", async () => {
      await expect(dialog).toBeVisible()

      // Trigger error messages by clicking on input field
      await dialog.getByLabel("Email").click()
      await dialog.getByLabel("Set Password").click()
      await dialog.getByLabel("Confirm Password").click()

      // Click Save to trigger error message on 'Confirm Password' field
      const saveBtn = dialog.getByRole("button", { name: "Save" })
      await saveBtn.click()

      // Check the error messages
      await expect(dialog.getByText("Invalid email address")).toBeVisible()
      await expect(dialog.getByText("Password is required")).toBeVisible()
      await expect(
        dialog.getByText("Please confirm your password"),
      ).toBeVisible()
    })

    await test.step("Close the Dialog", async () => {
      const cancelBtn = dialog.getByRole("button", { name: "Cancel" })
      await cancelBtn.click()
      // Check if Add User button is visible after closing the dialog
      await expect(dialog).toBeHidden()
      await expect(addUserBtn).toBeVisible()
    })
  })

  test("Admin should fill out the Add User form, save then delete it", async ({
    page,
  }) => {
    const email = "becebal.burebista@example.com"
    const fullName = "Decebal Burebista"
    const password = "SecurePass123!"

    const addUserBtn = page.getByRole("button", { name: "Add User" })
    await expect(addUserBtn).toBeVisible()
    await addUserBtn.click()

    const dialog = page.getByRole("dialog", { name: "Add User" })
    await expect(dialog).toBeVisible()

    await test.step("Fill out text and password fields", async () => {
      await dialog.getByLabel("Email").fill(email)
      await dialog.getByLabel("Full Name").fill(fullName)
      await dialog.locator('input[name="password"]').fill(password)
      await dialog.locator('input[name="confirm_password"]').fill(password)

      // Toggle Checkboxes
      const superuserCheckbox = dialog.getByRole("checkbox", {
        name: "Is superuser?",
      })
      const activeCheckbox = dialog.getByRole("checkbox", {
        name: "Is active?",
      })

      await superuserCheckbox.check()
      await activeCheckbox.check()

      // Verify the data was entered correctly before saving
      await expect(dialog.getByLabel("Email")).toHaveValue(email)
      await expect(dialog.getByLabel("Full Name")).toHaveValue(fullName)
      await expect(dialog.getByLabel("Set Password")).toHaveValue(password)
      await expect(dialog.getByLabel("Confirm Password")).toHaveValue(password)
      await expect(superuserCheckbox).toBeChecked()
      await expect(activeCheckbox).toBeChecked()
    })

    await test.step("Save the User", async () => {
      const saveButton = dialog.getByRole("button", { name: "Save" })
      await saveButton.click()

      // Verify the dialog closes
      await expect(dialog).toBeHidden()
      await expect(addUserBtn).toBeVisible()
    })

    await test.step("Check the new user in the user table", async () => {
      await verifyUserRow(page, fullName, email, UserRole.SUPERUSER, "Active")
    })

    await test.step("Cleanup", async () => {
      const userRow = page.getByRole("row").filter({ hasText: email })

      // Click the "ellipsis" trigger inside that row
      await userRow
        .getByRole("button", { name: "menu" })
        .or(userRow.locator('[data-slot="dropdown-menu-trigger"]'))
        .click()

      // Click "Delete User" from the menu that appears globally
      await page.getByRole("menuitem", { name: "Delete User" }).click()

      // Confirm the deletion in the resulting dialog
      const confirmDialog = page.getByRole("dialog")
      await confirmDialog.getByRole("button", { name: "Delete" }).click()
    })
  })
})
