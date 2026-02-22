import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useEffect, useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import useCustomToast from "@/hooks/useCustomToast"
import { downloadTextAsPdf } from "@/lib/pdf"
import {
  getGeneration,
  listGenerations,
  updateGeneration,
} from "@/lib/templateMvpApi"
import { errorToMessage } from "@/lib/templateVariables"

export const Route = createFileRoute("/_layout/history")({
  component: HistoryPage,
  head: () => ({
    meta: [
      {
        title: "Generations History - FastAPI Template",
      },
    ],
  }),
})

function HistoryPage() {
  const queryClient = useQueryClient()
  const { showErrorToast, showSuccessToast } = useCustomToast()

  const [selectedGenerationId, setSelectedGenerationId] = useState<string>("")
  const [editableOutput, setEditableOutput] = useState("")

  const generationsQuery = useQuery({
    queryKey: ["generations"],
    queryFn: listGenerations,
  })

  useEffect(() => {
    if (selectedGenerationId || !generationsQuery.data?.data.length) {
      return
    }
    setSelectedGenerationId(generationsQuery.data.data[0].id)
  }, [generationsQuery.data, selectedGenerationId])

  const generationDetailQuery = useQuery({
    queryKey: ["generation", selectedGenerationId],
    queryFn: () => getGeneration(selectedGenerationId),
    enabled: Boolean(selectedGenerationId),
  })

  useEffect(() => {
    if (!generationDetailQuery.data) {
      return
    }
    setEditableOutput(generationDetailQuery.data.output_text)
  }, [generationDetailQuery.data])

  const updateMutation = useMutation({
    mutationFn: (payload: { id: string; output_text: string }) =>
      updateGeneration(payload.id, { output_text: payload.output_text }),
  })

  const handleSaveEditedOutput = async () => {
    if (!selectedGenerationId) {
      return
    }

    try {
      const updatedGeneration = await updateMutation.mutateAsync({
        id: selectedGenerationId,
        output_text: editableOutput,
      })
      await queryClient.invalidateQueries({
        queryKey: ["generation", selectedGenerationId],
      })
      await queryClient.invalidateQueries({ queryKey: ["generations"] })

      try {
        await downloadTextAsPdf({
          title: updatedGeneration.title,
          body: updatedGeneration.output_text,
          subtitle: `Saved at ${new Date().toLocaleString()}`,
        })
        showSuccessToast("Generation updated and PDF downloaded")
      } catch {
        showSuccessToast("Generation updated")
        showErrorToast("PDF download failed")
      }
    } catch (error) {
      showErrorToast(errorToMessage(error))
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          Generations History
        </h1>
        <p className="text-muted-foreground">
          Browse saved generations and edit final outputs.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Records</CardTitle>
            <CardDescription>
              {generationsQuery.data?.count || 0} generation(s)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {generationsQuery.isLoading ? (
              <p className="text-sm text-muted-foreground">
                Loading history...
              </p>
            ) : generationsQuery.error ? (
              <p className="text-sm text-destructive">
                {errorToMessage(generationsQuery.error)}
              </p>
            ) : generationsQuery.data &&
              generationsQuery.data.data.length > 0 ? (
              generationsQuery.data.data.map((generation) => (
                <button
                  key={generation.id}
                  type="button"
                  className={`w-full rounded-md border p-3 text-left text-sm transition hover:border-primary ${
                    generation.id === selectedGenerationId
                      ? "border-primary bg-primary/5"
                      : ""
                  }`}
                  onClick={() => setSelectedGenerationId(generation.id)}
                >
                  <p className="font-medium">{generation.title}</p>
                  <p className="text-xs text-muted-foreground">
                    {generation.created_at
                      ? new Date(generation.created_at).toLocaleString()
                      : "-"}
                  </p>
                  <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                    {generation.output_text}
                  </p>
                </button>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">No history yet.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {!selectedGenerationId ? (
              <p className="text-sm text-muted-foreground">
                Select a generation to view details.
              </p>
            ) : generationDetailQuery.isLoading ? (
              <p className="text-sm text-muted-foreground">Loading detail...</p>
            ) : generationDetailQuery.error ? (
              <p className="text-sm text-destructive">
                {errorToMessage(generationDetailQuery.error)}
              </p>
            ) : generationDetailQuery.data ? (
              <>
                <div className="space-y-2">
                  <p className="text-sm font-medium">Input</p>
                  <pre className="whitespace-pre-wrap rounded-md border p-3 text-xs">
                    {generationDetailQuery.data.input_text}
                  </pre>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-medium">Extracted Values</p>
                  <pre className="whitespace-pre-wrap rounded-md border p-3 text-xs">
                    {JSON.stringify(
                      generationDetailQuery.data.extracted_values,
                      null,
                      2,
                    )}
                  </pre>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-medium">Output</p>
                  <textarea
                    className="border-input bg-background min-h-[220px] w-full rounded-md border p-3 text-sm"
                    value={editableOutput}
                    onChange={(event) => setEditableOutput(event.target.value)}
                  />
                  <Button
                    variant="outline"
                    onClick={handleSaveEditedOutput}
                    disabled={updateMutation.isPending}
                  >
                    Save Edited Output & Download PDF
                  </Button>
                </div>
              </>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
