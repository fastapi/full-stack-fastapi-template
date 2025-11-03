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
import { Input } from "@chakra-ui/react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { UsersService, ProjectsService } from "@/client"
import { FiUserPlus } from "react-icons/fi"
import useCustomToast from "@/hooks/useCustomToast"

interface InviteClientProps {
  projectId: string
}

export function InviteClient({ projectId }: InviteClientProps) {
  const [open, setOpen] = useState(false)
  const [selectedUserId, setSelectedUserId] = useState<string>("")
  const [searchEmail, setSearchEmail] = useState("")
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  // Fetch client users
  const { data: usersData } = useQuery({
    queryKey: ["clients"],
    queryFn: async () => {
      const baseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, '')
      const response = await fetch(
        `${baseUrl}/api/v1/users/clients?skip=0&limit=100`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      )
      if (!response.ok) {
        throw new Error("Failed to fetch clients")
      }
      return response.json()
    },
    enabled: open,
  })

  const clientUsers = usersData?.data || []

  // Filter by search
  const filteredClients = clientUsers.filter(
    (user) =>
      user.email.toLowerCase().includes(searchEmail.toLowerCase()) ||
      user.full_name?.toLowerCase().includes(searchEmail.toLowerCase())
  )

  const inviteMutation = useMutation({
    mutationFn: async (userId: string) => {
      const baseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, '')
      const url = `${baseUrl}/api/v1/projects/${projectId}/access?user_id=${userId}&role=viewer&can_comment=true&can_download=true`
      const response = await fetch(url, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      })
      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.detail || "Failed to invite client")
      }
      return response.json()
    },
    onSuccess: () => {
      showSuccessToast("Client invited successfully")
      queryClient.invalidateQueries({ queryKey: ["projectAccess", projectId] })
      setOpen(false)
      setSelectedUserId("")
      setSearchEmail("")
    },
    onError: (error: any) => {
      const message = error?.body?.detail || error?.message || "Failed to invite client"
      showErrorToast(message)
    },
  })

  const handleInvite = () => {
    if (selectedUserId) {
      inviteMutation.mutate(selectedUserId)
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
          <Field label="Search for client">
            <Input
              placeholder="Search by email or name..."
              value={searchEmail}
              onChange={(e) => setSearchEmail(e.target.value)}
              mb={4}
            />
          </Field>

          <div style={{ maxHeight: "300px", overflowY: "auto" }}>
            {filteredClients.length === 0 ? (
              <p style={{ color: "gray", textAlign: "center", padding: "20px" }}>
                No clients found
              </p>
            ) : (
              filteredClients.map((user) => (
                <div
                  key={user.id}
                  onClick={() => setSelectedUserId(user.id)}
                  style={{
                    padding: "12px",
                    border: "1px solid #e2e8f0",
                    borderRadius: "8px",
                    marginBottom: "8px",
                    cursor: "pointer",
                    backgroundColor:
                      selectedUserId === user.id ? "#ebf8ff" : "transparent",
                    transition: "all 0.2s",
                  }}
                  onMouseEnter={(e) => {
                    if (selectedUserId !== user.id) {
                      e.currentTarget.style.backgroundColor = "#f7fafc"
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedUserId !== user.id) {
                      e.currentTarget.style.backgroundColor = "transparent"
                    }
                  }}
                >
                  <div style={{ fontWeight: "500" }}>
                    {user.full_name || "No name"}
                  </div>
                  <div style={{ fontSize: "14px", color: "#718096" }}>
                    {user.email}
                  </div>
                </div>
              ))
            )}
          </div>
        </DialogBody>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button
            colorScheme="blue"
            onClick={handleInvite}
            disabled={!selectedUserId}
            loading={inviteMutation.isPending}
          >
            Invite Client
          </Button>
        </DialogFooter>
      </DialogContent>
    </DialogRoot>
  )
}

