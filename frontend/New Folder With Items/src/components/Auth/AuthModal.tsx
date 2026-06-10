import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import type { Body_login_login_access_token as AccessToken } from "@/client"
import { LoginService } from "@/client"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const signInSchema = z.object({
  username: z.string().email(),
  password: z.string().min(8),
}) satisfies z.ZodType<AccessToken>

const signUpSchema = z
  .object({
    email: z.string().email(),
    full_name: z.string().min(1),
    password: z.string().min(8),
    confirm_password: z.string().min(1),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "The passwords don't match",
    path: ["confirm_password"],
  })

type SignInData = z.infer<typeof signInSchema>
type SignUpData = z.infer<typeof signUpSchema>

export default function AuthModal({
  open,
  setOpen,
  initialTab = "signin",
}: {
  open: boolean
  setOpen: (open: boolean) => void
  initialTab?: "signin" | "signup"
}) {
  const { loginMutation, signUpMutation } = useAuth()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [tab, setTab] = useState<"signin" | "signup" | "recover">(initialTab)

  const signInForm = useForm<SignInData>({
    resolver: zodResolver(signInSchema),
    mode: "onBlur",
    defaultValues: { username: "", password: "" },
  })

  const signUpForm = useForm<SignUpData>({
    resolver: zodResolver(signUpSchema),
    mode: "onBlur",
    defaultValues: {
      email: "",
      full_name: "",
      password: "",
      confirm_password: "",
    },
  })

  const recoverForm = useForm<{ email: string }>({
    resolver: zodResolver(z.object({ email: z.string().email() })),
    mode: "onBlur",
    defaultValues: { email: "" },
  })

  const recoverMutation = useMutation({
    mutationFn: (data: { email: string }) =>
      LoginService.recoverPassword({ email: data.email }),
    onSuccess: () => {
      showSuccessToast("If that email exists, a recovery message has been sent")
      setTab("signin")
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSignIn = (data: SignInData) => {
    if (loginMutation.isPending) return
    loginMutation.mutate(data)
  }

  const onSignUp = (data: SignUpData) => {
    if (signUpMutation.isPending) return
    const { confirm_password: _c, ...submit } = data
    signUpMutation.mutate(submit)
  }

  const onRecover = (data: { email: string }) => {
    if (recoverMutation.isPending) return
    recoverMutation.mutate(data)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-center">
            Welcome to docs2excel.ai
          </DialogTitle>
          <DialogDescription className="text-center mb-2">
            Log in and subscribe to unlock advanced features
          </DialogDescription>
        </DialogHeader>

        <Tabs
          value={tab}
          onValueChange={(v: string) =>
            setTab(v as "signin" | "signup" | "recover")
          }
        >
          <TabsList>
            <TabsTrigger value="signin">Sign In</TabsTrigger>
            <TabsTrigger value="signup">Sign Up</TabsTrigger>
          </TabsList>

          <TabsContent value="signin">
            <Form {...signInForm}>
              <form
                onSubmit={signInForm.handleSubmit(onSignIn)}
                className="flex flex-col gap-6"
              >
                <div className="grid gap-4">
                  <FormField
                    control={signInForm.control}
                    name="username"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Email</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Enter your email"
                            type="email"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={signInForm.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <div className="flex items-center">
                          <FormLabel>Password</FormLabel>
                          <button
                            type="button"
                            onClick={() => setTab("recover")}
                            className="ml-auto text-sm underline-offset-4 hover:underline"
                          >
                            Forgot your password?
                          </button>
                        </div>
                        <FormControl>
                          <PasswordInput
                            placeholder="Enter your password"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <LoadingButton
                    type="submit"
                    loading={loginMutation.isPending}
                  >
                    Sign In
                  </LoadingButton>
                </div>
              </form>
            </Form>
          </TabsContent>

          <TabsContent value="signup">
            <Form {...signUpForm}>
              <form
                onSubmit={signUpForm.handleSubmit(onSignUp)}
                className="flex flex-col gap-6"
              >
                <div className="grid gap-4">
                  <FormField
                    control={signUpForm.control}
                    name="full_name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Full name</FormLabel>
                        <FormControl>
                          <Input placeholder="Full name" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={signUpForm.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Email</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="user@example.com"
                            type="email"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={signUpForm.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Password</FormLabel>
                        <FormControl>
                          <PasswordInput placeholder="Password" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={signUpForm.control}
                    name="confirm_password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Confirm Password</FormLabel>
                        <FormControl>
                          <PasswordInput
                            placeholder="Confirm Password"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <LoadingButton
                    type="submit"
                    loading={signUpMutation.isPending}
                  >
                    Sign Up
                  </LoadingButton>
                </div>

                <div className="text-center text-sm">
                  Already have an account?{" "}
                  <button
                    type="button"
                    onClick={() => setTab("signin")}
                    className="underline underline-offset-4"
                  >
                    Log in
                  </button>
                </div>
              </form>
            </Form>
          </TabsContent>

          <TabsContent value="recover">
            <Form {...recoverForm}>
              <form
                onSubmit={recoverForm.handleSubmit(onRecover)}
                className="flex flex-col gap-6"
              >
                <div className="grid gap-4">
                  <FormField
                    control={recoverForm.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Email</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Enter your account email"
                            type="email"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <LoadingButton
                    type="submit"
                    loading={recoverMutation.isPending}
                  >
                    Send Recovery Email
                  </LoadingButton>
                </div>

                <div className="text-center text-sm">
                  Remembered your password?{" "}
                  <button
                    type="button"
                    onClick={() => setTab("signin")}
                    className="underline underline-offset-4"
                  >
                    Sign in
                  </button>
                </div>
              </form>
            </Form>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}
