// Utility functions for form validation patterns and error handling in the app.
// Includes regular expressions for email and name validation, as well as password rules.
// Also provides an error handling function to display error messages in toasts.

import type { ApiError } from "./client"

// emailPattern: Regular expression for validating email addresses with error message
export const emailPattern = {
  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
  message: "Invalid email address",
}

// namePattern: Regular expression for validating names with up to 30 alphabetic or accented characters
export const namePattern = {
  value: /^[A-Za-z\s\u00C0-\u017F]{1,30}$/,
  message: "Invalid name",
}

// passwordRules: Returns an object containing password validation rules, including minimum length
// Optionally makes the password field required based on the isRequired argument
export const passwordRules = (isRequired = true) => {
  const rules: any = {
    minLength: {
      value: 8,
      message: "Password must be at least 8 characters",
    },
  }

  if (isRequired) {
    rules.required = "Password is required"
  }

  return rules
}

// confirmPasswordRules: Returns an object containing validation rules for confirming a password
// Uses a validate function to check if the password matches the confirmation field
export const confirmPasswordRules = (
  getValues: () => any, // Function to retrieve form values
  isRequired = true,
) => {
  const rules: any = {
    validate: (value: string) => {
      const password = getValues().password || getValues().new_password
      return value === password ? true : "The passwords do not match"
    },
  }

  if (isRequired) {
    rules.required = "Password confirmation is required"
  }

  return rules
}

// handleError: Function to handle API errors by displaying an error toast message
// Uses a custom toast function to display error details to the user
export const handleError = (err: ApiError, showToast: any) => {
  const errDetail = (err.body as any)?.detail
  let errorMessage = errDetail || "Something went wrong."
  if (Array.isArray(errDetail) && errDetail.length > 0) {
    errorMessage = errDetail[0].msg
  }
  showToast("Error", errorMessage, "error")
}
