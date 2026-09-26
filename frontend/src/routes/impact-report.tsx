import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import type { ImpactReport } from "@/types/impactReport"

import fieldRenamed from "@/mocks/impact-reports/drift-field-renamed.json"
import typeChanged from "@/mocks/impact-reports/drift-type-changed.json"
import endpointRemoved from "@/mocks/impact-reports/drift-endpoint-removed.json"

export const Route = createFileRoute("/impact-report")({
  component: ImpactReportPage,
  head: () => ({
    meta: [{ title: "Impact Report - ContractGuard" }],
  }),
})

const scenarios: { key: string; label: string; data: ImpactReport }[] = [
  { key: "field-renamed", label: "Field Renamed", data: fieldRenamed as ImpactReport },
  { key: "type-changed", label: "Type Changed", data: typeChanged as ImpactReport },
  { key: "endpoint-removed", label: "Endpoint Removed", data: endpointRemoved as ImpactReport },
]

const severityStyles: Record<ImpactReport["severity"], string> = {
  high: "bg-red-100 text-red-700 hover:bg-red-100",
  medium: "bg-amber-100 text-amber-700 hover:bg-amber-100",
  low: "bg-yellow-50 text-yellow-700 hover:bg-yellow-50",
}

const verifyStyles: Record<ImpactReport["verify_status"], string> = {
  pass: "bg-green-100 text-green-700 hover:bg-green-100",
  fail: "bg-red-100 text-red-700 hover:bg-red-100",
}

function ImpactReportCard({ report }: { report: ImpactReport }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <p className="text-lg font-medium leading-snug">
            {report.summary_plain_english}
          </p>
          <Badge className={severityStyles[report.severity]}>
            {report.severity}
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground">
          {report.method} {report.endpoint} · {report.change_type}
        </p>
      </CardHeader>

      <CardContent className="flex flex-col gap-4">
        <div>
          <p className="text-sm font-semibold mb-1">Affected files</p>
          <ul className="text-sm text-muted-foreground list-disc list-inside">
            {report.affected_files.map((file) => (
              <li key={file}>{file}</li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-sm font-semibold mb-1">
            {report.patch_applied ? "✅ Patch applied" : "❌ Patch not applied"}
          </p>
          <p className="text-sm text-muted-foreground">
            {report.patch_description}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold">Verify:</span>
          <Badge className={verifyStyles[report.verify_status]}>
            {report.verify_status}
          </Badge>
        </div>

        <details className="text-sm">
          <summary className="cursor-pointer font-medium text-muted-foreground">
            View verify log
          </summary>
          <pre className="mt-2 whitespace-pre-wrap rounded bg-muted p-3 text-xs">
            {report.verify_log}
          </pre>
        </details>

        {(report.old_schema_fragment || report.new_schema_fragment) && (
          <details className="text-sm">
            <summary className="cursor-pointer font-medium text-muted-foreground">
              View schema diff
            </summary>
            <div className="mt-2 grid grid-cols-2 gap-3 text-xs">
              <div>
                <p className="font-semibold mb-1">Old</p>
                <pre className="rounded bg-muted p-3">
                  {report.old_schema_fragment
                    ? JSON.stringify(report.old_schema_fragment, null, 2)
                    : "—"}
                </pre>
              </div>
              <div>
                <p className="font-semibold mb-1">New</p>
                <pre className="rounded bg-muted p-3">
                  {report.new_schema_fragment
                    ? JSON.stringify(report.new_schema_fragment, null, 2)
                    : "—"}
                </pre>
              </div>
            </div>
          </details>
        )}
      </CardContent>
    </Card>
  )
}

function ImpactReportPage() {
  const [active, setActive] = useState(scenarios[0].key)

  return (
    <div className="mx-auto max-w-3xl p-6">
      <h1 className="text-2xl font-bold mb-4">ContractGuard — Impact Report</h1>

      <Tabs value={active} onValueChange={setActive}>
        <TabsList>
          {scenarios.map((s) => (
            <TabsTrigger key={s.key} value={s.key}>
              {s.label}
            </TabsTrigger>
          ))}
        </TabsList>

        {scenarios.map((s) => (
          <TabsContent key={s.key} value={s.key} className="mt-4">
            <ImpactReportCard report={s.data} />
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}