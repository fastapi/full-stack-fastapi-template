import { UserType } from "@/lib/client";

export const USER_TYPES: { value: UserType; labelKey: "roleUser" | "roleCompany" | "roleAdmin" }[] = [
  { value: "normal", labelKey: "roleUser" },
  { value: "company", labelKey: "roleCompany" },
  { value: "admin", labelKey: "roleAdmin" },
];