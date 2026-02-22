import { zodResolver } from "@hookform/resolvers/zod"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
} from "@tanstack/react-router"
import { useEffect, useRef, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import type { Body_login_login_access_token as AccessToken } from "@/client"
import { AuthLayout } from "@/components/Common/AuthLayout"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import { PasswordInput } from "@/components/ui/password-input"
import { Separator } from "@/components/ui/separator"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"
import { renderGoogleSignInButton } from "@/lib/googleIdentity"

const formSchema = z.object({
  username: z.email(),
  password: z
    .string()
    .min(1, { message: "Password is required" })
    .min(8, { message: "Password must be at least 8 characters" }),
}) satisfies z.ZodType<AccessToken>

type FormData = z.infer<typeof formSchema>

export const Route = createFileRoute("/login")({
  component: Login,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/",
      })
    }
  },
  head: () => ({
    meta: [
      {
        title: "Log In - TemplateForge AI",
      },
    ],
  }),
})

function Login() {
  const { loginMutation, googleLoginMutation } = useAuth()
  const googleButtonRef = useRef<HTMLDivElement>(null)
  const [googleInitError, setGoogleInitError] = useState<string | null>(null)
  const googleClientId = (import.meta.env.VITE_GOOGLE_CLIENT_ID || "").trim()
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      password: "",
    },
  })

  const onSubmit = (data: FormData) => {
    if (loginMutation.isPending) return
    loginMutation.mutate(data)
  }

  useEffect(() => {
    if (!googleClientId || !googleButtonRef.current) return

    let cancelled = false
    setGoogleInitError(null)

    renderGoogleSignInButton({
      container: googleButtonRef.current,
      clientId: googleClientId,
      onCredential: (idToken) => {
        if (googleLoginMutation.isPending) return
        googleLoginMutation.mutate(idToken)
      },
    }).catch((error) => {
      if (cancelled) return
      setGoogleInitError(
        error instanceof Error
          ? error.message
          : "Failed to initialize Google login",
      )
    })

    return () => {
      cancelled = true
    }
  }, [googleLoginMutation])

  return (
    <AuthLayout>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-6"
        >
          <div className="flex flex-col items-center gap-2 text-center">
            <h1 className="text-2xl font-bold">Login to your account</h1>
          </div>

          <div className="grid gap-4">
            <FormField
              control={form.control}
              name="username"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      data-testid="email-input"
                      placeholder="user@example.com"
                      type="email"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-xs" />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <div className="flex items-center">
                    <FormLabel>Password</FormLabel>
                    <RouterLink
                      to="/recover-password"
                      className="ml-auto text-sm underline-offset-4 hover:underline"
                    >
                      Forgot your password?
                    </RouterLink>
                  </div>
                  <FormControl>
                    <PasswordInput
                      data-testid="password-input"
                      placeholder="Password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-xs" />
                </FormItem>
              )}
            />

            <LoadingButton type="submit" loading={loginMutation.isPending}>
              Log In
            </LoadingButton>

            {googleClientId ? (
              <>
                <div className="relative my-1">
                  <div className="absolute inset-0 flex items-center">
                    <Separator />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-2 text-muted-foreground">
                      or continue with
                    </span>
                  </div>
                </div>

                <div className="grid gap-2">
                  <div
                    ref={googleButtonRef}
                    className={
                      googleLoginMutation.isPending ? "opacity-70" : ""
                    }
                  />
                  {googleLoginMutation.isPending ? (
                    <p className="text-center text-xs text-muted-foreground">
                      Signing in with Google...
                    </p>
                  ) : null}
                  {googleInitError ? (
                    <p className="text-center text-xs text-destructive">
                      {googleInitError}
                    </p>
                  ) : null}
                </div>
              </>
            ) : null}
          </div>

          <div className="text-center text-sm">
            Don't have an account yet?{" "}
            <RouterLink to="/signup" className="underline underline-offset-4">
              Sign up
            </RouterLink>
          </div>
        </form>
      </Form>
    </AuthLayout>
  )
}
