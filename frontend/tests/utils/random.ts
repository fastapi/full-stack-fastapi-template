import { randomBytes } from "crypto";

export const randomEmail = () =>
  `test_${randomBytes(6).toString("base64url")}@example.com`

export const randomTeamName = () =>
  `Team ${randomBytes(6).toString("base64url")}`

export const randomPassword = () => randomBytes(12).toString("base64url")

export const slugify = (text: string) =>
  text
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^\w-]+/g, "")
