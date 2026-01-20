import { expect, Page } from "@playwright/test";

export enum UserRole {
    SUPERUSER = 'Superuser',
    USER = 'User'
}


export async function verifyUserRow(page: Page, name: string, email: string, role: UserRole, status: string, createUser: boolean = false) {
    const row = page.getByRole('row').filter({ hasText: name });
    await expect(row.getByText(name)).toBeVisible();

    if (createUser) {
        await expect(row.locator('[data-slot="badge"]', { hasText: 'You' })).toBeVisible();
    }

    await expect(row.getByText(email)).toBeVisible();
    const roleBadge = row.locator('[data-slot="badge"]').filter({ hasText: role });
    await expect(roleBadge).toBeVisible();

    if (role === UserRole.SUPERUSER) {
        await expect(roleBadge).toHaveClass(/bg-primary/);
    }

    await expect(row.getByText(status)).toBeVisible();
}
