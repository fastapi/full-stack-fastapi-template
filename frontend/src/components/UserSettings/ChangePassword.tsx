import { Button } from "@/components/ui/button"
import { Field } from "@/components/ui/field"
import { Box, Container, Heading, Input } from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import { type ApiError, type UpdatePassword, UsersService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { confirmPasswordRules, handleError, passwordRules } from "@/utils"

interface UpdatePasswordForm extends UpdatePassword {
  confirm_password: string
}

const ChangePassword = () => {
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    getValues,
    formState: { errors, isSubmitting },
  } = useForm<UpdatePasswordForm>({
    mode: "onBlur",
    criteriaMode: "all",
  })

  const mutation = useMutation({
    mutationFn: (data: UpdatePassword) =>
      UsersService.updatePasswordMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Password updated successfully.")
      reset()
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  const onSubmit: SubmitHandler<UpdatePasswordForm> = async (data) => {
    mutation.mutate(data)
  }

  return (
    <>
      <Container maxW="full">
        <Heading size="sm" py={4}>
          Change Password
        </Heading>
        <Box
          w={{ sm: "full", md: "50%" }}
          as="form"
          onSubmit={handleSubmit(onSubmit)}
        >
          <Field
            label="Current Password"
            required
            invalid={!!errors.current_password}
            errorText={errors.current_password?.message}
          >
            <Input
              {...register("current_password")}
              placeholder="Password"
              type="password"
              w="auto"
            />
          </Field>
          <Field
            mt={4}
            label="Set Password"
            required
            invalid={!!errors.new_password}
            errorText={errors.new_password?.message}
          >
            <Input
              {...register("new_password", passwordRules())}
              placeholder="Password"
              type="password"
              w="auto"
            />
          </Field>
          <Field
            mt={4}
            label="Confirm Password"
            required
            invalid={!!errors.confirm_password}
            errorText={errors.confirm_password?.message}
          >
            <Input
              {...register("confirm_password", confirmPasswordRules(getValues))}
              placeholder="Password"
              type="password"
              w="auto"
            />
          </Field>
          <Button
            colorPalette="blue"
            mt={4}
            type="submit"
            loading={isSubmitting}
          >
            Save
          </Button>
        </Box>
      </Container>
    </>
  )
}
export default ChangePassword
