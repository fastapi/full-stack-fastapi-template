"use client"

import { useToast } from "@chakra-ui/toast"
import type { UseToastOptions } from "@chakra-ui/toast"

export function useCustomToast() {
  const toast = useToast()

  const defaultOptions: UseToastOptions = {
    duration: 3000,
    isClosable: true,
    position: "top",
  }

  const success = (message: string, options: UseToastOptions = {}) =>
    toast({
      ...defaultOptions,
      ...options,
      title: message,
      status: "success",
    })

  const error = (message: string, options: UseToastOptions = {}) =>
    toast({
      ...defaultOptions,
      ...options,
      title: message,
      status: "error",
    })

  const warning = (message: string, options: UseToastOptions = {}) =>
    toast({
      ...defaultOptions,
      ...options,
      title: message,
      status: "warning",
    })

  const info = (message: string, options: UseToastOptions = {}) =>
    toast({
      ...defaultOptions,
      ...options,
      title: message,
      status: "info",
    })

  return {
    success,
    error,
    warning,
    info,
    showSuccessToast: success,
    showErrorToast: error,
  }
}

export default useCustomToast
