import { useQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"

import { LikesService } from "@/client"
import { ArticleRow } from "@/components/Articles/ArticleRow"
import ChangePassword from "@/components/UserSettings/ChangePassword"
import DeleteAccount from "@/components/UserSettings/DeleteAccount"
import UserInformation from "@/components/UserSettings/UserInformation"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/profile")({
  component: Profile,
  beforeLoad: async ({ location }) => {
    if (!isLoggedIn()) {
      throw redirect({ to: "/login", search: { redirect: location.href } })
    }
  },
  head: () => ({
    meta: [
      {
        title: "Profile - FastAPI Template",
      },
    ],
  }),
})

function LikedArticles() {
  const { data, isLoading } = useQuery({
    queryKey: ["liked-articles"],
    queryFn: () => LikesService.readLikedArticles(),
  })

  if (isLoading) {
    return null
  }

  const articles = data?.data ?? []

  if (articles.length === 0) {
    return (
      <p
        data-testid="liked-articles-empty"
        className="py-6 text-sm text-muted-foreground"
      >
        You haven't liked any articles yet.
      </p>
    )
  }

  return (
    <ul data-testid="liked-articles-list" className="divide-y divide-border/40">
      {articles.map((article) => (
        <ArticleRow key={article.id} article={article} />
      ))}
    </ul>
  )
}

function Profile() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Profile</h1>
        <p className="text-muted-foreground">
          Manage your liked articles and account settings
        </p>
      </div>

      <Tabs defaultValue="liked">
        <TabsList>
          <TabsTrigger value="liked">Liked</TabsTrigger>
          <TabsTrigger value="my-profile">My profile</TabsTrigger>
          <TabsTrigger value="password">Password</TabsTrigger>
          <TabsTrigger value="danger-zone">Danger zone</TabsTrigger>
        </TabsList>
        <TabsContent value="liked">
          <LikedArticles />
        </TabsContent>
        <TabsContent value="my-profile">
          <UserInformation />
        </TabsContent>
        <TabsContent value="password">
          <ChangePassword />
        </TabsContent>
        <TabsContent value="danger-zone">
          <DeleteAccount />
        </TabsContent>
      </Tabs>
    </div>
  )
}
