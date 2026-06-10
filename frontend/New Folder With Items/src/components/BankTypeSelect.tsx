import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const VIETNAMESE_BANKS = [
  { value: "vietcombank", label: "Vietcombank (VCB)" },
  { value: "techcombank", label: "Techcombank (TCB)" },
  { value: "acb", label: "ACB (AC Bank)" },
  { value: "bidv", label: "BIDV" },
  { value: "vietinbank", label: "VietinBank" },
  { value: "sacombank", label: "SacomBank" },
  { value: "hdbank", label: "HDBank" },
  { value: "vpbank", label: "VPBank" },
  { value: "maritime", label: "Maritime Bank" },
  { value: "agribank", label: "Agribank" },
  { value: "other", label: "Other Bank" },
]

interface BankTypeSelectorProps {
  value?: string
  onValueChange?: (value: string) => void
}

export function BankTypeSelect({
  value,
  onValueChange,
}: BankTypeSelectorProps) {
  return (
    <div className="space-y-2">
      <label htmlFor="bank-select" className="text-sm font-medium">
        Select your bank
      </label>
      <Select value={value} onValueChange={onValueChange}>
        <SelectTrigger id="bank-select" className="w-full">
          <SelectValue placeholder="Choose a bank..." />
        </SelectTrigger>
        <SelectContent>
          {VIETNAMESE_BANKS.map((bank) => (
            <SelectItem key={bank.value} value={bank.value}>
              {bank.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
