import { Activity, Calendar, Loader2 } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"
import {
  type TimeRange,
  type UserBrand,
  type UserBrandsResponse,
  dashboardAPI,
} from "@/clients/dashboard"
import { BrandAwarenessScore } from "@/components/app/dashboard/components/BrandAwarenessScore"
import { DetailMetricsView } from "@/components/app/dashboard/components/DetailMetricsView"
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function Dashboard() {
  // ============================================================================
  // State Management
  // ============================================================================

  const [brands, setBrands] = useState<UserBrand[]>([])
  const [selectedBrandId, setSelectedBrandId] = useState<string | null>(null)
  const [isLoadingBrands, setIsLoadingBrands] = useState(true)
  const [brandsError, setBrandsError] = useState<string | null>(null)
  const [timeRange, setTimeRange] = useState<TimeRange>("1month")
  const [showCustomDate, setShowCustomDate] = useState(false)
  const [customDateRange, setCustomDateRange] = useState({ start: "", end: "" })
  const [customDateApplied, setCustomDateApplied] = useState<{ start: string; end: string } | null>(null)

  // ============================================================================
  // Data Fetching
  // ============================================================================

  const fetchUserBrands = useCallback(async () => {
    try {
      setIsLoadingBrands(true)
      setBrandsError(null)

      const data: UserBrandsResponse = await dashboardAPI.getUserBrands()
      setBrands(data.brands)

      // Auto-select the first brand if available
      if (data.brands.length > 0 && !selectedBrandId) {
        setSelectedBrandId(data.brands[0].brand_id)
      }

      console.log("[Dashboard] Loaded brands:", data.total_count)
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load brands"
      setBrandsError(errorMessage)
      console.error("[Dashboard] Error loading brands:", err)
    } finally {
      setIsLoadingBrands(false)
    }
  }, [selectedBrandId])

  useEffect(() => {
    fetchUserBrands()
  }, [fetchUserBrands])

  // ============================================================================
  // Event Handlers
  // ============================================================================

  const handleBrandChange = (brandId: string) => {
    setSelectedBrandId(brandId)
    console.log("[Dashboard] Selected brand:", brandId)
  }

  const handleRefresh = async () => {
    try {
      // Clear cache and reload
      dashboardAPI.clearUserBrandsCache()
      await fetchUserBrands()
      toast.success("Data refreshed successfully")
    } catch {
      toast.error("Failed to refresh data")
    }
  }

  const handleCustomDateApply = () => {
    if (customDateRange.start && customDateRange.end) {
      setTimeRange("custom")
      setCustomDateApplied({ start: customDateRange.start, end: customDateRange.end })
    }
  }

  // ============================================================================
  // Get Selected Brand Info
  // ============================================================================

  const selectedBrand = brands.find((b) => b.brand_id === selectedBrandId)

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">
              Brand Performance Dashboard
            </h1>
            <p className="text-slate-600 mt-2">
              Welcome back! Here's what's happening today.
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={handleRefresh}>
              Refresh Data
            </Button>
            <Button>
              <Activity className="mr-2 h-4 w-4" />
              View Analytics
            </Button>
          </div>
        </div>

        {/* Brand Selector */}
        <Card className="shadow-md">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg font-semibold">
              Select Brand to Monitor
            </CardTitle>
            <CardDescription>
              Choose a brand from your projects to view its performance metrics
            </CardDescription>
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
                <p>No brands found. Create a project with brand settings to get started.</p>
              </div>
            ) : (
              <div className="flex items-center gap-4">
                <Select
                  value={selectedBrandId || undefined}
                  onValueChange={handleBrandChange}
                >
                  <SelectTrigger className="w-[350px]">
                    <SelectValue placeholder="Select a brand" />
                  </SelectTrigger>
                  <SelectContent>
                    {brands.map((brand) => (
                      <SelectItem key={brand.brand_id} value={brand.brand_id}>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{brand.brand_name}</span>
                          <span className="text-xs text-slate-400">
                            ({brand.project_name})
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedBrand && (
                  <div className="text-sm text-slate-500">
                    <span className="font-medium">Project:</span>{" "}
                    {selectedBrand.project_name}
                    <span className="mx-2">|</span>
                    <span className="font-medium">Role:</span>{" "}
                    <span className="capitalize">{selectedBrand.user_role}</span>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Main Dashboard Section with Tabs */}
        {selectedBrandId && (
          <div className="w-full mx-auto">
            <Tabs defaultValue="awareness">
              <div className="flex items-center justify-between mb-4">
                <TabsList>
                  <TabsTrigger value="awareness">Awareness</TabsTrigger>
                  <TabsTrigger value="detail-metrics">Detail Metrics</TabsTrigger>
                </TabsList>

                {/* Global Time Range Selection */}
                <div className="flex items-center gap-3">
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
                        className="bg-transparent rounded-none shadow-none px-4 py-2
                          data-[state=active]:bg-transparent data-[state=active]:shadow-none
                          border-b-2 border-transparent data-[state=active]:border-primary"
                      >
                        1M
                      </TabsTrigger>
                      <TabsTrigger
                        value="1quarter"
                        className="bg-transparent rounded-none shadow-none px-4 py-2
                          data-[state=active]:bg-transparent data-[state=active]:shadow-none
                          border-b-2 border-transparent data-[state=active]:border-primary"
                      >
                        1Q
                      </TabsTrigger>
                      <TabsTrigger
                        value="1year"
                        className="bg-transparent rounded-none shadow-none px-4 py-2
                          data-[state=active]:bg-transparent data-[state=active]:shadow-none
                          border-b-2 border-transparent data-[state=active]:border-primary"
                      >
                        1Y
                      </TabsTrigger>
                      <TabsTrigger
                        value="ytd"
                        className="bg-transparent rounded-none shadow-none px-4 py-2
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
                  >
                    <Calendar className="h-4 w-4 mr-2" />
                    Custom Range
                  </Button>
                </div>
              </div>

              {/* Custom Date Range Inputs */}
              {showCustomDate && (
                <div className="flex gap-3 items-center p-4 bg-gray-50 rounded-lg mb-4">
                  <div className="flex-1">
                    <label className="text-sm font-medium text-gray-700 block mb-1">
                      Start Date
                    </label>
                    <input
                      type="date"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={customDateRange.start}
                      onChange={(e) =>
                        setCustomDateRange({ ...customDateRange, start: e.target.value })
                      }
                    />
                  </div>
                  <div className="flex-1">
                    <label className="text-sm font-medium text-gray-700 block mb-1">
                      End Date
                    </label>
                    <input
                      type="date"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={customDateRange.end}
                      onChange={(e) =>
                        setCustomDateRange({ ...customDateRange, end: e.target.value })
                      }
                    />
                  </div>
                  <Button
                    className="self-end"
                    onClick={handleCustomDateApply}
                    type="button"
                  >
                    Apply
                  </Button>
                </div>
              )}

              <TabsContent value="awareness">
                <Card className="shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-2xl font-bold">
                      Brand AI Awareness Score
                      {selectedBrand && (
                        <span className="ml-2 text-lg font-normal text-slate-500">
                          - {selectedBrand.brand_name}
                        </span>
                      )}
                    </CardTitle>
                    <CardDescription>
                      Track and analyze your brand's AI awareness performance
                    </CardDescription>
                    <div className="h-px w-full bg-slate-200 shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1)]" />
                  </CardHeader>
                  <CardContent className="space-y-8">
                    <BrandAwarenessScore
                      brandId={selectedBrandId}
                      timeRange={timeRange}
                      customStartDate={customDateApplied?.start}
                      customEndDate={customDateApplied?.end}
                    />
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="detail-metrics">
                <Card className="shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-2xl font-bold">
                      Brand Visibility &amp; Ranking
                      {selectedBrand && (
                        <span className="ml-2 text-lg font-normal text-slate-500">
                          - {selectedBrand.brand_name}
                        </span>
                      )}
                    </CardTitle>
                    <CardDescription>
                      Track your brand's search visibility rate and ranking trends
                    </CardDescription>
                    <div className="h-px w-full bg-slate-200 shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1)]" />
                  </CardHeader>
                  <CardContent className="space-y-8">
                    <DetailMetricsView
                      brandId={selectedBrandId}
                      timeRange={timeRange}
                      customStartDate={customDateApplied?.start}
                      customEndDate={customDateApplied?.end}
                    />
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        )}

        {/* Empty State when no brand selected */}
        {!isLoadingBrands && !brandsError && brands.length > 0 && !selectedBrandId && (
          <Card className="shadow-lg">
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
