// This component provides a form for users to initiate password recovery by entering their email address. 
// If the user is logged in, they are redirected to the home page. Upon submitting a valid email, a password 
// recovery email is sent, and a success toast notification is shown.

import {
  Button,
  Container,
  FormControl,
  FormErrorMessage,
  Heading,
  Input,
  Text,
} from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { type SubmitHandler, useForm } from "react-hook-form"

import { type ApiError, LoginService } from "../client" // Import LoginService for password recovery
import { isLoggedIn } from "../hooks/useAuth" // Import utility to check if user is logged in
import useCustomToast from "../hooks/useCustomToast" // Custom hook for displaying toast notifications
import { emailPattern, handleError } from "../utils" // Utilities for email validation and error handling

// Define FormData interface for form input structure
interface FormData {
  email: string
}

// Set up routing for password recovery page, redirecting logged-in users to the home page
export const Route = createFileRoute("/recover-password")({
  component: RecoverPassword,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/",
      })
    }
  },
})

// Main component function for password recovery form
function RecoverPassword() {
  // Set up form handling with react-hook-form
  const {
    register, // Register form fields
    handleSubmit, // Handle form submission
    reset, // Reset form fields on success
    formState: { errors, isSubmitting },
  } = useForm<FormData>()
  const showToast = useCustomToast() // Custom hook to display toast notifications

  // Async function to call password recovery API
  const recoverPassword = async (data: FormData) => {
    await LoginService.recoverPassword({
      email: data.email,
    })
  }

  // Mutation for handling API call with success and error handling
  const mutation = useMutation({
    mutationFn: recoverPassword, // Function to execute on mutation
    onSuccess: () => {
      showToast(
        "Email sent.",
        "We sent an email with a link to get back into your account.",
        "success",
      )
      reset() // Reset form fields after successful request
    },
    onError: (err: ApiError) => {
      handleError(err, showToast) // Show error using handleError utility
    },
  })

  // Function for handling form submission
  const onSubmit: SubmitHandler<FormData> = async (data) => {
    mutation.mutate(data) // Trigger mutation on form submission
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
      <Heading size="xl" color="ui.main" textAlign="center" mb={2}>
        Password Recovery
      </Heading>
      <Text align="center">
        A password recovery email will be sent to the registered account.
      </Text>
      
      {/* Email input field with validation */}
      <FormControl isInvalid={!!errors.email}>
        <Input
          id="email"
          {...register("email", {
            required: "Email is required",
            pattern: emailPattern, // Pattern for email validation
          })}
          placeholder="Email"
          type="email"
        />
        {errors.email && (
          <FormErrorMessage>{errors.email.message}</FormErrorMessage> // Display error message for email
        )}
      </FormControl>
      
      {/* Submit button with loading state */}
      <Button variant="primary" type="submit" isLoading={isSubmitting}>
        Continue
      </Button>
    </Container>
  )
}
