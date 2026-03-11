import { Calendar, Loader2, RefreshCw } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"
import {
  type BrandSegmentsResponse,
  dashboardAPI,
  type TimeRange,
  type UserBrand,
  type UserBrandsResponse,
} from "@/clients/dashboard"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface DashboardPageLayoutProps {
  title: string
  description: string
  /** Override the brand card title. Default: "Select Brand to Monitor" */
  brandCardTitle?: string
  /** Description shown below the card title. Pass empty string to hide. */
  brandCardDescription?: string
  /** Whether to show Project and Role fields. Default: true */
  showProjectRole?: boolean
  /** Extra content rendered inside the brand card after the dropdown row */
  brandCardExtras?: (
    selectedBrand: UserBrand | undefined,
    selectedSegment: string,
  ) => React.ReactNode
  children: (props: {
    selectedBrandId: string
    selectedBrand: UserBrand
    selectedSegment: string
    /** All individual segment names for this brand (excludes the "All Segment" sentinel) */
    segments: string[]
    timeRange: TimeRange
    customStartDate?: string
    customEndDate?: string
    timeRangeControls: React.ReactNode
    customDateInputs: React.ReactNode
  }) => React.ReactNode
}

export function DashboardPageLayout({
  title,
  description,
  brandCardTitle = "Select Brand to Monitor",
  brandCardDescription = "Choose a brand from your projects to view its performance metrics",
  showProjectRole = true,
  brandCardExtras,
  children,
}: DashboardPageLayoutProps) {
  const [brands, setBrands] = useState<UserBrand[]>([])
  const [selectedBrandId, setSelectedBrandId] = useState<string | null>(null)
  const [isLoadingBrands, setIsLoadingBrands] = useState(true)
  const [brandsError, setBrandsError] = useState<string | null>(null)
  const [segments, setSegments] = useState<string[]>([])
  const [selectedSegment, setSelectedSegment] = useState<string>("")
  const [isLoadingSegments, setIsLoadingSegments] = useState(false)
  const [timeRange, setTimeRange] = useState<TimeRange>("1month")
  const [showCustomDate, setShowCustomDate] = useState(false)
  const [customDateRange, setCustomDateRange] = useState({ start: "", end: "" })
  const [customDateApplied, setCustomDateApplied] = useState<{
    start: string
    end: string
  } | null>(null)

  const fetchUserBrands = useCallback(async () => {
    try {
      setIsLoadingBrands(true)
      setBrandsError(null)
      const data: UserBrandsResponse = await dashboardAPI.getUserBrands()
      setBrands(data.brands)
      if (data.brands.length > 0 && !selectedBrandId) {
        setSelectedBrandId(data.brands[0].brand_id)
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load brands"
      setBrandsError(errorMessage)
    } finally {
      setIsLoadingBrands(false)
    }
  }, [selectedBrandId])

  useEffect(() => {
    fetchUserBrands()
  }, [fetchUserBrands])

  useEffect(() => {
    if (!selectedBrandId) return
    setIsLoadingSegments(true)
    setSegments([])
    setSelectedSegment("__all_segments__")
    dashboardAPI
      .getBrandSegments(selectedBrandId)
      .then((data: BrandSegmentsResponse) => {
        setSegments(data.segments)
        // Default to "All Segment" — user can drill into a specific segment
        setSelectedSegment("__all_segments__")
      })
      .catch(() => setSegments([]))
      .finally(() => setIsLoadingSegments(false))
  }, [selectedBrandId])

  const handleBrandChange = (brandId: string) => {
    setSelectedBrandId(brandId)
  }

  const handleRefresh = async () => {
    try {
      dashboardAPI.clearAllCache()
      await fetchUserBrands()
      toast.success("Data refreshed successfully")
    } catch {
      toast.error("Failed to refresh data")
    }
  }

  const handleCustomDateApply = () => {
    if (customDateRange.start && customDateRange.end) {
      setTimeRange("custom")
      setCustomDateApplied({
        start: customDateRange.start,
        end: customDateRange.end,
      })
    }
  }

  const selectedBrand = brands.find((b) => b.brand_id === selectedBrandId)

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-4">
      <div className="space-y-4">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
          <p className="text-sm text-slate-600 mt-1">{description}</p>
        </div>

        {/* Brand Selector */}
        <Card className="rounded-xl ring-1 ring-slate-900/5 shadow-sm">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>
                  <span className="text-sm font-semibold text-slate-900 bg-indigo-50 px-3 py-1 rounded-full">
                    {brandCardTitle}
                  </span>
                </CardTitle>
                {brandCardDescription && (
                  <CardDescription>{brandCardDescription}</CardDescription>
                )}
              </div>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    type="button"
                    onClick={handleRefresh}
                    className="text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-md p-1.5 transition-colors"
                  >
                    <RefreshCw className="h-5 w-5" strokeWidth={2.5} />
                  </button>
                </TooltipTrigger>
                <TooltipContent>Refresh Data</TooltipContent>
              </Tooltip>
            </div>
          </CardHeader>
          <CardContent>
            {isLoadingBrands ? (
              <div className="flex items-center gap-2 text-slate-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Loading brands...</span>
              </div>
            ) : brandsError ? (
              <div className="text-red-500">
                <p>{brandsError}</p>
                <Button
                  variant="link"
                  className="p-0 h-auto text-red-500 underline"
                  onClick={handleRefresh}
                >
                  Try again
                </Button>
              </div>
            ) : brands.length === 0 ? (
              <div className="text-slate-500">
                <p>
                  No brands found. Create a project with brand settings to get
                  started.
                </p>
              </div>
            ) : (
              <div className="flex items-center gap-4 flex-wrap">
                {/* Brand dropdown */}
                <div className="flex items-center gap-1.5">
                  <span className="text-xs text-slate-500 font-medium whitespace-nowrap">
                    Brand
                  </span>
                  <Select
                    value={selectedBrandId || undefined}
                    onValueChange={handleBrandChange}
                  >
                    <SelectTrigger className="w-[180px] !h-8 !py-0 px-2 text-xs [&_svg:last-child]:size-3">
                      <SelectValue placeholder="Select a brand" />
                    </SelectTrigger>
                    <SelectContent className="max-h-40">
                      {brands.map((brand) => (
                        <SelectItem
                          key={brand.brand_id}
                          value={brand.brand_id}
                          className="text-xs !py-1 px-2"
                        >
                          <div className="flex items-center gap-1">
                            <span className="font-medium">
                              {brand.brand_name}
                            </span>
                            <span className="text-slate-400">
                              ({brand.project_name})
                            </span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Segment dropdown */}
                <div className="flex items-center gap-1.5">
                  <span className="text-xs text-slate-500 font-medium whitespace-nowrap">
                    Segment
                  </span>
                  <Select
                    value={selectedSegment}
                    onValueChange={setSelectedSegment}
                    disabled={isLoadingSegments}
                  >
                    <SelectTrigger className="w-[180px] !h-8 !py-0 px-2 text-xs [&_svg:last-child]:size-3">
                      <SelectValue
                        placeholder={
                          isLoadingSegments ? "Loading…" : "All Segment"
                        }
                      />
                    </SelectTrigger>
                    <SelectContent className="max-h-40">
                      <SelectItem
                        value="__all_segments__"
                        className="text-xs !py-1 px-2 font-medium"
                      >
                        All Segment
                      </SelectItem>
                      {segments.map((seg) => (
                        <SelectItem
                          key={seg}
                          value={seg}
                          className="text-xs !py-1 px-2"
                        >
                          {seg}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {showProjectRole && selectedBrand && (
                  <div className="text-xs text-slate-500">
                    <span className="font-medium">Project:</span>{" "}
                    {selectedBrand.project_name}
                    <span className="mx-2">|</span>
                    <span className="font-medium">Role:</span>{" "}
                    <span className="capitalize">
                      {selectedBrand.user_role}
                    </span>
                  </div>
                )}
                {brandCardExtras && (
                  <div className="ml-auto flex items-center gap-2">
                    {brandCardExtras(selectedBrand, selectedSegment)}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Page Content */}
        {selectedBrandId && selectedBrand && (
          <div className="w-full">
            {children({
              selectedBrandId,
              selectedBrand,
              selectedSegment,
              segments,
              timeRange,
              customStartDate: customDateApplied?.start,
              customEndDate: customDateApplied?.end,
              timeRangeControls: (
                <div className="flex items-center gap-2">
                  <Tabs
                    value={showCustomDate ? "custom" : timeRange}
                    onValueChange={(value) => {
                      if (value === "custom") {
                        setShowCustomDate(true)
                      } else {
                        setTimeRange(value as TimeRange)
                        setShowCustomDate(false)
                        setCustomDateApplied(null)
                      }
                    }}
                  >
                    <TabsList className="bg-transparent rounded-none border-b h-auto p-0">
                      <TabsTrigger
                        value="1month"
                        className="bg-transparent rounded-none shadow-none px-3 py-1 text-xs
                          data-[state=active]:bg-transparent data-[state=active]:shadow-none
                          border-b-2 border-transparent data-[state=active]:border-primary"
                      >
                        1M
                      </TabsTrigger>
                      <TabsTrigger
                        value="1quarter"
                        className="bg-transparent rounded-none shadow-none px-3 py-1 text-xs
                          data-[state=active]:bg-transparent data-[state=active]:shadow-none
                          border-b-2 border-transparent data-[state=active]:border-primary"
                      >
                        1Q
                      </TabsTrigger>
                      <TabsTrigger
                        value="1year"
                        className="bg-transparent rounded-none shadow-none px-3 py-1 text-xs
                          data-[state=active]:bg-transparent data-[state=active]:shadow-none
                          border-b-2 border-transparent data-[state=active]:border-primary"
                      >
                        1Y
                      </TabsTrigger>
                      <TabsTrigger
                        value="ytd"
                        className="bg-transparent rounded-none shadow-none px-3 py-1 text-xs
                          data-[state=active]:bg-transparent data-[state=active]:shadow-none
                          border-b-2 border-transparent data-[state=active]:border-primary"
                      >
                        YTD
                      </TabsTrigger>
                    </TabsList>
                  </Tabs>
                  <Button
                    variant={showCustomDate ? "default" : "outline"}
                    onClick={() => setShowCustomDate(!showCustomDate)}
                    size="sm"
                    type="button"
                    className="h-8 text-xs px-3"
                  >
                    <Calendar className="h-3 w-3 mr-1" />
                    Custom
                  </Button>
                </div>
              ),
              customDateInputs: showCustomDate ? (
                <div className="flex gap-3 items-center p-3 bg-slate-50 rounded-lg">
                  <div className="flex-1">
                    <label
                      htmlFor="dashboard-page-start-date"
                      className="text-sm font-medium text-slate-700 block mb-1"
                    >
                      Start Date
                    </label>
                    <input
                      id="dashboard-page-start-date"
                      type="date"
                      className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={customDateRange.start}
                      onChange={(e) =>
                        setCustomDateRange({
                          ...customDateRange,
                          start: e.target.value,
                        })
                      }
                    />
                  </div>
                  <div className="flex-1">
                    <label
                      htmlFor="dashboard-page-end-date"
                      className="text-sm font-medium text-slate-700 block mb-1"
                    >
                      End Date
                    </label>
                    <input
                      id="dashboard-page-end-date"
                      type="date"
                      className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={customDateRange.end}
                      onChange={(e) =>
                        setCustomDateRange({
                          ...customDateRange,
                          end: e.target.value,
                        })
                      }
                    />
                  </div>
                  <Button
                    className="self-end h-8 text-xs px-3"
                    onClick={handleCustomDateApply}
                    type="button"
                  >
                    Apply
                  </Button>
                </div>
              ) : null,
            })}
          </div>
        )}

        {/* Empty State */}
        {!isLoadingBrands &&
          !brandsError &&
          brands.length > 0 &&
          !selectedBrandId && (
            <Card className="rounded-xl ring-1 ring-slate-900/5 shadow-sm">
              <CardContent className="flex flex-col items-center justify-center h-64">
                <p className="text-slate-500">
                  Select a brand above to view its performance metrics
                </p>
              </CardContent>
            </Card>
          )}
      </div>
    </div>
  )
}
