function sanitizeFilename(input: string): string {
  return input
    .trim()
    .replace(/[\\/:*?"<>|]+/g, "-")
    .replace(/\s+/g, " ")
    .slice(0, 80)
}

export async function downloadTextAsPdf(params: {
  title: string
  body: string
  subtitle?: string
}) {
  const { jsPDF } = await import("jspdf")
  const { title, body, subtitle } = params
  const doc = new jsPDF({ unit: "pt", format: "a4" })

  const marginX = 48
  const marginTop = 56
  const marginBottom = 48
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const usableWidth = pageWidth - marginX * 2
  const maxY = pageHeight - marginBottom

  let y = marginTop

  const ensureSpace = (height: number) => {
    if (y + height <= maxY) {
      return
    }
    doc.addPage()
    y = marginTop
  }

  doc.setFont("helvetica", "bold")
  doc.setFontSize(16)
  ensureSpace(22)
  doc.text(title || "Generation", marginX, y)
  y += 24

  if (subtitle) {
    doc.setFont("helvetica", "normal")
    doc.setFontSize(10)
    doc.setTextColor(100)
    ensureSpace(14)
    doc.text(subtitle, marginX, y)
    y += 20
    doc.setTextColor(0)
  }

  doc.setFont("helvetica", "normal")
  doc.setFontSize(11)

  const paragraphs = body.split(/\r?\n/)
  for (const paragraph of paragraphs) {
    if (!paragraph.trim()) {
      ensureSpace(12)
      y += 12
      continue
    }

    const lines = doc.splitTextToSize(paragraph, usableWidth) as string[]
    for (const line of lines) {
      ensureSpace(14)
      doc.text(line, marginX, y)
      y += 14
    }
    ensureSpace(6)
    y += 6
  }

  const filenameBase =
    sanitizeFilename(title || "generation-output") || "generation-output"
  doc.save(`${filenameBase}.pdf`)
}
