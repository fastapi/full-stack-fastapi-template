import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"

import {
  type Body_login_login_access_token as AccessToken,
  LoginService,
  OpenAPI,
  type UserPublic,
  type UserRegister,
  UsersService,
} from "@/client"
import { handleError } from "@/utils"
import useCustomToast from "./useCustomToast"

const isLoggedIn = () => {
  return localStorage.getItem("access_token") !== null
}

const useAuth = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()

  const { data: user } = useQuery<UserPublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: UsersService.readUserMe,
    enabled: isLoggedIn(),
  })

  const signUpMutation = useMutation({
    mutationFn: (data: UserRegister) =>
      UsersService.registerUser({ requestBody: data }),
    onSuccess: () => {
      navigate({ to: "/login" })
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

  const login = async (data: AccessToken) => {
    const response = await LoginService.loginAccessToken({
      formData: data,
    })
    localStorage.setItem("access_token", response.access_token)
  }

  const loginWithGoogleIdToken = async (idToken: string) => {
    const apiBase = OpenAPI.BASE.replace(/\/$/, "")
    const response = await fetch(`${apiBase}/api/v1/login/google`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ id_token: idToken }),
    })

    const payload = (await response.json().catch(() => ({}))) as {
      access_token?: string
      detail?: string
    }

    if (!response.ok || !payload.access_token) {
      throw new Error(payload.detail || "Google login failed")
    }

    localStorage.setItem("access_token", payload.access_token)
  }

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      navigate({ to: "/" })
    },
    onError: handleError.bind(showErrorToast),
  })

  const googleLoginMutation = useMutation({
    mutationFn: loginWithGoogleIdToken,
    onSuccess: () => {
      navigate({ to: "/" })
    },
    onError: (error) => {
      showErrorToast(
        error instanceof Error ? error.message : "Google login failed",
      )
    },
  })

  const logout = () => {
    localStorage.removeItem("access_token")
    navigate({ to: "/login" })
  }

  return {
    signUpMutation,
    loginMutation,
    googleLoginMutation,
    logout,
    user,
  }
}

export { isLoggedIn }
export default useAuth
