import type { ResumeData } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface ResumeConfirmationModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  resumeData: ResumeData | null
  onApply: () => void
  onCancel: () => void
}

interface DataRowProps {
  label: string
  value: string | undefined
}

function DataRow({ label, value }: DataRowProps) {
  if (!value) return null
  return (
    <div className="flex gap-2 text-sm">
      <span className="font-medium text-muted-foreground min-w-[100px]">
        {label}:
      </span>
      <span className="break-all">{value}</span>
    </div>
  )
}

interface DataListRowProps {
  label: string
  items: Array<string> | undefined
}

function DataListRow({ label, items }: DataListRowProps) {
  if (!items || items.length === 0) return null
  return (
    <div className="flex gap-2 text-sm">
      <span className="font-medium text-muted-foreground min-w-[100px]">
        {label}:
      </span>
      <span className="break-all">{items.join(", ")}</span>
    </div>
  )
}

function hasAnyData(data: ResumeData): boolean {
  return !!(
    data.name ||
    data.email ||
    data.phone ||
    data.city ||
    data.state ||
    data.linkedin ||
    (data.skills && data.skills.length > 0) ||
    (data.education && data.education.length > 0) ||
    (data.experience && data.experience.length > 0)
  )
}

export function ResumeConfirmationModal({
  open,
  onOpenChange,
  resumeData,
  onApply,
  onCancel,
}: ResumeConfirmationModalProps) {
  if (!resumeData) return null

  const dataFound = hasAnyData(resumeData)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Dados do Currículo</DialogTitle>
          <DialogDescription>
            {dataFound
              ? "Identificamos alguns dados no seu currículo. Deseja aplicá-los automaticamente ao formulário?"
              : "Não foi possível identificar dados estruturados no currículo enviado."}
          </DialogDescription>
        </DialogHeader>

        {dataFound && (
          <div className="flex flex-col gap-2 py-2">
            <DataRow label="Nome" value={resumeData.name} />
            <DataRow label="Email" value={resumeData.email} />
            <DataRow label="Telefone" value={resumeData.phone} />
            <DataRow label="Cidade" value={resumeData.city} />
            <DataRow label="UF" value={resumeData.state} />
            <DataRow label="LinkedIn" value={resumeData.linkedin} />
            <DataListRow label="Habilidades" items={resumeData.skills} />
            <DataListRow label="Formação" items={resumeData.education} />
            <DataListRow label="Experiência" items={resumeData.experience} />
          </div>
        )}

        <DialogFooter>
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancelar
          </Button>
          {dataFound && (
            <Button type="button" onClick={onApply}>
              Aplicar dados do currículo
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
