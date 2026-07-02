import { Search, X } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { useFilters } from "@/context/filters"
import { cn } from "@/lib/utils"

const DATE_OPTIONS = [
  { value: "3d", label: "Last 3 days" },
  { value: "1w", label: "Last week" },
  { value: "1m", label: "Last month" },
]

const SORT_OPTIONS = [
  { value: "score-desc", label: "Score" },
  { value: "published_at-desc", label: "Date" },
  { value: "likes-desc", label: "Popular" },
]

const CATEGORY_OPTIONS = [
  { value: "", label: "All" },
  { value: "models", label: "Models" },
  { value: "dev", label: "Dev" },
  { value: "research", label: "Research" },
]

const KIND_OPTIONS = [
  { value: "", label: "All" },
  { value: "repo", label: "Repo" },
  { value: "paper", label: "Paper" },
  { value: "model", label: "Model" },
  { value: "blog", label: "Blog" },
  { value: "product", label: "Product" },
  { value: "announcement", label: "Announcement" },
]

function FilterGroup({
  label,
  options,
  value,
  onChange,
}: {
  label: string
  options: { value: string; label: string }[]
  value: string
  onChange: (v: string) => void
}) {
  return (
    <div className="space-y-0.5">
      <p className="px-2 pb-0.5 text-[10px] uppercase tracking-wider text-muted-foreground/70">
        {label}
      </p>
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          onClick={() => onChange(o.value)}
          className={cn(
            "flex shrink-0 items-center gap-2.5 rounded-sm px-2 py-[3px] text-xs transition-colors whitespace-nowrap",
            o.value === value
              ? "text-foreground"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          <span
            className={cn(
              "h-[5px] w-[5px] shrink-0 rounded-full transition-colors",
              o.value === value
                ? "bg-foreground"
                : "border border-muted-foreground/40",
            )}
          />
          {o.label}
        </button>
      ))}
    </div>
  )
}

export function SidebarFilters() {
  const { filters, setFilter } = useFilters()
  const [localSearch, setLocalSearch] = useState(filters.search)
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(null)

  function handleSearchChange(v: string) {
    setLocalSearch(v)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => setFilter("search", v), 300)
  }

  function handleSearchClear() {
    if (debounceRef.current) clearTimeout(debounceRef.current)
    setLocalSearch("")
    setFilter("search", "")
  }

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [])

  return (
    <div className="flex flex-col gap-4">
      <div className="relative flex items-center rounded-sm border bg-background px-2">
        <Search className="h-3 w-3 shrink-0 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search…"
          value={localSearch}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="w-full bg-transparent py-1.5 pl-2 text-xs outline-none placeholder:text-muted-foreground"
        />
        {localSearch && (
          <button
            type="button"
            onClick={handleSearchClear}
            className="flex h-4 w-4 shrink-0 items-center justify-center text-muted-foreground hover:text-foreground"
          >
            <X className="h-3 w-3" />
          </button>
        )}
      </div>

      <FilterGroup
        label="Published"
        options={DATE_OPTIONS}
        value={filters.dateRange}
        onChange={(v) => setFilter("dateRange", v)}
      />
      <FilterGroup
        label="Sort by"
        options={SORT_OPTIONS}
        value={filters.sort}
        onChange={(v) => setFilter("sort", v)}
      />
      <FilterGroup
        label="Category"
        options={CATEGORY_OPTIONS}
        value={filters.category}
        onChange={(v) => setFilter("category", v)}
      />
      <FilterGroup
        label="Kind"
        options={KIND_OPTIONS}
        value={filters.kind}
        onChange={(v) => setFilter("kind", v)}
      />
    </div>
  )
}
