export interface FileHistoryItem {
  id: string
  filename: string
  uploadDate: string
  size: string
  status: "pending" | "running" | "done" | "failed"
  bankType: string
}

export interface PricingTier {
  name: string
  price: string
  description: string
  features: string[]
  cta: string
  highlighted?: boolean
}

export const mockFileHistory: FileHistoryItem[] = [
  {
    id: "1",
    filename: "Vietcombank_Statement_May_2024.pdf",
    uploadDate: "2024-05-15",
    size: "2.4 MB",
    status: "done" as const,
    bankType: "Vietcombank",
  },
  {
    id: "2",
    filename: "Techcombank_April_Statement.pdf",
    uploadDate: "2024-04-28",
    size: "1.8 MB",
    status: "done" as const,
    bankType: "Techcombank",
  },
  {
    id: "3",
    filename: "ACB_Statement_June.pdf",
    uploadDate: "2024-06-10",
    size: "3.1 MB",
    status: "running" as const,
    bankType: "ACB",
  },
  {
    id: "4",
    filename: "BIDV_May_Statement.pdf",
    uploadDate: "2024-05-20",
    size: "2.7 MB",
    status: "done" as const,
    bankType: "BIDV",
  },
]

export const pricingTiers: PricingTier[] = [
  {
    name: "Free",
    price: "$0",
    description: "Get started at no cost — no credit card required",
    features: [
      "5 conversions per month",
      "PDF & image bank statements",
      "Basic Excel export",
      "Up to 5 MB file size",
      "Email support",
    ],
    cta: "Get Started Free",
  },
  {
    name: "Pro",
    price: "$4.99",
    description: "For individuals and freelancers who convert regularly",
    features: [
      "100 conversions per month",
      "PDF & image bank statements",
      "Advanced Excel formatting",
      "Up to 50 MB file size",
      "Transaction categorization",
      "Priority email support",
      "Download history (30 days)",
    ],
    cta: "Start Free Trial",
    highlighted: true,
  },
  {
    name: "Business",
    price: "$9.99",
    description: "For teams and accounting firms with high volume needs",
    features: [
      "Unlimited conversions",
      "All file types supported",
      "Custom Excel templates",
      "Up to 100 MB file size",
      "Batch processing",
      "API access",
      "Team management (up to 5 seats)",
      "Priority support & SLA",
      "Download history (unlimited)",
    ],
    cta: "Start Free Trial",
  },
]
