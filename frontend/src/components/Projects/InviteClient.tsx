import { useState } from "react"
import {
  DialogRoot,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogBody,
  DialogFooter,
  DialogCloseTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Field } from "@/components/ui/field"
import { Input, Text } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { FiUserPlus } from "react-icons/fi"
import useCustomToast from "@/hooks/useCustomToast"

interface InviteClientProps {
  projectId: string
}

export function InviteClient({ projectId }: InviteClientProps) {
  const [open, setOpen] = useState(false)
  const [email, setEmail] = useState("")
  const [emailError, setEmailError] = useState("")
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const inviteMutation = useMutation({
    mutationFn: async (email: string) => {
      const baseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, '')
      const url = `${baseUrl}/api/v1/projects/${projectId}/access/invite-by-email`
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          role: "viewer",
          can_comment: true,
          can_download: true,
        }),
      })
      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.detail || "Failed to invite client")
      }
      return response.json()
    },
    onSuccess: (data) => {
      if (data.is_pending) {
        showSuccessToast("Invitation created! Client will get access when they sign up with this email.")
      } else {
        showSuccessToast("Client invited successfully!")
      }
      queryClient.invalidateQueries({ queryKey: ["projectAccess", projectId] })
      setOpen(false)
      setEmail("")
      setEmailError("")
    },
    onError: (error: any) => {
      const message = error?.message || "Failed to invite client"
      showErrorToast(message)
    },
  })

  const handleInvite = () => {
    // Validate email
    if (!email.trim()) {
      setEmailError("Email is required")
      return
    }
    
    if (!validateEmail(email)) {
      setEmailError("Please enter a valid email address")
      return
    }

    setEmailError("")
    inviteMutation.mutate(email.trim().toLowerCase())
  }

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value)
    if (emailError) {
      setEmailError("")
    }
  }

  return (
    <DialogRoot open={open} onOpenChange={(e) => setOpen(e.open)}>
      <Button
        onClick={() => setOpen(true)}
        variant="outline"
        size="sm"
        colorScheme="blue"
      >
        <FiUserPlus />
        Invite Client
      </Button>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>Invite Client to Project</DialogTitle>
        </DialogHeader>
        <DialogCloseTrigger />

        <DialogBody>
          <Field 
            label="Client Email" 
            invalid={!!emailError}
            errorText={emailError}
          >
            <Input
              placeholder="client@example.com"
              value={email}
              onChange={handleEmailChange}
              type="email"
              autoComplete="email"
            />
          </Field>
          <Text fontSize="sm" color="fg.muted" mt={2}>
            Enter the client's email address. If they already have an account, they'll be added immediately. 
            If not, they'll get access when they sign up with this email.
          </Text>
        </DialogBody>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button
            colorScheme="blue"
            onClick={handleInvite}
            disabled={!email.trim()}
            loading={inviteMutation.isPending}
          >
            Invite Client
          </Button>
        </DialogFooter>
      </DialogContent>
    </DialogRoot>
  )
}

