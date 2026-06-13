export type DocStatus = "done" | "proc" | "fail";
export type DocType = "pdf" | "img";

export interface DocRow {
  id: string;
  name: string;
  type: DocType;
  size: string;
  date: string;
  status: DocStatus;
  pages: number;
  progress?: number;
  model?: string | null;
}

/** Mock parse jobs — file names/ids are data, not translatable UI strings. */
export const DOCS: DocRow[] = [
  { id: "DX-2051", name: "invoice_q2_northwind.pdf", type: "pdf", size: "2.4 MB", date: "2026-06-08 14:22", status: "done", pages: 4 },
  { id: "DX-2050", name: "bank_statement_may.pdf", type: "pdf", size: "1.1 MB", date: "2026-06-08 11:05", status: "done", pages: 6 },
  { id: "DX-2049", name: "receipt_scan_0421.jpg", type: "img", size: "880 KB", date: "2026-06-08 09:48", status: "proc", pages: 1, progress: 64 },
  { id: "DX-2048", name: "shipping_manifest.pdf", type: "pdf", size: "3.8 MB", date: "2026-06-07 17:31", status: "done", pages: 12 },
  { id: "DX-2047", name: "handwritten_ledger.png", type: "img", size: "1.6 MB", date: "2026-06-07 16:10", status: "fail", pages: 1 },
  { id: "DX-2046", name: "payroll_export_w21.pdf", type: "pdf", size: "560 KB", date: "2026-06-07 13:02", status: "done", pages: 2 },
  { id: "DX-2045", name: "inventory_count.jpg", type: "img", size: "2.0 MB", date: "2026-06-06 19:55", status: "done", pages: 1 },
  { id: "DX-2044", name: "vendor_terms_acme.pdf", type: "pdf", size: "740 KB", date: "2026-06-06 15:40", status: "done", pages: 3 },
  { id: "DX-2043", name: "expense_report_apr.pdf", type: "pdf", size: "1.3 MB", date: "2026-06-06 10:18", status: "proc", pages: 5, progress: 28 },
  { id: "DX-2042", name: "tax_form_1099.png", type: "img", size: "920 KB", date: "2026-06-05 18:24", status: "done", pages: 1 },
  { id: "DX-2041", name: "balance_sheet_fy25.pdf", type: "pdf", size: "2.9 MB", date: "2026-06-05 14:07", status: "fail", pages: 8 },
  { id: "DX-2040", name: "purchase_orders_batch.pdf", type: "pdf", size: "4.5 MB", date: "2026-06-05 09:33", status: "done", pages: 18 },
];

export interface Member {
  name: string;
  email: string;
  /** translation key under `roles.*` */
  roleKey: "owner" | "admin" | "analyst";
  jobs: number;
  gradient: string;
}

export const MEMBERS: Member[] = [
  { name: "Mara Vance", email: "mara@tabula.io", roleKey: "owner", jobs: 4218, gradient: "linear-gradient(135deg,oklch(0.82 0.14 205),oklch(0.82 0.14 75))" },
  { name: "Devon Park", email: "devon@tabula.io", roleKey: "admin", jobs: 2904, gradient: "linear-gradient(135deg,oklch(0.82 0.14 75),oklch(0.80 0.15 155))" },
  { name: "Lena Ostrow", email: "lena@tabula.io", roleKey: "analyst", jobs: 1877, gradient: "linear-gradient(135deg,oklch(0.80 0.15 155),oklch(0.82 0.14 205))" },
  { name: "Theo Marsh", email: "theo@tabula.io", roleKey: "analyst", jobs: 1102, gradient: "linear-gradient(135deg,oklch(0.82 0.14 205),oklch(0.68 0.17 25))" },
];

export interface Company {
  id: string;
  name: string;
  seats: number;
  /** translation key under `companies.plans.*` */
  planKey: "starter" | "team" | "enterprise";
  docs: number;
  status: DocStatus;
}

export const COMPANIES: Company[] = [
  { id: "CO-1001", name: "Northwind Co.", seats: 24, planKey: "enterprise", docs: 48210, status: "done" },
  { id: "CO-1002", name: "Acme Freight", seats: 8, planKey: "team", docs: 12044, status: "done" },
  { id: "CO-1003", name: "Globex Ltd.", seats: 41, planKey: "enterprise", docs: 91337, status: "done" },
  { id: "CO-1004", name: "Initech LLC", seats: 3, planKey: "starter", docs: 1899, status: "proc" },
  { id: "CO-1005", name: "Soylent Corp", seats: 16, planKey: "team", docs: 27654, status: "done" },
  { id: "CO-1006", name: "Umbrella Sys", seats: 2, planKey: "starter", docs: 442, status: "fail" },
];

/** Deterministic 30-day parse volume for the overview chart. */
export interface VolumePoint {
  day: string;
  parsed: number;
  failed: number;
}

export const VOLUME: VolumePoint[] = Array.from({ length: 30 }, (_, i) => {
  const base = 180 + Math.sin(i / 2.2) * 70 + i * 6;
  const noise = ((i * 73) % 40) - 12;
  const parsed = Math.max(40, Math.round(base + noise));
  const failed = Math.max(1, Math.round(parsed * (0.02 + ((i * 17) % 30) / 1000)));
  const d = new Date(2026, 4, 10);
  d.setDate(d.getDate() + i);
  return { day: `${d.getMonth() + 1}/${d.getDate()}`, parsed, failed };
});
