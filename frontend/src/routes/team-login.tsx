import { Container, Heading, Input, Text } from "@chakra-ui/react"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
} from "@tanstack/react-router"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FiLock, FiMail } from "react-icons/fi"

import type { Body_login_login_access_token as AccessToken } from "@/client"
import { Button } from "@/components/ui/button"
import { Field } from "@/components/ui/field"
import { InputGroup } from "@/components/ui/input-group"
import { PasswordInput } from "@/components/ui/password-input"
import useAuth, { isLoggedIn } from "@/hooks/useAuth"
import { emailPattern, passwordRules } from "@/utils"

export const Route = createFileRoute("/team-login")({
  component: TeamLogin,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/dashboard",
      })
    }
  },
})

function TeamLogin() {
  const { loginMutation, error, resetError } = useAuth()
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AccessToken>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      password: "",
    },
  })

  const onSubmit: SubmitHandler<AccessToken> = async (data) => {
    if (isSubmitting) return

    resetError()

    try {
      await loginMutation.mutateAsync(data)
    } catch {
      // error is handled by useAuth hook
    }
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
          gradientTo="blue.600"
          bgClip="text"
        >
          Team Member Login
        </Heading>
        <Text fontSize="md" color="fg.muted" mt={2}>
          Access your organization's projects
        </Text>
      </div>
      <Field
        invalid={!!errors.username}
        errorText={errors.username?.message || !!error}
      >
        <InputGroup w="100%" startElement={<FiMail />}>
          <Input
            {...register("username", {
              required: "Username is required",
              pattern: emailPattern,
            })}
            placeholder="Email"
            type="email"
          />
        </InputGroup>
      </Field>
      <PasswordInput
        type="password"
        startElement={<FiLock />}
        {...register("password", passwordRules())}
        placeholder="Password"
        errors={errors}
      />
      <RouterLink to="/recover-password" className="main-link">
        Forgot Password?
      </RouterLink>
      <Button variant="solid" colorScheme="blue" type="submit" loading={isSubmitting} size="md">
        Log In
      </Button>
      <Text>
        <RouterLink to="/" className="main-link">
          ← Back to Home
        </RouterLink>
      </Text>
    </Container>
  )
}
