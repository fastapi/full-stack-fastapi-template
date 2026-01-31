import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { UsersService, type UserUpdateMe } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
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
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { cn } from "@/lib/utils"
import { handleError } from "@/utils"

const personalInfoSchema = z.object({
  full_name: z.string().max(30).optional().or(z.literal("")),
  email: z.string().email({ message: "Invalid email address" }),
})

type PersonalInfoFormData = z.infer<typeof personalInfoSchema>

export function PersonalInfoCard() {
  const queryClient = useQueryClient()
  const { user } = useAuth()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [editMode, setEditMode] = useState(false)

  const form = useForm<PersonalInfoFormData>({
    resolver: zodResolver(personalInfoSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      full_name: user?.full_name ?? undefined,
      email: user?.email ?? "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: UserUpdateMe) =>
      UsersService.updateUserMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Profile updated successfully")
      setEditMode(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
    },
  })

  const onSubmit = (data: PersonalInfoFormData) => {
    const payload: UserUpdateMe = {}
    if (data.full_name !== (user?.full_name ?? undefined)) {
      payload.full_name = data.full_name || null
    }
    if (data.email !== user?.email) {
      payload.email = data.email
    }
    if (Object.keys(payload).length === 0) return
    mutation.mutate(payload)
  }

  const onCancel = () => {
    form.reset({
      full_name: user?.full_name ?? undefined,
      email: user?.email ?? "",
    })
    setEditMode(false)
  }

  // Sync form when user loads or changes, but not while editing
  useEffect(() => {
    if (user && !editMode) {
      form.reset({
        full_name: user.full_name ?? undefined,
        email: user.email ?? "",
      })
    }
  }, [user?.id, user?.full_name, user?.email, editMode, form.reset, user])

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div>
          <CardTitle>Personal information</CardTitle>
          <CardDescription>
            Update your personal details and profile information.
          </CardDescription>
        </div>
        {!editMode && (
          <Button
            type="button"
            variant="outline"
            onClick={() => setEditMode(true)}
          >
            Edit
          </Button>
        )}
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            noValidate
            className="space-y-6"
          >
            <div className="grid gap-6 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="full_name"
                render={({ field }) =>
                  editMode ? (
                    <FormItem>
                      <FormLabel>Full name</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Your full name"
                          autoComplete="name"
                          disabled={mutation.isPending}
                          {...field}
                          value={field.value ?? ""}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  ) : (
                    <FormItem>
                      <FormLabel htmlFor="full-name-display">
                        Full name
                      </FormLabel>
                      <Input
                        id="full-name-display"
                        readOnly
                        disabled
                        value={field.value ?? ""}
                        placeholder="Your full name"
                        className={cn(
                          "bg-muted/50 border-muted cursor-default",
                          !field.value && "text-muted-foreground",
                        )}
                      />
                    </FormItem>
                  )
                }
              />
              <FormField
                control={form.control}
                name="email"
                render={({ field }) =>
                  editMode ? (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input
                          type="email"
                          placeholder="your@email.com"
                          autoComplete="email"
                          disabled={mutation.isPending}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  ) : (
                    <FormItem>
                      <FormLabel htmlFor="email-display">Email</FormLabel>
                      <Input
                        id="email-display"
                        readOnly
                        disabled
                        value={field.value ?? ""}
                        placeholder="your@email.com"
                        className={cn(
                          "bg-muted/50 border-muted cursor-default",
                          !field.value && "text-muted-foreground",
                        )}
                      />
                    </FormItem>
                  )
                }
              />
            </div>
            {editMode && (
              <div className="flex gap-3">
                <LoadingButton
                  type="submit"
                  loading={mutation.isPending}
                  disabled={!form.formState.isDirty || mutation.isPending}
                >
                  Save changes
                </LoadingButton>
                <Button
                  type="button"
                  variant="outline"
                  onClick={onCancel}
                  disabled={mutation.isPending}
                >
                  Cancel
                </Button>
              </div>
            )}
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
