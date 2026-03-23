import { useEffect, useState } from "react"
import { PricingPage } from "@/components/app/PricingPage"
import UserProfile from "@/components/app/UserProfile"
import { WeeklyReportSubscriptionToggle } from "@/components/app/WeeklyReportSubscriptionToggle"
import { type UserBrand, dashboardAPI } from "@/clients/dashboard"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

function NotificationsTab() {
  const [brands, setBrands] = useState<UserBrand[]>([])
  const [selectedBrandId, setSelectedBrandId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dashboardAPI
      .getUserBrands()
      .then((data) => {
        setBrands(data.brands)
        if (data.brands.length > 0) {
          setSelectedBrandId(data.brands[0].brand_id)
        }
      })
      .catch(() => {
        // ignore
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-slate-900 mb-1">Weekly Report</h2>
        <p className="text-sm text-slate-500 mb-4">
          Get a PDF summary of your brand's GEO performance delivered to your inbox.
        </p>

        {loading ? (
          <p className="text-sm text-slate-500">Loading brands...</p>
        ) : brands.length === 0 ? (
          <p className="text-sm text-slate-500">
            No brands found. Create a project with brand settings to configure notifications.
          </p>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-slate-700">Brand</span>
              <Select
                value={selectedBrandId ?? undefined}
                onValueChange={setSelectedBrandId}
              >
                <SelectTrigger className="w-[220px]">
                  <SelectValue placeholder="Select a brand" />
                </SelectTrigger>
                <SelectContent>
                  {brands.map((brand) => (
                    <SelectItem key={brand.brand_id} value={brand.brand_id}>
                      {brand.brand_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedBrandId && (
              <WeeklyReportSubscriptionToggle brandId={selectedBrandId} />
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export function SettingsPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900 mb-6">Settings</h1>
      <Tabs defaultValue="profile">
        <TabsList className="mb-6">
          <TabsTrigger value="profile">My Profile</TabsTrigger>
          <TabsTrigger value="plan">My Plan</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
        </TabsList>
        <TabsContent value="profile">
          <UserProfile />
        </TabsContent>
        <TabsContent value="plan">
          <PricingPage embedded />
        </TabsContent>
        <TabsContent value="notifications">
          <NotificationsTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
