import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { type UpdatePassword, UsersService } from "@/client"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { LoadingButton } from "@/components/ui/loading-button"
import { PasswordInput } from "@/components/ui/password-input"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

const PASSWORD_MIN_LENGTH = 8

const passwordSchema = z
  .string()
  .min(1, { message: "Password is required" })
  .min(PASSWORD_MIN_LENGTH, {
    message: `Password must be at least ${PASSWORD_MIN_LENGTH} characters`,
  })

const changePasswordSchema = z
  .object({
    current_password: passwordSchema,
    new_password: passwordSchema,
    confirm_password: z
      .string()
      .min(1, { message: "Please confirm your new password" }),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  })
  .refine((data) => data.new_password !== data.current_password, {
    message: "New password cannot be the same as the current one",
    path: ["new_password"],
  })

type ChangePasswordFormData = z.infer<typeof changePasswordSchema>

export interface ChangePasswordProps {
  /** Called after password is updated successfully (e.g. to close a dialog) */
  onSuccess?: () => void
  /** When true, omits the heading and adjusts layout for use inside a dialog */
  embedded?: boolean
}

export default function ChangePassword({
  onSuccess,
  embedded,
}: ChangePasswordProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      current_password: "",
      new_password: "",
      confirm_password: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: UpdatePassword) =>
      UsersService.updatePasswordMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Password updated successfully")
      form.reset()
      onSuccess?.()
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: ChangePasswordFormData) => {
    if (mutation.isPending) return
    mutation.mutate(data)
  }

  return (
    <div className={embedded ? "pt-1" : "max-w-md"}>
      {!embedded && (
        <h2 className="text-lg font-semibold tracking-tight pb-4">
          Change password
        </h2>
      )}
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          noValidate
          className="flex flex-col gap-6"
        >
          <FormField
            control={form.control}
            name="current_password"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Current password</FormLabel>
                <FormControl>
                  <PasswordInput
                    data-testid="current-password-input"
                    placeholder="••••••••"
                    autoComplete="current-password"
                    aria-invalid={fieldState.invalid}
                    disabled={mutation.isPending}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="new_password"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>New password</FormLabel>
                <FormControl>
                  <PasswordInput
                    data-testid="new-password-input"
                    placeholder="••••••••"
                    autoComplete="new-password"
                    aria-invalid={fieldState.invalid}
                    disabled={mutation.isPending}
                    {...field}
                  />
                </FormControl>
                <FormDescription>
                  At least {PASSWORD_MIN_LENGTH} characters
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="confirm_password"
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Confirm new password</FormLabel>
                <FormControl>
                  <PasswordInput
                    data-testid="confirm-password-input"
                    placeholder="••••••••"
                    autoComplete="new-password"
                    aria-invalid={fieldState.invalid}
                    disabled={mutation.isPending}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <LoadingButton
            type="submit"
            loading={mutation.isPending}
            disabled={!form.formState.isDirty || mutation.isPending}
            className={embedded ? "w-full sm:w-auto" : "w-full sm:w-auto"}
          >
            Update password
          </LoadingButton>
        </form>
      </Form>
    </div>
  )
}
