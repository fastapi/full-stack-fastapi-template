import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { ArrowRight } from "lucide-react"
import { useState } from "react"
import { FilesService, StoragesService } from "@/client"
import { FileUploadDropzone } from "@/components/FileUploadDropzone"
import { useLoadingSpinner } from "@/components/loading-spinner-provider"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import useCustomToast from "@/hooks/useCustomToast"
import { formatBytes, handleError } from "@/utils"
import { FilesTableContent } from "./files"

export const Route = createFileRoute("/_layout/dashboard")({
  component: Dashboard,
})

function Dashboard() {
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()
  const { showSpinner, hideSpinner } = useLoadingSpinner()
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])

  const { data: storageStat } = useQuery({
    queryKey: ["storageStat"],
    queryFn: () => StoragesService.getMyStorageStat(),
  })

  const uploadMutation = useMutation({
    mutationFn: async (files: File[]) => {
      // Upload all files in parallel using Promise.all; each promise resolves
      // to an UploadResult (ok or error) so we can report partial failures.
      showSpinner(`Uploading ${files.length} file(s)...`)
      try {
        const promises = files.map((file) =>
          FilesService.uploadFileEndpoint({ formData: { file } }),
        )

        const results = await Promise.all(promises)
        console.log("Upload results:", results)
        return results
      } finally {
        hideSpinner()
      }
    },
    onSuccess: () => {
      setSelectedFiles([])
      queryClient.invalidateQueries({ queryKey: ["files"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const handleFilesSelect = (files: File[]) => {
    setSelectedFiles(files)
  }

  const handleUpload = () => {
    if (selectedFiles.length === 0) return
    uploadMutation.mutate(selectedFiles, {
      onSettled: () => {
        hideSpinner()
      },
    })
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 mb-12">
          {/* Upload Section */}
          <div className="lg:col-span-3 space-y-6">
            <Card className="p-8">
              <h2 className="text-2xl font-bold mb-6">
                Convert Your Statement
              </h2>

              <div className="space-y-6">
                {/* File Upload */}
                <div>
                  {/* <label className="text-sm font-medium block mb-3">Upload Statement</label> */}
                  <FileUploadDropzone onFilesSelect={handleFilesSelect} />
                </div>

                {/* Convert Button */}
                <Button
                  onClick={handleUpload}
                  disabled={
                    selectedFiles.length === 0 || uploadMutation.isPending
                  }
                  className="w-full gap-2"
                  size="lg"
                >
                  {uploadMutation.isPending ? (
                    <>Uploading...</>
                  ) : (
                    <>
                      Upload <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </Button>

                {/* Info Box */}
                <div className="bg-primary/5 rounded-lg p-4 border border-primary/10 text-sm text-foreground/70">
                  <p className="font-medium mb-2 text-primary">💡 Pro Tip:</p>
                  <p>
                    Upload multiple statements to process them together. Our
                    system will automatically organize all transactions
                    chronologically.
                  </p>
                </div>
              </div>
            </Card>

            {/* Recent Conversions */}
            <div>
              <h2 className="text-2xl font-bold mb-6">Recent Conversions</h2>
              <Card className="overflow-hidden">
                {/* <FileHistoryTable /> */}
                <FilesTableContent limit={5} />
              </Card>
            </div>
          </div>

          {/* Sidebar Stats */}
          <div className="space-y-6">
            {/* <Card className="p-6 bg-primary/5 border-primary/10">
              <div className="text-center">
                <p className="text-4xl font-bold text-primary mb-2">12</p>
                <p className="text-sm text-foreground/70 mb-4">
                  Files Processed This Month
                </p>
                <div className="w-full bg-primary/20 rounded-full h-2">
                  <div
                    className="bg-primary h-2 rounded-full"
                    style={{ width: "60%" }}
                  />
                </div>
                <p className="text-xs text-foreground/60 mt-2">
                  60% of monthly quota
                </p>
              </div>
            </Card> */}

            <Card className="p-6">
              <h3 className="font-semibold mb-4">Quick Stats</h3>
              <div className="space-y-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-foreground/60">Total Files</span>
                  <span className="font-semibold">
                    {storageStat?.file_count ?? "—"}
                  </span>
                </div>
                <div className="border-t border-border pt-4 flex justify-between">
                  <span className="text-foreground/60">Total Pages</span>
                  <span className="font-semibold">
                    {storageStat?.total_pages?.toLocaleString() ?? "—"}
                  </span>
                </div>
                <div className="border-t border-border pt-4 flex justify-between">
                  <span className="text-foreground/60">Storage Used</span>
                  <span className="font-semibold">
                    {storageStat ? formatBytes(storageStat.total_size) : "—"}
                  </span>
                </div>
                <div className="border-t border-border pt-4 flex justify-between">
                  <span className="text-foreground/60">Total Cost</span>
                  <span className="font-semibold">
                    {storageStat
                      ? `$${storageStat.total_cost.toFixed(2)}`
                      : "—"}
                  </span>
                </div>
                <div className="border-t border-border pt-4 flex justify-between">
                  <span className="text-foreground/60">Balance</span>
                  <span className="font-semibold text-green-600">
                    {storageStat != null
                      ? new Intl.NumberFormat("vi-VN", {
                          style: "currency",
                          currency: "VND",
                          maximumFractionDigits: 0,
                        }).format(storageStat.balance)
                      : "—"}
                  </span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
