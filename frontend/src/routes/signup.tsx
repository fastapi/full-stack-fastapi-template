import { Container, Heading, Input, NativeSelectRoot, NativeSelectField, Text } from "@chakra-ui/react"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
} from "@tanstack/react-router"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FiLock, FiUser, FiMail } from "react-icons/fi"

import type { UserRegister } from "@/client"
import { Button } from "@/components/ui/button"
import { Field } from "@/components/ui/field"
import { InputGroup } from "@/components/ui/input-group"
import { PasswordInput } from "@/components/ui/password-input"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"
import { confirmPasswordRules, emailPattern, passwordRules } from "@/utils"

export const Route = createFileRoute("/signup")({
  component: SignUp,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/dashboard",
      })
    }
  },
})

interface UserRegisterForm extends UserRegister {
  confirm_password: string
}

function SignUp() {
  const { signUpMutation } = useAuth()
  const {
    register,
    handleSubmit,
    getValues,
    formState: { errors, isSubmitting },
  } = useForm<UserRegisterForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      email: "",
      full_name: "",
      password: "",
      confirm_password: "",
      user_type: "team_member",
    },
  })

  const onSubmit: SubmitHandler<UserRegisterForm> = (data) => {
    signUpMutation.mutate(data)
  }

  return (
    <Container
      as="form"
      onSubmit={handleSubmit(onSubmit)}
      h="100vh"
      maxW="sm"
      alignItems="stretch"
      justifyContent="center"
      gap={4}
      centerContent
    >
      <div style={{ textAlign: "center", marginBottom: "2rem" }}>
        <Heading
          size="4xl"
          bgGradient="to-r"
          gradientFrom="blue.400"
          gradientTo="purple.500"
          bgClip="text"
        >
          Sign Up
        </Heading>
        <Text fontSize="md" color="fg.muted" mt={2}>
          Create your Mosaic account
        </Text>
      </div>

      <Field
        invalid={!!errors.full_name}
        errorText={errors.full_name?.message}
      >
        <InputGroup w="100%" startElement={<FiUser />}>
          <Input
            minLength={3}
            {...register("full_name", {
              required: "Full Name is required",
            })}
            placeholder="Full Name"
            type="text"
          />
        </InputGroup>
      </Field>

      <Field invalid={!!errors.email} errorText={errors.email?.message}>
        <InputGroup w="100%" startElement={<FiMail />}>
          <Input
            {...register("email", {
              required: "Email is required",
              pattern: emailPattern,
            })}
            placeholder="Email"
            type="email"
          />
        </InputGroup>
      </Field>

      <Field label="Account Type">
        <NativeSelectRoot>
          <NativeSelectField {...register("user_type")} defaultValue="team_member">
            <option value="team_member">Team Member</option>
            <option value="client">Client</option>
          </NativeSelectField>
        </NativeSelectRoot>
      </Field>

      <PasswordInput
        type="password"
        startElement={<FiLock />}
        {...register("password", passwordRules())}
        placeholder="Password"
        errors={errors}
      />
      <PasswordInput
        type="confirm_password"
        startElement={<FiLock />}
        {...register("confirm_password", confirmPasswordRules(getValues))}
        placeholder="Confirm Password"
        errors={errors}
      />
      <Button variant="solid" type="submit" loading={isSubmitting}>
        Sign Up
      </Button>
      <Text>
        Already have an account?{" "}
        <RouterLink to="/" className="main-link">
          Log In
        </RouterLink>
      </Text>
    </Container>
  )
}
