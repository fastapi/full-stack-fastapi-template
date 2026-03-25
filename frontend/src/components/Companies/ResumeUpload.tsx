import { useMutation } from "@tanstack/react-query"
import { FileText, Loader2, Upload } from "lucide-react"
import { useRef, useState } from "react"

import { CompaniesService, type ResumeData } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

interface ResumeUploadProps {
  onResumeDataParsed: (data: ResumeData) => void
}

export function ResumeUpload({ onResumeDataParsed }: ResumeUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [fileName, setFileName] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: (file: File) =>
      CompaniesService.parseResume({ formData: { file } }),
    onSuccess: (data) => {
      setError(null)
      onResumeDataParsed(data)
    },
    onError: (err: unknown) => {
      const message =
        err instanceof Error
          ? err.message
          : "Não foi possível ler o currículo enviado. Verifique o formato do arquivo e tente novamente."
      setError(message)
      console.error("Erro ao processar currículo:", err)
    },
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const extension = file.name.split(".").pop()?.toLowerCase()
    if (extension !== "pdf" && extension !== "docx") {
      setError(
        "Formato de arquivo não suportado. Envie um arquivo PDF ou DOCX.",
      )
      setFileName(null)
      return
    }

    setFileName(file.name)
    setError(null)
    mutation.mutate(file)
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Upload de Currículo
        </CardTitle>
        <CardDescription>
          Envie seu currículo para tentar preencher automaticamente os campos
          obrigatórios do cadastro.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-3">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileChange}
              className="hidden"
            />
            <Button
              type="button"
              variant="outline"
              onClick={handleClick}
              disabled={mutation.isPending}
            >
              {mutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Upload className="mr-2 h-4 w-4" />
              )}
              {mutation.isPending ? "Processando..." : "Selecionar arquivo"}
            </Button>
            {fileName && !mutation.isPending && (
              <span className="text-sm text-muted-foreground">{fileName}</span>
            )}
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <p className="text-xs text-muted-foreground">
            Formatos aceitos: PDF, DOCX
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
