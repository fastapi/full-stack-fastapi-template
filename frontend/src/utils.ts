import { AxiosError } from "axios"

import type { UserMePublic } from "@/client"

function extractErrorMessage(err: Error): string {
  if (err instanceof AxiosError) {
    const errDetail = (err.response?.data as any)?.detail
    if (Array.isArray(errDetail) && errDetail.length > 0) {
      return errDetail[0].msg
    }
    if (typeof errDetail === "string") {
      return errDetail
    }
    return err.message
  }
  return "Something went wrong."
}

export const handleError = function (this: (msg: string) => void, err: Error) {
  const errorMessage = extractErrorMessage(err)
  this(errorMessage)
}

export const getInitials = (name: string): string => {
  return name
    .split(" ")
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase()
}

export const PERMISSIONS = {
  usersList: "users:list",
  usersCreate: "users:create",
  usersManage: "users:manage",
  metricsView: "metrics:view",
  systemAdmin: "system:admin",
} as const

export const hasPermission = (
  user: UserMePublic | null | undefined,
  code: string,
): boolean => {
  return user?.permissions.includes(code) ?? false
}
