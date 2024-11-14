// This component handles user login functionality. It uses Chakra UI for styling, React Hook Form 
// for form management, and custom hooks for authentication. Users are redirected to the home page 
// if they are already logged in, and the form includes validation and error handling.

import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons"
import {
  Button,
  Container,
  FormControl,
  FormErrorMessage,
  Icon,
  Image,
  Input,
  InputGroup,
  InputRightElement,
  Link,
  Text,
  useBoolean,
} from "@chakra-ui/react"
import {
  Link as RouterLink,
  createFileRoute,
  redirect,
} from "@tanstack/react-router"
import { type SubmitHandler, useForm } from "react-hook-form"

import Logo from "/assets/images/fastapi-logo.svg" // Import logo for branding
import type { Body_login_login_access_token as AccessToken } from "../client" // API typing for login
import useAuth, { isLoggedIn } from "../hooks/useAuth" // Custom hooks for auth logic
import { emailPattern } from "../utils" // Regex pattern for email validation

// Define the login route with a redirect if the user is already logged in
export const Route = createFileRoute("/login")({
  component: Login,
  beforeLoad: async () => {
    if (isLoggedIn()) { // Check if user is logged in
      throw redirect({
        to: "/", // Redirect to home if logged in
      })
    }
  },
})

// Main Login component
function Login() {
  const [show, setShow] = useBoolean() // Toggle visibility of password
  const { loginMutation, error, resetError } = useAuth() // Custom hook for login and error handling
  const {
    register, // Register input fields for validation
    handleSubmit, // Handle form submission
    formState: { errors, isSubmitting },
  } = useForm<AccessToken>({ // Set up form with React Hook Form and default values
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      password: "",
    },
  })

  // Function to handle form submission
  const onSubmit: SubmitHandler<AccessToken> = async (data) => {
    if (isSubmitting) return

    resetError() // Reset error state before attempting login

    try {
      await loginMutation.mutateAsync(data) // Attempt login with provided data
    } catch {
      // Error is handled by the useAuth hook
    }
  }

  return (
    <>
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
        <Image
          src={Logo} // Display logo at the top of the form
          alt="FastAPI logo"
          height="auto"
          maxW="2xs"
          alignSelf="center"
          mb={4}
        />
        
        {/* Username input with validation */}
        <FormControl id="username" isInvalid={!!errors.username || !!error}>
          <Input
            id="username"
            {...register("username", {
              required: "Username is required",
              pattern: emailPattern, // Validate email pattern
            })}
            placeholder="Email"
            type="email"
            required
          />
          {errors.username && (
            <FormErrorMessage>{errors.username.message}</FormErrorMessage> // Display validation error
          )}
        </FormControl>

        {/* Password input with toggle visibility */}
        <FormControl id="password" isInvalid={!!error}>
          <InputGroup>
            <Input
              {...register("password", {
                required: "Password is required",
              })}
              type={show ? "text" : "password"}
              placeholder="Password"
              required
            />
            <InputRightElement
              color="ui.dim"
              _hover={{
                cursor: "pointer",
              }}
            >
              <Icon
                as={show ? ViewOffIcon : ViewIcon} // Toggle visibility icon
                onClick={setShow.toggle}
                aria-label={show ? "Hide password" : "Show password"}
              >
                {show ? <ViewOffIcon /> : <ViewIcon />}
              </Icon>
            </InputRightElement>
          </InputGroup>
          {error && <FormErrorMessage>{error}</FormErrorMessage>} // Display error from auth hook
        </FormControl>

        {/* Forgot password link */}
        <Link as={RouterLink} to="/recover-password" color="blue.500">
          Forgot password?
        </Link>

        {/* Submit button */}
        <Button variant="primary" type="submit" isLoading={isSubmitting}>
          Log In
        </Button>

        {/* Sign up link */}
        <Text>
          Don't have an account?{" "}
          <Link as={RouterLink} to="/signup" color="blue.500">
            Sign up
          </Link>
        </Text>
      </Container>
    </>
  )
}
