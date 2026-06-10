import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Plus, Trash } from "lucide-react"
import { useState } from "react"

const SUPPORTED_PROVIDERS = [
  { label: "Google Generative AI", name: "google-genai" },
] as const

import { ApiKeysService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/_layout/api-keys")({
  component: ApiKeysPage,
  head: () => ({
    meta: [
      {
        title: "API Keys - FastAPI Template",
      },
    ],
  }),
})

function AddApiKeyDialog({
  onAdd,
  isPending,
}: {
  onAdd: (payload: { name?: string; key: string }) => void
  isPending: boolean
}) {
  const [open, setOpen] = useState(false)
  const [key, setKey] = useState("")

  const provider = SUPPORTED_PROVIDERS[0]

  const handleSubmit = () => {
    onAdd({ name: provider.name, key })
    setKey("")
    setOpen(false)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-2" />
          Add API Key
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Google Generative AI Key</DialogTitle>
          <DialogDescription>
            We currently only support{" "}
            <span className="font-medium text-foreground">
              Google Generative AI
            </span>{" "}
            API keys. You can get one from{" "}
            <a
              href="https://aistudio.google.com/apikey"
              target="_blank"
              rel="noreferrer"
              className="underline text-primary"
            >
              Google AI Studio
            </a>
            .
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-2">
          <div className="grid gap-1.5">
            <Label htmlFor="key-provider">Provider</Label>
            <Input
              id="key-provider"
              value={provider.label}
              disabled
              className="bg-muted text-muted-foreground"
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor="key-value">Secret key</Label>
            <Input
              id="key-value"
              placeholder="AIza..."
              value={key}
              onChange={(e) => setKey(e.target.value)}
            />
          </div>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button onClick={handleSubmit} disabled={!key || isPending}>
            Save
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function ApiKeysPage() {
  const { user: currentUser } = useAuth()
  const queryClient = useQueryClient()
  const { showErrorToast, showSuccessToast } = useCustomToast()

  const { data } = useQuery({
    queryKey: ["api-keys"],
    queryFn: () => ApiKeysService.listApiKeys(),
    enabled: !!currentUser,
  })

  const createMutation = useMutation({
    mutationFn: (payload: { name?: string; key: string }) =>
      ApiKeysService.createApiKey({ requestBody: payload }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["api-keys"] })
      showSuccessToast("API key saved")
    },
    onError: (err: unknown) =>
      showErrorToast(err instanceof Error ? err.message : "Unknown error"),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => ApiKeysService.deleteApiKey({ apiKeyId: id }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["api-keys"] }),
    onError: (err: unknown) =>
      showErrorToast(err instanceof Error ? err.message : "Unknown error"),
  })

  if (!currentUser) return null

  const keys = data?.data ?? []

  return (
    <div className="max-w-3xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">API Keys</h1>
          <p className="text-muted-foreground">
            Currently only{" "}
            <span className="font-medium text-foreground">
              Google Generative AI
            </span>{" "}
            keys are supported. Keys are stored securely and never exposed.
          </p>
        </div>
        <AddApiKeyDialog
          onAdd={(payload) => createMutation.mutate(payload)}
          isPending={createMutation.isPending}
        />
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Created At</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {keys.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={3}
                className="text-center text-muted-foreground py-8"
              >
                No API keys configured
              </TableCell>
            </TableRow>
          ) : (
            keys.map((k) => (
              <TableRow key={k.id}>
                <TableCell className="font-medium">
                  {k.name || "(unnamed)"}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {k.created_at ? new Date(k.created_at).toLocaleString() : "—"}
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => deleteMutation.mutate(k.id)}
                    disabled={deleteMutation.isPending}
                  >
                    <Trash className="w-4 h-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}

export default ApiKeysPage
