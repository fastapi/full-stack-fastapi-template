import { UserPublic } from "@/client";

export const UserRole = {
  ADMIN: "admin",
  MANAGER: "manager",
  MEMBER: "member",
} as const;

export type UserRole = (typeof UserRole)[keyof typeof UserRole];

export type Action =
  | "listUsers"
  | "createUser"
  | "viewMetrics"
  | "updateAnyUser"
  | "deleteAnyUser";

const POLICY: Record<Action, UserRole[]> = {
  listUsers: [UserRole.ADMIN, UserRole.MANAGER],
  createUser: [UserRole.ADMIN],
  viewMetrics: [UserRole.ADMIN, UserRole.MANAGER],
  updateAnyUser: [UserRole.ADMIN],
  deleteAnyUser: [UserRole.ADMIN],
};

export const can = (
  user: UserPublic | null | undefined,
  action: Action,
): boolean => {
  if (!user?.role) return false;
  return POLICY[action].includes(user.role as UserRole);
};
