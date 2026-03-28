import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowUpDown, ImageUp, Star, Trash2 } from "lucide-react"
import { useMemo, useState } from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import useCustomToast from "@/hooks/useCustomToast"
import {
  type MediaAsset,
  deleteMediaAsset,
  listMediaAssets,
  updateMediaAsset,
  uploadMediaAsset,
} from "@/lib/media-api"

interface MediaGalleryManagerProps {
  contentType: string
  contentId: string
  title?: string
  description?: string
}

type MediaKind = "cover" | "banner" | "gallery"

interface UploadProgressItem {
  id: string
  kind: MediaKind
  fileName: string
  progress: number
}

function getMediaUrl(fileUrl: string) {
  if (fileUrl.startsWith("http://") || fileUrl.startsWith("https://")) {
    return fileUrl
  }
  const base = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "")
  return `${base}${fileUrl}`
}

export default function MediaGalleryManager({
  contentType,
  contentId,
  title = "Media Gallery",
  description = "Upload and manage cover, banner, and gallery images.",
}: MediaGalleryManagerProps) {
  const [draggedGalleryId, setDraggedGalleryId] = useState<string | null>(null)
  const [uploadProgressItems, setUploadProgressItems] = useState<UploadProgressItem[]>([])
  const [dragActiveKind, setDragActiveKind] = useState<MediaKind | null>(null)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const queryKey = ["media", contentType, contentId]

  const mediaQuery = useQuery({
    queryKey,
    queryFn: () => listMediaAssets({ contentType, contentId }),
  })

  const uploadMutation = useMutation({
    mutationFn: async ({ files, kind }: { files: File[]; kind: MediaKind }) => {
      const normalizedFiles = kind === "gallery" ? files : files.slice(0, 1)

      for (const [index, file] of normalizedFiles.entries()) {
        const uploadId = `${file.name}-${Date.now()}-${index}`
        setUploadProgressItems((prev) => [
          ...prev,
          { id: uploadId, kind, fileName: file.name, progress: 0 },
        ])

        await uploadMediaAsset({
          file,
          contentType,
          contentId,
          kind,
          isPrimary: kind !== "gallery" ? true : false,
          displayOrder: 0,
          onProgress: (percent) => {
            setUploadProgressItems((prev) =>
              prev.map((item) =>
                item.id === uploadId ? { ...item, progress: percent } : item
              )
            )
          },
        })

        setUploadProgressItems((prev) =>
          prev.filter((item) => item.id !== uploadId)
        )
      }
    },
    onSuccess: () => {
      showSuccessToast("Media uploaded successfully")
      queryClient.invalidateQueries({ queryKey })
    },
    onError: (error) => {
      showErrorToast(error instanceof Error ? error.message : "Upload failed")
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (mediaId: string) => deleteMediaAsset(mediaId),
    onSuccess: () => {
      showSuccessToast("Media deleted")
      queryClient.invalidateQueries({ queryKey })
    },
    onError: (error) => {
      showErrorToast(error instanceof Error ? error.message : "Delete failed")
    },
  })

  const reorderMutation = useMutation({
    mutationFn: async (orderedGalleryAssets: MediaAsset[]) => {
      await Promise.all(
        orderedGalleryAssets.map((asset, index) =>
          updateMediaAsset(asset.id, {
            display_order: index,
            kind: "gallery",
          })
        )
      )
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey })
    },
    onError: (error) => {
      showErrorToast(error instanceof Error ? error.message : "Reorder failed")
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ mediaId, payload }: { mediaId: string; payload: { kind?: MediaKind; is_primary?: boolean; display_order?: number } }) =>
      updateMediaAsset(mediaId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey })
    },
    onError: (error) => {
      showErrorToast(error instanceof Error ? error.message : "Update failed")
    },
  })

  const onFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>,
    kind: MediaKind
  ) => {
    const files = event.target.files
    if (!files || files.length === 0) return
    uploadMutation.mutate({ files: Array.from(files), kind })
    event.target.value = ""
  }

  const assets = mediaQuery.data?.data ?? []

  const { coverAsset, bannerAsset, galleryAssets } = useMemo(() => {
    const cover = assets
      .filter((asset) => asset.kind === "cover")
      .sort((a, b) => Number(b.is_primary) - Number(a.is_primary) || a.display_order - b.display_order)[0]

    const banner = assets
      .filter((asset) => asset.kind === "banner")
      .sort((a, b) => Number(b.is_primary) - Number(a.is_primary) || a.display_order - b.display_order)[0]

    const gallery = assets
      .filter((asset) => asset.kind === "gallery")
      .sort((a, b) => a.display_order - b.display_order)

    return {
      coverAsset: cover,
      bannerAsset: banner,
      galleryAssets: gallery,
    }
  }, [assets])

  const handleDropUpload = (kind: MediaKind, event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setDragActiveKind(null)
    const files = Array.from(event.dataTransfer.files || []).filter((file) =>
      file.type.startsWith("image/")
    )
    if (files.length === 0) return
    uploadMutation.mutate({ files, kind })
  }

  const onGalleryDrop = (targetId: string) => {
    if (!draggedGalleryId || draggedGalleryId === targetId) return

    const sourceIndex = galleryAssets.findIndex((item) => item.id === draggedGalleryId)
    const targetIndex = galleryAssets.findIndex((item) => item.id === targetId)
    if (sourceIndex === -1 || targetIndex === -1) return

    const reordered = [...galleryAssets]
    const [moved] = reordered.splice(sourceIndex, 1)
    reordered.splice(targetIndex, 0, moved)

    reorderMutation.mutate(reordered)
    setDraggedGalleryId(null)
  }

  const kindUploads = (kind: MediaKind) =>
    uploadProgressItems.filter((item) => item.kind === kind)

  const renderUploadProgress = (kind: MediaKind) => {
    const uploads = kindUploads(kind)
    if (uploads.length === 0) return null

    return (
      <div className="space-y-2">
        {uploads.map((item) => (
          <div key={item.id} className="space-y-1">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span className="truncate max-w-[220px]">{item.fileName}</span>
              <span>{item.progress}%</span>
            </div>
            <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${item.progress}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {mediaQuery.isLoading ? (
          <p className="text-sm text-muted-foreground">Loading media...</p>
        ) : (
          <div className="space-y-8">
            <section className="space-y-3">
              <div>
                <h4 className="font-semibold">Cover Image</h4>
                <p className="text-xs text-muted-foreground">Single primary hero image for cards and listings.</p>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className="border rounded-lg overflow-hidden bg-muted aspect-[16/9]">
                  {coverAsset ? (
                    <img
                      src={getMediaUrl(coverAsset.file_url)}
                      alt={coverAsset.alt_text || coverAsset.original_filename}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div className="h-full w-full grid place-content-center text-muted-foreground text-sm">No cover image</div>
                  )}
                </div>
                <div className="space-y-2">
                  {/* biome-ignore lint/a11y/noStaticElementInteractions: dropzone needs drag events */}
                  <div
                    className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
                      dragActiveKind === "cover" ? "border-primary bg-primary/5" : "border-border"
                    }`}
                    onDragOver={(e) => {
                      e.preventDefault()
                      setDragActiveKind("cover")
                    }}
                    onDragLeave={() => setDragActiveKind(null)}
                    onDrop={(e) => handleDropUpload("cover", e)}
                  >
                    <ImageUp className="mx-auto mb-2 h-5 w-5 text-muted-foreground" />
                    <p className="text-sm">Drag and drop cover image here</p>
                    <p className="text-xs text-muted-foreground">or choose a file below</p>
                  </div>
                  <Input type="file" accept="image/*" onChange={(e) => onFileChange(e, "cover")} />
                  {coverAsset ? (
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          updateMutation.mutate({
                            mediaId: coverAsset.id,
                            payload: { kind: "gallery", is_primary: false },
                          })
                        }
                      >
                        Move to Gallery
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => deleteMutation.mutate(coverAsset.id)}
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </Button>
                    </div>
                  ) : null}
                  {renderUploadProgress("cover")}
                </div>
              </div>
            </section>

            <Separator />

            <section className="space-y-3">
              <div>
                <h4 className="font-semibold">Banner Image</h4>
                <p className="text-xs text-muted-foreground">Single wide banner image for detail headers.</p>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className="border rounded-lg overflow-hidden bg-muted aspect-[21/9]">
                  {bannerAsset ? (
                    <img
                      src={getMediaUrl(bannerAsset.file_url)}
                      alt={bannerAsset.alt_text || bannerAsset.original_filename}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div className="h-full w-full grid place-content-center text-muted-foreground text-sm">No banner image</div>
                  )}
                </div>
                <div className="space-y-2">
                  {/* biome-ignore lint/a11y/noStaticElementInteractions: dropzone needs drag events */}
                  <div
                    className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
                      dragActiveKind === "banner" ? "border-primary bg-primary/5" : "border-border"
                    }`}
                    onDragOver={(e) => {
                      e.preventDefault()
                      setDragActiveKind("banner")
                    }}
                    onDragLeave={() => setDragActiveKind(null)}
                    onDrop={(e) => handleDropUpload("banner", e)}
                  >
                    <ImageUp className="mx-auto mb-2 h-5 w-5 text-muted-foreground" />
                    <p className="text-sm">Drag and drop banner image here</p>
                    <p className="text-xs text-muted-foreground">or choose a file below</p>
                  </div>
                  <Input type="file" accept="image/*" onChange={(e) => onFileChange(e, "banner")} />
                  {bannerAsset ? (
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          updateMutation.mutate({
                            mediaId: bannerAsset.id,
                            payload: { kind: "gallery", is_primary: false },
                          })
                        }
                      >
                        Move to Gallery
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => deleteMutation.mutate(bannerAsset.id)}
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </Button>
                    </div>
                  ) : null}
                  {renderUploadProgress("banner")}
                </div>
              </div>
            </section>

            <Separator />

            <section className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-semibold">Gallery</h4>
                  <p className="text-xs text-muted-foreground">Drag items to reorder. Order is persisted automatically.</p>
                </div>
                <Badge variant="outline" className="gap-1">
                  <ArrowUpDown className="h-3 w-3" />
                  Drag to reorder
                </Badge>
              </div>

              {/* biome-ignore lint/a11y/noStaticElementInteractions: dropzone needs drag events */}
              <div
                className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
                  dragActiveKind === "gallery" ? "border-primary bg-primary/5" : "border-border"
                }`}
                onDragOver={(e) => {
                  e.preventDefault()
                  setDragActiveKind("gallery")
                }}
                onDragLeave={() => setDragActiveKind(null)}
                onDrop={(e) => handleDropUpload("gallery", e)}
              >
                <ImageUp className="mx-auto mb-2 h-5 w-5 text-muted-foreground" />
                <p className="text-sm">Drag and drop gallery images here</p>
                <p className="text-xs text-muted-foreground">or choose files below</p>
              </div>
              <Input type="file" accept="image/*" multiple onChange={(e) => onFileChange(e, "gallery")} />
              {renderUploadProgress("gallery")}

              {galleryAssets.length === 0 ? (
                <p className="text-sm text-muted-foreground">No gallery images uploaded yet.</p>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {galleryAssets.map((asset) => {
                    return (
                      <div
                        key={asset.id}
                        className="border rounded-lg p-3 space-y-3 bg-background"
                      >
                        <button
                          type="button"
                          className="w-full text-left space-y-3"
                          draggable
                          onDragStart={() => setDraggedGalleryId(asset.id)}
                          onDragOver={(e) => e.preventDefault()}
                          onDrop={() => onGalleryDrop(asset.id)}
                        >
                          <div className="aspect-[4/3] overflow-hidden rounded-md bg-muted">
                            <img
                              src={getMediaUrl(asset.file_url)}
                              alt={asset.alt_text || asset.original_filename}
                              className="h-full w-full object-cover"
                            />
                          </div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <Badge variant="secondary">#{asset.display_order + 1}</Badge>
                            {asset.is_primary ? <Badge>Primary</Badge> : null}
                          </div>
                        </button>
                        <div className="flex items-center gap-2 flex-wrap">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              updateMutation.mutate({
                                mediaId: asset.id,
                                payload: { kind: "cover", is_primary: true },
                              })
                            }
                          >
                            Set Cover
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              updateMutation.mutate({
                                mediaId: asset.id,
                                payload: { kind: "banner", is_primary: true },
                              })
                            }
                          >
                            Set Banner
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              updateMutation.mutate({
                                mediaId: asset.id,
                                payload: { is_primary: true },
                              })
                            }
                          >
                            <Star className="mr-2 h-4 w-4" />
                            Primary
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => deleteMutation.mutate(asset.id)}
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </Button>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </section>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
