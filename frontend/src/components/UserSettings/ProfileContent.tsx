import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AccountSecurityCard } from "./AccountSecurityCard"
import { DangerZoneCard } from "./DangerZoneCard"
import { PersonalInfoCard } from "./PersonalInfoCard"

export function ProfileContent() {
  return (
    <Tabs defaultValue="personal" className="w-full space-y-6">
      <TabsList className="grid w-full grid-cols-2 sm:w-auto">
        <TabsTrigger value="personal">Personal</TabsTrigger>
        <TabsTrigger value="account">Account</TabsTrigger>
      </TabsList>

      <TabsContent value="personal" className="space-y-6">
        <PersonalInfoCard />
      </TabsContent>

      <TabsContent value="account" className="space-y-6">
        <AccountSecurityCard />
        <DangerZoneCard />
      </TabsContent>
    </Tabs>
  )
}
