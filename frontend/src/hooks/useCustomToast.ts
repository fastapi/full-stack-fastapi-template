import { toaster } from "@/components/ui/toaster"

const useCustomToast = () => {
  const showToast = (
    title: string,
    description: string,
    type: "success" | "error",
  ) => {
    toaster.create({
      title,
      description,
      type,
      meta: { closable: true },
    })
  }

  const showErrorToast = (description: string) => {
    showToast("An error occured", description, "error")
  }

  const showSuccessToast = (description: string) => {
    showToast("Success!", description, "success")
  }

  return { showToast, showSuccessToast, showErrorToast }
}

export default useCustomToast
