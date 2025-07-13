import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Controller, type SubmitHandler, useForm } from "react-hook-form"

import { type PrivateUserCreate, DefaultService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { emailPattern, handleError } from "@/utils"
import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Flex,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useState } from "react"
import { FaPlus } from "react-icons/fa"
import { Checkbox } from "../ui/checkbox"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

interface UserCreateFormData extends PrivateUserCreate {
  role: string
}

const AddUser = () => {
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const [open, setOpen] = useState(false)
  
  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors, isSubmitting },
  } = useForm<UserCreateFormData>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      email: "",
      full_name: "",
      password: "",
      role: "user",
      is_verified: false,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: UserCreateFormData) => {
      // For now, use DefaultService.untaggedCreateUser
      // TODO: Implement proper role-based user creation
      const userData: PrivateUserCreate = {
        email: data.email,
        full_name: data.full_name,
        password: data.password,
        is_verified: data.is_verified,
      }
      return DefaultService.untaggedCreateUser({ requestBody: userData })
    },
    onSuccess: () => {
      showSuccessToast("User created successfully.")
      reset()
      setOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

  const onSubmit: SubmitHandler<UserCreateFormData> = (data) => {
    mutation.mutate(data)
  }

  return (
    <>
      <DialogRoot 
        size={{ base: "xs", md: "md" }} 
        placement="center" 
        open={open} 
        onOpenChange={({ open }) => setOpen(open)}
      >
        <DialogTrigger asChild>
          <Button
            variant="solid"
            colorScheme="blue"
            size="sm"
          >
            <FaPlus /> Add User
          </Button>
        </DialogTrigger>
        <DialogContent>
          <form onSubmit={handleSubmit(onSubmit)}>
            <DialogHeader>
              <DialogTitle>Add User</DialogTitle>
            </DialogHeader>
            <DialogBody>
              <Text mb={4}>Create a new user account.</Text>
              <VStack gap={4}>
                <Field
                  required
                  invalid={!!errors.email}
                  errorText={errors.email?.message}
                  label="Email"
                >
                  <Input
                    id="email"
                    {...register("email", {
                      required: "Email is required",
                      pattern: emailPattern,
                    })}
                    placeholder="Email"
                    type="email"
                  />
                </Field>

                <Field
                  required
                  invalid={!!errors.full_name}
                  errorText={errors.full_name?.message}
                  label="Full Name"
                >
                  <Input
                    id="full_name"
                    {...register("full_name", {
                      required: "Full name is required",
                    })}
                    placeholder="Full Name"
                    type="text"
                  />
                </Field>

                <Field
                  required
                  invalid={!!errors.password}
                  errorText={errors.password?.message}
                  label="Password"
                >
                  <Input
                    id="password"
                    {...register("password", {
                      required: "Password is required",
                      minLength: {
                        value: 8,
                        message: "Password must be at least 8 characters",
                      },
                    })}
                    placeholder="Password"
                    type="password"
                  />
                </Field>

                <Field
                  required
                  invalid={!!errors.role}
                  errorText={errors.role?.message}
                  label="User Role"
                >
                  <Controller
                    name="role"
                    control={control}
                    rules={{ required: "Role is required" }}
                    render={({ field }) => (
                      <select
                        {...field}
                        style={{
                          width: "100%",
                          padding: "8px 12px",
                          borderRadius: "6px",
                          border: "1px solid #e2e8f0",
                          fontSize: "14px",
                          backgroundColor: "white",
                        }}
                      >
                        {roleOptions.map((role) => (
                          <option key={role.value} value={role.value}>
                            {role.label}
                          </option>
                        ))}
                      </select>
                    )}
                  />
                </Field>
              </VStack>

              <Flex mt={4} direction="column" gap={4}>
                <Controller
                  control={control}
                  name="is_verified"
                  render={({ field }) => (
                    <Field disabled={field.disabled} colorPalette="teal">
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={({ checked }) => field.onChange(checked)}
                      >
                        Is verified?
                      </Checkbox>
                    </Field>
                  )}
                />
              </Flex>
            </DialogBody>

            <DialogFooter gap={2}>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
              </DialogActionTrigger>
              <Button
                variant="solid"
                type="submit"
                loading={isSubmitting}
              >
                Add User
              </Button>
            </DialogFooter>
            <DialogCloseTrigger />
          </form>
        </DialogContent>
      </DialogRoot>
    </>
  )
}

const roleOptions = [
  { label: "User", value: "user" },
  { label: "Trainer", value: "trainer" },
  { label: "Counselor", value: "counselor" },
  { label: "Admin", value: "admin" },
]

export default AddUser
